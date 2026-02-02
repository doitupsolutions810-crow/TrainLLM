# Detailed Testing Approach: chatbot_memory_core.py

## Component Overview

[`chatbot_memory_core.py`](../TrainLLM/chatbot_memory_core.py) is a Python module that bridges chat interactions with the simulation:
- Maps chat interactions to simulation events
- Uses Universe/Civilization state as LLM context
- Implements 'Memory Crystallization' via Myths
- Creates civilizations for new users
- Updates civilization resources based on interactions
- Retrieves memory context for LLM queries

## Testing Challenges

1. **External Dependencies**: Depends on `full_cyclekernel_buildA_FH_complete` module
2. **Global State**: Accesses global `universes` and `kernel` objects
3. **Side Effects**: Modifies civilization state and kernel audit logs
4. **Date/Time**: Uses `datetime.now()` which varies between test runs
5. **Complex Data Structures**: Nested dictionaries for civilizations, factions, myths
6. **Missing Dependencies**: May not have all required modules available

## Testing Strategy

### Testing Approach

We'll use `pytest` with `unittest.mock` to:
- Mock the `full_cyclekernel_buildA_FH_complete` module
- Create mock kernel and universe objects
- Control datetime for deterministic tests
- Isolate tests from global state
- Test all public methods of `ChatMemoryBridge`

### Test File Structure

```
TrainLLM/tests/
├── __init__.py
├── conftest.py                      # Shared fixtures
└── test_chatbot_memory_core.py        # ChatMemoryBridge tests
```

## Shared Fixtures (conftest.py)

```python
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add TrainLLM to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_kernel():
    """Create a mock CycleKernel"""
    kernel = Mock()
    kernel.audit_logs = []
    return kernel

@pytest.fixture
def mock_universe():
    """Create a mock Universe"""
    universe = Mock()
    universe.civilizations = {}
    universe.factions = {}
    universe.myths = {}
    return universe

@pytest.fixture
def mock_civ_template():
    """Mock civ_template function"""
    def create_civ(cid):
        return {
            "id": cid,
            "age": 0,
            "alive": True,
            "resources": {
                "attention": 100,
                "compute": 100
            },
            "belief": {
                "truth": 0.7,
                "deception": 0.3
            },
            "observer_weight": 0.5,
            "faction": None,
            "myth_influence": 0.0
        }
    return create_civ

@pytest.fixture
def sample_civilization():
    """Create a sample civilization"""
    return {
        "id": "test_civ",
        "age": 0,
        "alive": True,
        "resources": {
            "attention": 100,
            "compute": 100
        },
        "belief": {
            "truth": 0.7,
            "deception": 0.3
        },
        "observer_weight": 0.5,
        "faction": "faction_A",
        "myth_influence": 0.0
    }

@pytest.fixture
def sample_faction():
    """Create a sample faction"""
    return {
        "id": "faction_A",
        "name": "Faction A",
        "members": [],
        "belief_avg": {
            "truth": 0.5,
            "deception": 0.5
        },
        "compute_pool": 0.0,
        "coalitions": [],
        "reputation": 0.5
    }

@pytest.fixture
def sample_myth():
    """Create a sample myth"""
    return {
        "id": "myth_1",
        "faction": "faction_A",
        "epoch": 1,
        "strength": 0.8,
        "believers": 5
    }

@pytest.fixture
def frozen_datetime():
    """Provide frozen datetime for deterministic tests"""
    with patch('chatbot_memory_core.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 18, 10, 0, 0)
        yield mock_datetime
```

## Detailed Test Cases

### Test Suite 1: ChatMemoryBridge Initialization

#### Test 1.1: __init__ initializes with kernel and universes

```python
import pytest
from unittest.mock import Mock, patch

def test_chatmemorybridge_initialization(mock_kernel, mock_universe):
    """Test that ChatMemoryBridge initializes correctly"""
    with patch('chatbot_memory_core.civ_template') as mock_civ:
        mock_civ.return_value = {"id": "test", "faction": None}

        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        assert bridge.kernel == mock_kernel
        assert bridge.universes == universes
        assert isinstance(bridge.chat_to_civ_map, dict)
        assert len(bridge.chat_to_civ_map) == 0
```

#### Test 1.2: __init__ creates empty chat_to_civ_map

```python
def test_chatmemorybridge_empty_map(mock_kernel, mock_universe):
    """Test that chat_to_civ_map starts empty"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        assert len(bridge.chat_to_civ_map) == 0
```

### Test Suite 2: process_interaction - New User

#### Test 2.1: process_interaction creates civilization for new user

```python
def test_process_interaction_creates_civilization_new_user(
    mock_kernel, mock_universe, mock_civ_template, frozen_datetime
):
    """Test that process_interaction creates civilization for new user"""
    with patch('chatbot_memory_core.civ_template', mock_civ_template):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        civ_id = bridge.process_interaction("user123", "Hello", "Hi there!")

        assert civ_id is not None
        assert civ_id in mock_universe.civilizations
        assert mock_universe.civilizations[civ_id]["id"] == civ_id
```

#### Test 2.2: process_interaction creates civ with correct ID format

```python
def test_process_interaction_civ_id_format(
    mock_kernel, mock_universe, mock_civ_template, frozen_datetime
):
    """Test that civilization ID has correct format"""
    with patch('chatbot_memory_core.civ_template', mock_civ_template):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        civ_id = bridge.process_interaction("user123456", "Hello", "Hi there!")

        assert civ_id.startswith("user_")
        assert len(civ_id) == len("user_") + 6  # user_ + 6 chars
```

#### Test 2.3: process_interaction maps user to civilization

```python
def test_process_interaction_maps_user_to_civ(
    mock_kernel, mock_universe, mock_civ_template, frozen_datetime
):
    """Test that user is mapped to civilization"""
    with patch('chatbot_memory_core.civ_template', mock_civ_template):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        civ_id = bridge.process_interaction("user123", "Hello", "Hi there!")

        assert "user123" in bridge.chat_to_civ_map
        assert bridge.chat_to_civ_map["user123"] == civ_id
```

#### Test 2.4: process_interaction returns None if U1 doesn't exist

```python
def test_process_interaction_no_u1(mock_kernel, frozen_datetime):
    """Test that process_interaction returns None if U1 doesn't exist"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {}  # No U1
        bridge = ChatMemoryBridge(mock_kernel, universes)

        civ_id = bridge.process_interaction("user123", "Hello", "Hi there!")

        assert civ_id is None
```

### Test Suite 3: process_interaction - Resource Updates

#### Test 3.1: process_interaction increases attention

```python
def test_process_interaction_increases_attention(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction increases attention"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_attention = mock_universe.civilizations["user_user1"]["resources"]["attention"]

        bridge.process_interaction("user123", "Hello", "Hi there!")

        final_attention = mock_universe.civilizations["user_user1"]["resources"]["attention"]
        assert final_attention > initial_attention
        assert final_attention == min(100, initial_attention + 5)
```

#### Test 3.2: process_interaction increases compute

```python
def test_process_interaction_increases_compute(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction increases compute"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_compute = mock_universe.civilizations["user_user1"]["resources"]["compute"]

        bridge.process_interaction("user123", "Hello", "Hi there!")

        final_compute = mock_universe.civilizations["user_user1"]["resources"]["compute"]
        assert final_compute > initial_compute
        assert final_compute == initial_compute + 2
```

#### Test 3.3: process_interaction caps attention at 100

```python
def test_process_interaction_caps_attention(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that attention is capped at 100"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        sample_civilization["resources"]["attention"] = 98
        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        bridge.process_interaction("user123", "Hello", "Hi there!")

        final_attention = mock_universe.civilizations["user_user1"]["resources"]["attention"]
        assert final_attention == 100  # Capped at 100
```

### Test Suite 4: process_interaction - Belief Updates

#### Test 4.1: process_interaction increases truth for long messages

```python
def test_process_interaction_increases_truth_long_message(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that long messages increase truth belief"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_truth = mock_universe.civilizations["user_user1"]["belief"]["truth"]

        # Long message (> 50 chars)
        long_message = "A" * 100
        bridge.process_interaction("user123", long_message, "Hi there!")

        final_truth = mock_universe.civilizations["user_user1"]["belief"]["truth"]
        assert final_truth > initial_truth
        assert final_truth == min(1.0, initial_truth + 0.01)
```

#### Test 4.2: process_interaction doesn't increase truth for short messages

```python
def test_process_interaction_no_truth_short_message(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that short messages don't increase truth belief"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_truth = mock_universe.civilizations["user_user1"]["belief"]["truth"]

        # Short message (< 50 chars)
        short_message = "Hi"
        bridge.process_interaction("user123", short_message, "Hi there!")

        final_truth = mock_universe.civilizations["user_user1"]["belief"]["truth"]
        assert final_truth == initial_truth  # No change
```

#### Test 4.3: process_interaction caps truth at 1.0

```python
def test_process_interaction_caps_truth(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that truth is capped at 1.0"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        sample_civilization["belief"]["truth"] = 0.99
        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        # Long message to trigger increase
        long_message = "A" * 100
        bridge.process_interaction("user123", long_message, "Hi there!")

        final_truth = mock_universe.civilizations["user_user1"]["belief"]["truth"]
        assert final_truth == 1.0  # Capped at 1.0
```

### Test Suite 5: process_interaction - Audit Logging

#### Test 5.1: process_interaction logs interaction to kernel

```python
def test_process_interaction_logs_to_kernel(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction logs to kernel audit_logs"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_log_count = len(mock_kernel.audit_logs)

        bridge.process_interaction("user123", "Hello", "Hi there!")

        assert len(mock_kernel.audit_logs) == initial_log_count + 1
```

#### Test 5.2: process_interaction log has correct structure

```python
def test_process_interaction_log_structure(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that log entry has correct structure"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        bridge.process_interaction("user123", "Hello", "Hi there!")

        log_entry = mock_kernel.audit_logs[-1]
        assert log_entry["type"] == "chat_interaction"
        assert log_entry["user_id"] == "user123"
        assert "timestamp" in log_entry
        assert "impact" in log_entry
        assert "civ_id" in log_entry["impact"]
        assert "attention_delta" in log_entry["impact"]
        assert "compute_delta" in log_entry["impact"]
```

#### Test 5.3: process_interaction log has correct deltas

```python
def test_process_interaction_log_deltas(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that log entry has correct delta values"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        bridge.process_interaction("user123", "Hello", "Hi there!")

        log_entry = mock_kernel.audit_logs[-1]
        assert log_entry["impact"]["attention_delta"] == 5
        assert log_entry["impact"]["compute_delta"] == 2
```

### Test Suite 6: process_interaction - Existing User

#### Test 6.1: process_interaction updates existing civilization

```python
def test_process_interaction_updates_existing_civ(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction updates existing civilization"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_attention = mock_universe.civilizations["user_user1"]["resources"]["attention"]

        bridge.process_interaction("user123", "Hello", "Hi there!")

        final_attention = mock_universe.civilizations["user_user1"]["resources"]["attention"]
        assert final_attention > initial_attention
```

#### Test 6.2: process_interaction doesn't create new civ for existing user

```python
def test_process_interaction_no_new_civ_existing_user(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction doesn't create new civ for existing user"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        initial_civ_count = len(mock_universe.civilizations)

        bridge.process_interaction("user123", "Hello", "Hi there!")

        final_civ_count = len(mock_universe.civilizations)
        assert final_civ_count == initial_civ_count  # No new civ created
```

### Test Suite 7: get_context_from_memory - New User

#### Test 7.1: get_context_from_memory returns message for new user

```python
def test_get_context_new_user(mock_kernel, mock_universe):
    """Test that get_context_from_memory returns message for new user"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        context = bridge.get_context_from_memory("nonexistent_user")

        assert context == "No prior memory found."
```

#### Test 7.2: get_context_from_memory handles empty chat_to_civ_map

```python
def test_get_context_empty_map(mock_kernel, mock_universe):
    """Test that get_context_from_memory handles empty map"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)

        context = bridge.get_context_from_memory("any_user")

        assert context == "No prior memory found."
```

### Test Suite 8: get_context_from_memory - Existing User

#### Test 8.1: get_context_from_memory returns user_state

```python
def test_get_context_returns_user_state(
    mock_kernel, mock_universe, sample_civilization
):
    """Test that get_context_from_memory returns user state"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        context = bridge.get_context_from_memory("user123")

        assert "user_state" in context
        assert context["user_state"]["id"] == "user_user1"
```

#### Test 8.2: get_context_from_memory includes related myths

```python
def test_get_context_includes_related_myths(
    mock_kernel, mock_universe, sample_civilization, sample_faction, sample_myth
):
    """Test that get_context_from_memory includes related myths"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        # Set up civilization with faction
        sample_civilization["faction"] = "faction_A"
        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        mock_universe.factions["faction_A"] = sample_faction.copy()
        mock_universe.myths["myth_1"] = sample_myth.copy()

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        context = bridge.get_context_from_memory("user123")

        assert "crystallized_memories" in context
        assert len(context["crystallized_memories"]) == 1
        assert context["crystallized_memories"][0]["id"] == "myth_1"
```

#### Test 8.3: get_context_from_memory filters myths by faction

```python
def test_get_context_filters_myths_by_faction(
    mock_kernel, mock_universe, sample_civilization, sample_faction, sample_myth
):
    """Test that get_context_from_memory filters myths by faction"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        # Set up civilization with faction A
        sample_civilization["faction"] = "faction_A"
        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        mock_universe.factions["faction_A"] = sample_faction.copy()
        mock_universe.factions["faction_B"] = sample_faction.copy()
        mock_universe.factions["faction_B"]["id"] = "faction_B"

        # Add myths for both factions
        mock_universe.myths["myth_A"] = sample_myth.copy()
        mock_universe.myths["myth_A"]["faction"] = "faction_A"
        mock_universe.myths["myth_B"] = sample_myth.copy()
        mock_universe.myths["myth_B"]["faction"] = "faction_B"

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        context = bridge.get_context_from_memory("user123")

        # Should only include myths from faction A
        assert len(context["crystallized_memories"]) == 1
        assert context["crystallized_memories"][0]["faction"] == "faction_A"
```

#### Test 8.4: get_context_from_memory includes universe_vibe

```python
def test_get_context_includes_universe_vibe(
    mock_kernel, mock_universe, sample_civilization
):
    """Test that get_context_from_memory includes universe vibe"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        mock_universe.civilizations["user_user2"] = sample_civilization.copy()
        mock_universe.factions["faction_A"] = {"id": "A", "members": []}
        mock_universe.factions["faction_B"] = {"id": "B", "members": []}

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        context = bridge.get_context_from_memory("user123")

        assert "universe_vibe" in context
        assert "total_civs" in context["universe_vibe"]
        assert "active_factions" in context["universe_vibe"]
        assert context["universe_vibe"]["total_civs"] == 2
        assert context["universe_vibe"]["active_factions"] == 2
```

#### Test 8.5: get_context_from_memory handles missing faction

```python
def test_get_context_handles_missing_faction(
    mock_kernel, mock_universe, sample_civilization
):
    """Test that get_context_from_memory handles missing faction"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        # Civilization without faction
        sample_civilization["faction"] = None
        mock_universe.civilizations["user_user1"] = sample_civilization.copy()

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        context = bridge.get_context_from_memory("user123")

        # Should return empty list for myths
        assert "crystallized_memories" in context
        assert len(context["crystallized_memories"]) == 0
```

### Test Suite 9: Edge Cases

#### Test 9.1: process_interaction handles empty message

```python
def test_process_interaction_empty_message(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction handles empty message"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        # Should not raise exception
        civ_id = bridge.process_interaction("user123", "", "Hi there!")

        assert civ_id is not None
```

#### Test 9.2: process_interaction handles very long message

```python
def test_process_interaction_very_long_message(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction handles very long message"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        # Very long message
        long_message = "A" * 10000

        # Should not raise exception
        civ_id = bridge.process_interaction("user123", long_message, "Hi there!")

        assert civ_id is not None
```

#### Test 9.3: process_interaction handles special characters in message

```python
def test_process_interaction_special_characters(
    mock_kernel, mock_universe, sample_civilization, frozen_datetime
):
    """Test that process_interaction handles special characters"""
    with patch('chatbot_memory_core.civ_template', return_value=sample_civilization):
        from chatbot_memory_core import ChatMemoryBridge

        mock_universe.civilizations["user_user1"] = sample_civilization.copy()
        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "user_user1"

        # Message with special characters
        special_message = "Hello @#$%^&*() World!"

        # Should not raise exception
        civ_id = bridge.process_interaction("user123", special_message, "Hi there!")

        assert civ_id is not None
```

#### Test 9.4: get_context_from_memory handles missing civilization

```python
def test_get_context_missing_civilization(mock_kernel, mock_universe):
    """Test that get_context_from_memory handles missing civilization"""
    with patch('chatbot_memory_core.civ_template'):
        from chatbot_memory_core import ChatMemoryBridge

        universes = {"U1": mock_universe}
        bridge = ChatMemoryBridge(mock_kernel, universes)
        bridge.chat_to_civ_map["user123"] = "nonexistent_civ"

        # Should handle gracefully
        context = bridge.get_context_from_memory("user123")

        # Should return error or handle gracefully
        assert context is not None
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
    --cov=chatbot_memory_core
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### requirements-test.txt

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

## Running Tests

```bash
# Run all tests
cd TrainLLM
pytest tests/test_chatbot_memory_core.py

# Run with coverage
pytest tests/test_chatbot_memory_core.py --cov=chatbot_memory_core --cov-report=html

# Run specific test
pytest tests/test_chatbot_memory_core.py -k "process_interaction_creates_civilization"

# Run only unit tests
pytest tests/test_chatbot_memory_core.py -m unit

# Run excluding slow tests
pytest tests/test_chatbot_memory_core.py -m "not slow"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

1. **Fixtures**: Reusable test setup with `conftest.py`
2. **Isolation**: Each test is independent
3. **Mocking**: External dependencies are mocked
4. **Determinism**: Frozen datetime for reproducible tests
5. **AAA Pattern**: Arrange, Act, Assert structure
6. **Descriptive Names**: Test names clearly describe behavior
7. **Markers**: Categorize tests (unit, integration, slow)
8. **Coverage**: Automated coverage reporting with thresholds
9. **Edge Cases**: Test empty values, very long values, special characters
10. **Error Handling**: Test both success and error paths

## Notes

- The `full_cyclekernel_buildA_FH_complete` module is mocked to avoid dependencies
- Global state (`universes`, `kernel`) is isolated using fixtures
- `datetime.now()` is frozen for deterministic timestamp testing
- Complex nested data structures are tested thoroughly
- Resource updates are verified with exact values
- Belief updates are tested with different message lengths
- Audit logging is verified for structure and content
- Myth filtering is tested with multiple factions
- Edge cases include empty values, very long values, special characters
- Missing data scenarios are tested for graceful handling
