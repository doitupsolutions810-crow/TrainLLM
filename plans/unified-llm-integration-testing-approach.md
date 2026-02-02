# Detailed Testing Approach: unified_llm_integration.py

## Component Overview

[`unified_llm_integration.py`](../unified_llm_integration.py) is a Python module that provides:
- **UnifiedLLMOrchestrator**: Central orchestrator for the entire Anti4 LLM ecosystem
- **LLMIntegrationAPI**: REST API for unified LLM integration
- OpenAI API integration for intelligent analysis
- Cross-component state synchronization
- Background monitoring of all components

## Testing Challenges

1. **External API Dependencies**: OpenAI API calls (costly, rate-limited)
2. **Network Requests**: HTTP requests to component endpoints
3. **Background Threads**: Monitoring thread runs in background
4. **Global State**: Component configurations and unified state
5. **Time Dependencies**: Timestamps, monitoring intervals
6. **Flask App**: Web server with multiple routes

## Testing Strategy

### Mocking Approach

We'll use `pytest` with `unittest.mock` to:
- Mock OpenAI API responses
- Mock HTTP requests to component endpoints
- Mock background monitoring thread
- Control time for deterministic tests
- Isolate Flask app for route testing

### Test File Structure

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures
├── test_orchestrator.py             # UnifiedLLMOrchestrator tests
├── test_orchestrator_monitoring.py   # Monitoring thread tests
├── test_orchestrator_llm.py         # LLM query tests
├── test_orchestrator_actions.py     # Action execution tests
└── test_api.py                      # LLMIntegrationAPI route tests
```

## Shared Fixtures (conftest.py)

```python
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "analysis": "Test analysis",
                        "recommendations": ["Test recommendation"],
                        "actions": [],
                        "generated_docs": "",
                        "risk_assessment": "Low risk"
                    })
                }
            }
        ]
    }

@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch('unified_llm_integration.requests') as mock:
        yield mock

@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    with patch('unified_llm_integration.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "analysis": "Test analysis",
                            "recommendations": ["Test recommendation"],
                            "actions": [],
                            "generated_docs": "",
                            "risk_assessment": "Low risk"
                        })
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def sample_orchestrator():
    """Create a sample UnifiedLLMOrchestrator"""
    from unified_llm_integration import UnifiedLLMOrchestrator

    orchestrator = UnifiedLLMOrchestrator("test-api-key")
    return orchestrator

@pytest.fixture
def sample_api(sample_orchestrator):
    """Create a sample LLMIntegrationAPI"""
    from unified_llm_integration import LLMIntegrationAPI

    api = LLMIntegrationAPI(sample_orchestrator)
    return api
```

## Detailed Test Cases

### Test Suite 1: UnifiedLLMOrchestrator Initialization

#### Test 1.1: __init__ initializes with OpenAI API key

```python
def test_orchestrator_initialization():
    from unified_llm_integration import UnifiedLLMOrchestrator

    orchestrator = UnifiedLLMOrchestrator("test-api-key")

    assert orchestrator.openai_api_key == "test-api-key"
    assert isinstance(orchestrator.components, dict)
    assert 'trainllm' in orchestrator.components
    assert 'ai_agent' in orchestrator.components
    assert 'docs' in orchestrator.components
    assert 'wallaby' in orchestrator.components
    assert isinstance(orchestrator.unified_state, dict)
    assert orchestrator.monitoring_active is False
```

#### Test 1.2: __init__ sets up component configurations

```python
def test_orchestrator_component_configurations():
    from unified_llm_integration import UnifiedLLMOrchestrator

    orchestrator = UnifiedLLMOrchestrator("test-api-key")

    # Check trainllm config
    assert orchestrator.components['trainllm']['status'] == 'offline'
    assert orchestrator.components['trainllm']['port'] == 5000
    assert orchestrator.components['trainllm']['endpoint'] == 'http://localhost:5000'

    # Check ai_agent config
    assert orchestrator.components['ai_agent']['status'] == 'offline'
    assert orchestrator.components['ai_agent']['port'] == 3000
    assert orchestrator.components['ai_agent']['endpoint'] == 'http://localhost:3000'

    # Check docs config
    assert orchestrator.components['docs']['status'] == 'online'
    assert orchestrator.components['docs']['port'] == 8000
    assert orchestrator.components['docs']['endpoint'] == 'http://localhost:8000'

    # Check wallaby config
    assert orchestrator.components['wallaby']['status'] == 'offline'
    assert orchestrator.components['wallaby']['port'] is None
    assert orchestrator.components['wallaby']['endpoint'] is None
```

### Test Suite 2: Monitoring Thread

#### Test 2.1: start_monitoring_thread starts background thread

```python
def test_start_monitoring_thread(sample_orchestrator):
    import threading

    initial_thread_count = threading.active_count()

    sample_orchestrator.start_monitoring_thread()

    assert sample_orchestrator.monitoring_active is True
    assert threading.active_count() > initial_thread_count

    # Clean up
    sample_orchestrator.monitoring_active = False
```

#### Test 2.2: _check_component_health updates online status

```python
def test_check_component_health_online(sample_orchestrator, mock_requests):
    # Mock successful health check
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response

    sample_orchestrator._check_component_health()

    assert sample_orchestrator.components['trainllm']['status'] == 'online'
    assert sample_orchestrator.components['ai_agent']['status'] == 'online'
    assert sample_orchestrator.components['docs']['status'] == 'online'
```

#### Test 2.3: _check_component_health updates offline status on error

```python
def test_check_component_health_offline(sample_orchestrator, mock_requests):
    # Mock failed health check
    mock_requests.get.side_effect = Exception("Connection refused")

    sample_orchestrator._check_component_health()

    assert sample_orchestrator.components['trainllm']['status'] == 'offline'
    assert sample_orchestrator.components['ai_agent']['status'] == 'offline'
```

#### Test 2.4: _check_component_health handles non-200 status

```python
def test_check_component_health_non_200(sample_orchestrator, mock_requests):
    # Mock 500 status
    mock_response = Mock()
    mock_response.status_code = 500
    mock_requests.get.return_value = mock_response

    sample_orchestrator._check_component_health()

    assert sample_orchestrator.components['trainllm']['status'] == 'offline'
```

#### Test 2.5: _sync_unified_state syncs TrainLLM state

```python
def test_sync_unified_state_trainllm(sample_orchestrator, mock_requests):
    # Mock TrainLLM state response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "epoch": 42,
        "universes": {"U1": {"civilizations_alive": 5}}
    }
    mock_requests.get.return_value = mock_response

    # Set trainllm as online
    sample_orchestrator.components['trainllm']['status'] = 'online'

    sample_orchestrator._sync_unified_state()

    assert 'trainllm' in sample_orchestrator.unified_state
    assert sample_orchestrator.unified_state['trainllm']['epoch'] == 42
```

#### Test 2.6: _sync_unified_state handles connection errors

```python
def test_sync_unified_state_error(sample_orchestrator, mock_requests):
    # Mock connection error
    mock_requests.get.side_effect = Exception("Connection refused")

    sample_orchestrator.components['trainllm']['status'] = 'online'

    # Should not raise exception
    sample_orchestrator._sync_unified_state()

    # State should remain unchanged or empty
    assert 'trainllm' not in sample_orchestrator.unified_state
```

### Test Suite 3: LLM Query

#### Test 3.1: query_unified_llm builds correct system prompt

```python
def test_query_unified_llm_system_prompt(sample_orchestrator, mock_openai):
    sample_orchestrator.query_unified_llm("test query")

    # Verify the request was made
    assert mock_openai.called

    # Get the call arguments
    call_args = mock_openai.call_args
    request_data = call_args[1]['json']

    # Check system prompt
    messages = request_data['messages']
    assert messages[0]['role'] == 'system'
    assert 'Unified Anti4 LLM Orchestrator' in messages[0]['content']
    assert 'TrainLLM' in messages[0]['content']
    assert 'v0-ai-agent-for-servers' in messages[0]['content']
```

#### Test 3.2: query_unified_llm sends request to OpenAI API

```python
def test_query_unified_llm_api_call(sample_orchestrator, mock_openai):
    sample_orchestrator.query_unified_llm("test query")

    assert mock_openai.called
    call_args = mock_openai.call_args

    # Check URL
    assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"

    # Check headers
    headers = call_args[1]['headers']
    assert headers['Authorization'] == 'Bearer test-api-key'
    assert headers['Content-Type'] == 'application/json'

    # Check request body
    request_data = call_args[1]['json']
    assert request_data['model'] == 'gpt-4'
    assert request_data['temperature'] == 0.7
    assert request_data['max_tokens'] == 2000
```

#### Test 3.3: query_unified_llm parses JSON response

```python
def test_query_unified_llm_parse_json(sample_orchestrator, mock_openai):
    result = sample_orchestrator.query_unified_llm("test query")

    assert 'analysis' in result
    assert 'recommendations' in result
    assert 'actions' in result
    assert 'generated_docs' in result
    assert 'risk_assessment' in result
    assert result['analysis'] == 'Test analysis'
    assert result['recommendations'] == ['Test recommendation']
```

#### Test 3.4: query_unified_llm handles non-JSON response

```python
def test_query_unified_llm_non_json(sample_orchestrator, mock_openai):
    # Mock non-JSON response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Plain text response"
                }
            }
        ]
    }
    mock_openai.return_value = mock_response

    result = sample_orchestrator.query_unified_llm("test query")

    assert 'analysis' in result
    assert result['analysis'] == 'Plain text response'
    assert result['recommendations'] == []
    assert result['actions'] == []
```

#### Test 3.5: query_unified_llm handles API errors

```python
def test_query_unified_llm_api_error(sample_orchestrator, mock_openai):
    # Mock API error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"
    mock_openai.return_value = mock_response

    result = sample_orchestrator.query_unified_llm("test query")

    assert 'error' in result
    assert '429' in result['error']
```

#### Test 3.6: query_unified_llm handles request failures

```python
def test_query_unified_llm_request_failure(sample_orchestrator, mock_openai):
    # Mock request exception
    mock_openai.side_effect = Exception("Network error")

    result = sample_orchestrator.query_unified_llm("test query")

    assert 'error' in result
    assert 'Network error' in result['error']
```

#### Test 3.7: query_unified_llm includes context in request

```python
def test_query_unified_llm_with_context(sample_orchestrator, mock_openai):
    context = {
        "trainllm": {"epoch": 42},
        "custom_data": {"key": "value"}
    }

    sample_orchestrator.query_unified_llm("test query", context)

    call_args = mock_openai.call_args
    request_data = call_args[1]['json']
    messages = request_data['messages']

    # Check that context is included in user message
    user_message = messages[1]['content']
    assert 'trainllm' in user_message
    assert 'custom_data' in user_message
```

### Test Suite 4: Action Execution

#### Test 4.1: execute_action routes to trainllm handler

```python
def test_execute_action_trainllm(sample_orchestrator, mock_requests):
    action = {
        "type": "query_llm",
        "prompt": "test prompt"
    }

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}
    mock_requests.post.return_value = mock_response

    result = sample_orchestrator.execute_action('trainllm', action)

    assert 'result' in result or 'error' in result
```

#### Test 4.2: execute_action routes to ai_agent handler

```python
def test_execute_action_ai_agent(sample_orchestrator):
    action = {
        "type": "test_action",
        "data": "test"
    }

    result = sample_orchestrator.execute_action('ai_agent', action)

    assert result['status'] == 'executed'
    assert result['component'] == 'ai_agent'
    assert result['action'] == action
```

#### Test 4.3: execute_action routes to docs handler

```python
def test_execute_action_docs(sample_orchestrator):
    action = {
        "type": "generate_docs",
        "topic": "test topic"
    }

    result = sample_orchestrator.execute_action('docs', action)

    assert result['status'] == 'executed'
    assert result['component'] == 'docs'
    assert result['action'] == action
```

#### Test 4.4: execute_action handles unknown component

```python
def test_execute_action_unknown_component(sample_orchestrator):
    action = {"type": "test"}

    result = sample_orchestrator.execute_action('unknown_component', action)

    assert 'error' in result
    assert 'unknown_component' in result['error']
```

#### Test 4.5: _execute_trainllm_action handles query_llm

```python
def test_execute_trainllm_query_llm(sample_orchestrator, mock_requests):
    action = {
        "type": "query_llm",
        "prompt": "test prompt"
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "LLM response"}
    mock_requests.post.return_value = mock_response

    result = sample_orchestrator._execute_trainllm_action(action)

    assert result['result'] == "LLM response"
```

#### Test 4.6: _execute_trainllm_action handles approve_proposal

```python
def test_execute_trainllm_approve_proposal(sample_orchestrator, mock_requests):
    action = {
        "type": "approve_proposal",
        "proposal_id": "test-proposal-123"
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests.post.return_value = mock_response

    result = sample_orchestrator._execute_trainllm_action(action)

    assert result['status'] == 'approved'
```

#### Test 4.7: _execute_trainllm_action handles unknown action

```python
def test_execute_trainllm_unknown_action(sample_orchestrator):
    action = {
        "type": "unknown_action"
    }

    result = sample_orchestrator._execute_trainllm_action(action)

    assert 'error' in result
```

#### Test 4.8: _generate_documentation generates docs via LLM

```python
def test_generate_documentation(sample_orchestrator, mock_openai):
    result = sample_orchestrator._generate_documentation("test topic")

    assert result['status'] == 'generated'
    assert 'content' in result
```

### Test Suite 5: Health Status

#### Test 5.1: get_unified_health_status returns comprehensive status

```python
def test_get_unified_health_status(sample_orchestrator):
    status = sample_orchestrator.get_unified_health_status()

    assert 'timestamp' in status
    assert 'components' in status
    assert 'unified_state' in status
    assert 'overall_health' in status
    assert isinstance(status['components'], dict)
    assert isinstance(status['unified_state'], dict)
```

#### Test 5.2: _calculate_overall_health returns excellent when all online

```python
def test_calculate_overall_health_excellent(sample_orchestrator):
    # Set all components online
    for comp in sample_orchestrator.components.values():
        comp['status'] = 'online'

    health = sample_orchestrator._calculate_overall_health()

    assert health == 'excellent'
```

#### Test 5.3: _calculate_overall_health returns good when 75%+ online

```python
def test_calculate_overall_health_good(sample_orchestrator):
    # Set 3 of 4 components online (75%)
    components = list(sample_orchestrator.components.keys())
    for i, comp in enumerate(components):
        sample_orchestrator.components[comp]['status'] = 'online' if i < 3 else 'offline'

    health = sample_orchestrator._calculate_overall_health()

    assert health == 'good'
```

#### Test 5.4: _calculate_overall_health returns fair when 50%+ online

```python
def test_calculate_overall_health_fair(sample_orchestrator):
    # Set 2 of 4 components online (50%)
    components = list(sample_orchestrator.components.keys())
    for i, comp in enumerate(components):
        sample_orchestrator.components[comp]['status'] = 'online' if i < 2 else 'offline'

    health = sample_orchestrator._calculate_overall_health()

    assert health == 'fair'
```

#### Test 5.5: _calculate_overall_health returns critical when <50% online

```python
def test_calculate_overall_health_critical(sample_orchestrator):
    # Set 1 of 4 components online (25%)
    components = list(sample_orchestrator.components.keys())
    for i, comp in enumerate(components):
        sample_orchestrator.components[comp]['status'] = 'online' if i == 0 else 'offline'

    health = sample_orchestrator._calculate_overall_health()

    assert health == 'critical'
```

### Test Suite 6: LLMIntegrationAPI Routes

#### Test 6.1: GET /health returns unified health status

```python
def test_api_health_route(sample_api):
    with sample_api.app.test_client() as client:
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert 'timestamp' in data
        assert 'components' in data
        assert 'unified_state' in data
        assert 'overall_health' in data
```

#### Test 6.2: POST /query requires query parameter

```python
def test_api_query_missing_parameter(sample_api):
    with sample_api.app.test_client() as client:
        response = client.post('/query',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'query' in data['error']
```

#### Test 6.3: POST /query returns LLM response

```python
def test_api_query_success(sample_api, mock_openai):
    with sample_api.app.test_client() as client:
        response = client.post('/query',
                               json={"query": "test query"},
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert 'analysis' in data
        assert 'recommendations' in data
```

#### Test 6.4: POST /query includes context

```python
def test_api_query_with_context(sample_api, mock_openai):
    with sample_api.app.test_client() as client:
        response = client.post('/query',
                               json={
                                   "query": "test query",
                                   "context": {"custom": "data"}
                               },
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert 'analysis' in data
```

#### Test 6.5: POST /execute requires component and action

```python
def test_api_execute_missing_parameters(sample_api):
    with sample_api.app.test_client() as client:
        # Missing component
        response = client.post('/execute',
                               json={"action": {"type": "test"}},
                               content_type='application/json')
        assert response.status_code == 400

        # Missing action
        response = client.post('/execute',
                               json={"component": "trainllm"},
                               content_type='application/json')
        assert response.status_code == 400
```

#### Test 6.6: POST /execute executes action

```python
def test_api_execute_success(sample_api):
    with sample_api.app.test_client() as client:
        response = client.post('/execute',
                               json={
                                   "component": "ai_agent",
                                   "action": {"type": "test"}
                               },
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'executed'
```

#### Test 6.7: GET /state returns unified state

```python
def test_api_state_route(sample_api):
    with sample_api.app.test_client() as client:
        response = client.get('/state')

        assert response.status_code == 200
        data = response.get_json()
        assert 'unified_state' in data
        assert 'components' in data
```

### Test Suite 7: Integration Tests

#### Test 7.1: Full workflow - monitor, query, execute

```python
def test_full_workflow(sample_orchestrator, mock_requests, mock_openai):
    # 1. Check component health
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response

    sample_orchestrator._check_component_health()

    # 2. Query LLM
    result = sample_orchestrator.query_unified_llm("test query")
    assert 'analysis' in result

    # 3. Execute action
    action_result = sample_orchestrator.execute_action('ai_agent', {"type": "test"})
    assert action_result['status'] == 'executed'
```

#### Test 7.2: Error recovery - component goes offline

```python
def test_error_recovery_component_offline(sample_orchestrator, mock_requests):
    # Initially online
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response

    sample_orchestrator._check_component_health()
    assert sample_orchestrator.components['trainllm']['status'] == 'online'

    # Component goes offline
    mock_requests.get.side_effect = Exception("Connection refused")
    sample_orchestrator._check_component_health()

    assert sample_orchestrator.components['trainllm']['status'] == 'offline'

    # Health should reflect this
    health = sample_orchestrator.get_unified_health_status()
    assert health['overall_health'] in ['good', 'fair', 'critical']
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=unified_llm_integration
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API route tests
```

### requirements-test.txt

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-flask==1.3.0
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_orchestrator.py

# Run with coverage
pytest --cov=unified_llm_integration --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run excluding slow tests
pytest -m "not slow"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

1. **Fixtures**: Reusable test setup with `conftest.py`
2. **Isolation**: Each test is independent
3. **Mocking**: External APIs (OpenAI, HTTP) are mocked
4. **Determinism**: No reliance on real network calls
5. **AAA Pattern**: Arrange, Act, Assert structure
6. **Descriptive Names**: Test names clearly describe behavior
7. **Markers**: Categorize tests (unit, integration, api, slow)
8. **Coverage**: Automated coverage reporting with thresholds
9. **Error Handling**: Test both success and failure paths
10. **Integration Tests**: Test complete workflows

## Notes

- OpenAI API calls are fully mocked to avoid costs and rate limits
- HTTP requests to components are mocked for isolation
- Background monitoring thread is tested but not fully controlled
- Flask app is tested using test client for route testing
- Time-dependent operations use mock time for determinism
- Global state is reset between tests using fixtures
- Error conditions are tested alongside success paths
- Integration tests verify end-to-end workflows
