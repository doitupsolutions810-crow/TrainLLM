import json
import unittest
from unittest.mock import patch, MagicMock
from unified_llm_integration import UnifiedLLMOrchestrator
import requests

class TestLLMTooling(unittest.TestCase):
    def setUp(self):
        self.orchestrator = UnifiedLLMOrchestrator(openai_api_key="mock-key")
        # Ensure it points to the correct port (5001) for this session
        self.orchestrator.components['trainllm']['endpoint'] = 'http://localhost:5001'

    @patch('requests.post')
    def test_reasoning_to_action_cycle(self, mock_post):
        """
        Verify that:
        1. Context is correctly passed to the mock LLM.
        2. LLM response is parsed correctly.
        3. Resulting actions are dispatched to the simulation.
        """
        # 1. Setup Mock LLM Response (Reasoning)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "analysis": "Critical attention level in Universe 1.",
                        "recommendations": ["Scale resources for core civilization"],
                        "actions": [
                            {
                                "component": "trainllm",
                                "action": {
                                    "type": "approve_proposal",
                                    "proposal_id": "test-prop-123"
                                },
                                "priority": "high",
                                "reasoning": "Immediate intervention required"
                            }
                        ]
                    })
                }
            }]
        }
        mock_post.return_value = mock_response

        # 2. Trigger Unified Reasoning
        query = "Analyze simulation state and fix any critical issues."
        result = self.orchestrator.query_unified_llm(query)
        
        print("\n--- LLM Reasoning Output ---")
        print(json.dumps(result, indent=2))

        self.assertIn("analysis", result)
        self.assertEqual(len(result["actions"]), 1)
        self.assertEqual(result["actions"][0]["component"], "trainllm")

        # 3. Execute Dispatched Tool/Action
        # We need to mock the SECOND post call which is the action execution
        action_mock_response = MagicMock()
        action_mock_response.status_code = 200
        action_mock_response.json.return_value = {"status": "ok", "message": "Proposal test-prop-123 processed"}
        
        # Reset mock and setup for sequential calls
        mock_post.reset_mock()
        mock_post.return_value = action_mock_response

        action_result = self.orchestrator.execute_action(
            result["actions"][0]["component"],
            result["actions"][0]["action"]
        )

        print("\n--- Action Execution Result ---")
        print(json.dumps(action_result, indent=2))

        self.assertEqual(action_result["status"], "approved") # As per orchestrator's _execute_trainllm_action logic
        
        # Verify the actual call made to the backend
        mock_post.assert_called_with('http://localhost:5001/approve/test-prop-123')

    @patch('requests.get')
    def test_context_synchronization(self, mock_get):
        """
        Verify that the orchestrator correctly pulls state from the simulation.
        """
        # 1. Mock Simulation State Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "epoch": 999,
            "universes": {"U1": {"population": 1000}}
        }
        mock_get.return_value = mock_response

        # 2. Sync State
        self.orchestrator.components['trainllm']['status'] = 'online'
        self.orchestrator._sync_unified_state()

        # 3. Verify Inner State
        print("\n--- Context Synchronization Result ---")
        print(f"Epoch in Orchestrator State: {self.orchestrator.unified_state['trainllm']['epoch']}")
        
        self.assertEqual(self.orchestrator.unified_state['trainllm']['epoch'], 999)
        self.assertEqual(self.orchestrator.unified_state['trainllm']['universes']['U1']['population'], 1000)

if __name__ == "__main__":
    unittest.main()
