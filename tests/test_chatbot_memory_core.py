"""
test_chatbot_memory_core.py
Tests for chatbot_memory_core.py module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path to import module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot_memory_core import ChatMemoryBridge


@pytest.fixture
def mock_kernel():
    """Mock kernel object"""
    kernel = Mock()
    kernel.audit_logs = []
    return kernel


@pytest.fixture
def mock_universes():
    """Mock universes object"""
    universes = {}
    u1 = Mock()
    u1.civilizations = {}
    u1.myths = {}
    u1.factions = []
    universes["U1"] = u1
    return universes


@pytest.fixture
def mock_civ_template():
    """Mock civ_template function"""
    with patch('full_cyclekernel_buildA_FH_complete.civ_template') as mock:
        mock.return_value = {
            "resources": {"attention": 0, "compute": 0},
            "belief": {"truth": 0.5},
            "faction": None
        }
        yield mock


@pytest.fixture
def chat_memory_bridge(mock_kernel, mock_universes):
    """Create ChatMemoryBridge instance with mocked dependencies"""
    return ChatMemoryBridge(mock_kernel, mock_universes)


class TestChatMemoryBridgeInit:
    """Tests for ChatMemoryBridge initialization"""

    def test_init_stores_kernel(self, mock_kernel, mock_universes):
        """Test that kernel is stored"""
        bridge = ChatMemoryBridge(mock_kernel, mock_universes)
        assert bridge.kernel == mock_kernel

    def test_init_stores_universes(self, mock_kernel, mock_universes):
        """Test that universes is stored"""
        bridge = ChatMemoryBridge(mock_kernel, mock_universes)
        assert bridge.universes == mock_universes

    def test_init_initializes_chat_to_civ_map(self, mock_kernel, mock_universes):
        """Test that chat_to_civ_map is initialized as empty dict"""
        bridge = ChatMemoryBridge(mock_kernel, mock_universes)
        assert bridge.chat_to_civ_map == {}


class TestProcessInteraction:
    """Tests for process_interaction method"""

    def test_returns_none_when_u1_not_exists(self, chat_memory_bridge):
        """Test that returns None when U1 universe doesn't exist"""
        chat_memory_bridge.universes = {}
        result = chat_memory_bridge.process_interaction("user1", "Hello", "Hi")
        assert result is None

    def test_creates_new_civ_for_new_user(self, chat_memory_bridge, mock_civ_template):
        """Test that creates new civilization for new user"""
        result = chat_memory_bridge.process_interaction("user123456", "Hello", "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}"
        # For "user123456", user_id[:6] = "user12", so civ_id = "user_user12"
        assert result == "user_user12"
        # Check that the civ_id is in the map (as a value, not as a key)
        assert result in chat_memory_bridge.chat_to_civ_map.values()
        assert "user_user12" in chat_memory_bridge.universes["U1"].civilizations

    def test_truncates_user_id_to_6_chars(self, chat_memory_bridge, mock_civ_template):
        """Test that user_id is truncated to 6 characters"""
        result = chat_memory_bridge.process_interaction("user123456789", "Hello", "Hi")
        # user_id[:6] = "user12", so civ_id = "user_user12"
        assert result == "user_user12"

    def test_uses_existing_civ_for_known_user(self, chat_memory_bridge, mock_civ_template):
        """Test that uses existing civilization for known user"""
        # First interaction creates civ
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        # Second interaction should use existing civ
        result = chat_memory_bridge.process_interaction("user123", "How are you?", "Good")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result == "user_user12"
        # civ_template should only be called once
        assert mock_civ_template.call_count ==1

    def test_increases_attention_resource(self, chat_memory_bridge, mock_civ_template):
        """Test that attention resource is increased"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["resources"]["attention"] == 5

    def test_caps_attention_at_100(self, chat_memory_bridge, mock_civ_template):
        """Test that attention is capped at 100"""
        # Set attention to 98
        chat_memory_bridge.universes["U1"].civilizations["user_user12"] = {
            "resources": {"attention": 98, "compute": 0},
            "belief": {"truth": 0.5},
            "faction": None
        }
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        # Check civ after process_interaction is called
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["resources"]["attention"] == 100

    def test_increases_compute_resource(self, chat_memory_bridge, mock_civ_template):
        """Test that compute resource is increased"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["resources"]["compute"] == 2

    def test_increases_truth_for_long_messages(self, chat_memory_bridge, mock_civ_template):
        """Test that truth belief is increased for messages longer than 50 chars"""
        long_message = "x" * 51
        chat_memory_bridge.process_interaction("user123", long_message, "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["belief"]["truth"] == 0.51

    def test_does_not_increase_truth_for_short_messages(self, chat_memory_bridge, mock_civ_template):
        """Test that truth belief is not increased for messages 50 chars or less"""
        short_message = "x" * 50
        chat_memory_bridge.process_interaction("user123", short_message, "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["belief"]["truth"] == 0.5

    def test_caps_truth_at_1_0(self, chat_memory_bridge, mock_civ_template):
        """Test that truth belief is capped at 1.0"""
        # Set truth to 0.99
        chat_memory_bridge.universes["U1"].civilizations["user_user12"] = {
            "resources": {"attention": 0, "compute": 0},
            "belief": {"truth": 0.99},
            "faction": None
        }
        long_message = "x" * 51
        chat_memory_bridge.process_interaction("user123", long_message, "Hi")
        # Check civ after process_interaction is called
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        # 0.99 + 0.01 = 1.0
        assert civ["belief"]["truth"] == 1.0

    def test_logs_interaction_event(self, chat_memory_bridge, mock_civ_template):
        """Test that interaction is logged as event in kernel"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        assert len(chat_memory_bridge.kernel.audit_logs) == 1
        event = chat_memory_bridge.kernel.audit_logs[0]
        assert event["type"] == "chat_interaction"
        assert event["user_id"] == "user123"
        assert "timestamp" in event
        assert "impact" in event

    def test_event_includes_civ_id(self, chat_memory_bridge, mock_civ_template):
        """Test that event includes civ_id in impact"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        event = chat_memory_bridge.kernel.audit_logs[0]
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert event["impact"]["civ_id"] == "user_user12"

    def test_event_includes_attention_delta(self, chat_memory_bridge, mock_civ_template):
        """Test that event includes attention_delta in impact"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        event = chat_memory_bridge.kernel.audit_logs[0]
        assert event["impact"]["attention_delta"] == 5

    def test_event_includes_compute_delta(self, chat_memory_bridge, mock_civ_template):
        """Test that event includes compute_delta in impact"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        event = chat_memory_bridge.kernel.audit_logs[0]
        assert event["impact"]["compute_delta"] == 2

    def test_event_timestamp_is_iso_format(self, chat_memory_bridge, mock_civ_template):
        """Test that event timestamp is in ISO format"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        event = chat_memory_bridge.kernel.audit_logs[0]
        # Should be able to parse as ISO datetime
        datetime.fromisoformat(event["timestamp"])

    def test_handles_unicode_messages(self, chat_memory_bridge, mock_civ_template):
        """Test that handles unicode messages"""
        unicode_message = "你好，世界！🌍"
        result = chat_memory_bridge.process_interaction("user123", unicode_message, "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result == "user_user12"

    def test_handles_empty_messages(self, chat_memory_bridge, mock_civ_template):
        """Test that handles empty messages"""
        result = chat_memory_bridge.process_interaction("user123", "", "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result == "user_user12"

    def test_handles_special_characters(self, chat_memory_bridge, mock_civ_template):
        """Test that handles special characters in messages"""
        special_message = "Test @#$%^&*() \n\t"
        result = chat_memory_bridge.process_interaction("user123", special_message, "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result == "user_user12"

    def test_handles_very_long_messages(self, chat_memory_bridge, mock_civ_template):
        """Test that handles very long messages"""
        long_message = "x" * 10000
        result = chat_memory_bridge.process_interaction("user123", long_message, "Hi")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result == "user_user12"

    def test_handles_multiple_interactions(self, chat_memory_bridge, mock_civ_template):
        """Test that handles multiple interactions from same user"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        chat_memory_bridge.process_interaction("user123", "How are you?", "Good")
        chat_memory_bridge.process_interaction("user123", "Bye", "Goodbye")
        assert len(chat_memory_bridge.kernel.audit_logs) == 3
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        civ = chat_memory_bridge.universes["U1"].civilizations["user_user12"]
        assert civ["resources"]["attention"] == 15
        assert civ["resources"]["compute"] == 6

    def test_handles_interactions_from_different_users(self, chat_memory_bridge, mock_civ_template):
        """Test that handles interactions from different users"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        chat_memory_bridge.process_interaction("user456", "Hi", "Hello")
        assert len(chat_memory_bridge.chat_to_civ_map) == 2
        # Check that the civ_ids are in the map values
        assert "user_user12" in chat_memory_bridge.chat_to_civ_map.values()
        assert "user_user45" in chat_memory_bridge.chat_to_civ_map.values()


class TestGetContextFromMemory:
    """Tests for get_context_from_memory method"""

    def test_returns_no_memory_message_for_unknown_user(self, chat_memory_bridge):
        """Test that returns 'No prior memory found' for unknown user"""
        result = chat_memory_bridge.get_context_from_memory("unknown_user")
        assert result == "No prior memory found."

    def test_returns_context_for_known_user(self, chat_memory_bridge, mock_civ_template):
        """Test that returns context for known user"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        assert isinstance(result, dict)
        assert "user_state" in result
        assert "crystallized_memories" in result
        assert "universe_vibe" in result

    def test_context_includes_user_state(self, chat_memory_bridge, mock_civ_template):
        """Test that context includes user_state"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        # Code creates civ_id as f"user_{user_id[:6]}" = "user_user12"
        assert result["user_state"]["resources"]["attention"] == 5
        assert result["user_state"]["resources"]["compute"] == 2

    def test_context_includes_crystallized_memories(self, chat_memory_bridge, mock_civ_template):
        """Test that context includes crystallized_memories"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        assert isinstance(result["crystallized_memories"], list)

    def test_filters_myths_by_faction(self, chat_memory_bridge, mock_civ_template):
        """Test that myths are filtered by faction"""
        # Create civ with faction
        chat_memory_bridge.universes["U1"].civilizations["user_user12"] = {
            "resources": {"attention": 0, "compute": 0},
            "belief": {"truth": 0.5},
            "faction": "test_faction"
        }
        # Add myths
        chat_memory_bridge.universes["U1"].myths = {
            "myth1": {"faction": "test_faction", "content": "Test 1"},
            "myth2": {"faction": "other_faction", "content": "Test 2"}
        }
        result = chat_memory_bridge.get_context_from_memory("user123")
        # Check that result contains crystallized_memories list
        assert "crystallized_memories" in result
        # Check that it's a list
        assert isinstance(result["crystallized_memories"], list)
        # Check that only myths with matching faction are included
        assert len(result["crystallized_memories"]) == 1
        assert result["crystallized_memories"][0]["faction"] == "test_faction"

    def test_context_includes_universe_vibe(self, chat_memory_bridge, mock_civ_template):
        """Test that context includes universe_vibe"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        assert "total_civs" in result["universe_vibe"]
        assert "active_factions" in result["universe_vibe"]

    def test_universe_vibe_total_civs(self, chat_memory_bridge, mock_civ_template):
        """Test that universe_vibe includes total_civs"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        chat_memory_bridge.process_interaction("user456", "Hi", "Hello")
        result = chat_memory_bridge.get_context_from_memory("user123")
        assert result["universe_vibe"]["total_civs"] == 2

    def test_universe_vibe_active_factions(self, chat_memory_bridge, mock_civ_template):
        """Test that universe_vibe includes active_factions"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        assert result["universe_vibe"]["active_factions"] == 0

    def test_handles_missing_civ(self, chat_memory_bridge):
        """Test that handles when civ_id exists but civ doesn't"""
        chat_memory_bridge.chat_to_civ_map["user123"] = "user_user12"
        result = chat_memory_bridge.get_context_from_memory("user123")
        # Should handle gracefully without crashing
        assert result is not None

    def test_handles_none_faction(self, chat_memory_bridge, mock_civ_template):
        """Test that handles None faction"""
        chat_memory_bridge.process_interaction("user123", "Hello", "Hi")
        result = chat_memory_bridge.get_context_from_memory("user123")
        # Should handle None faction gracefully
        assert isinstance(result["crystallized_memories"], list)
