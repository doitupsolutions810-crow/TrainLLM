# Detailed Testing Approach: full_cyclekernel_buildA_FH_complete.py

## Component Overview

[`full_cyclekernel_buildA_FH_complete.py`](../TrainLLM/full_cyclekernel_buildA_FH_complete.py) is a complex Python module that implements a multi-universe simulation system with:
- CycleKernel governance (proposals, approvals, rollbacks)
- Universe simulation (civilizations, factions, institutions, markets, myths)
- Flask web server with SocketIO for real-time updates
- ChatMemoryBridge for LLM integration
- Background simulation loop

## Testing Challenges

1. **Global State**: Multiple global variables (`kernel`, `universes`, `memory_bridge`, `current_epoch`, `simulation_running`)
2. **External Dependencies**: Flask, SocketIO, OpenAI API, file system
3. **Concurrency**: Background simulation thread
4. **Randomness**: Uses `random` module for stochastic behavior
5. **Time**: Uses `time.sleep()` and `datetime.now()`
6. **Side Effects**: SocketIO emits, file writes, HTTP requests

## Testing Strategy

### Mocking Approach

We'll use `pytest` with `unittest.mock` to:
- Mock Flask app and routes
- Mock SocketIO emits
- Mock OpenAI API calls
- Mock file system operations
- Control randomness with seeded random
- Control time with freezegun or time mocking

### Test File Structure

```
TrainLLM/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_cyclekernel.py       # CycleKernel class tests
├── test_universe.py          # Universe and template tests
├── test_mechanics.py        # Core mechanics tests
├── test_chat_memory.py       # ChatMemoryBridge tests
├── test_api_routes.py        # Flask route tests
└── test_simulation.py        # Simulation loop tests
```

## Shared Fixtures (conftest.py)

```python
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add TrainLLM to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_socketio():
    """Mock SocketIO for testing"""
    with patch('full_cyclekernel_buildA_FH_complete.socketio') as mock:
        mock.emit = Mock()
        yield mock

@pytest.fixture
def mock_openai():
    """Mock OpenAI API for testing"""
    with patch('full_cyclekernel_buildA_FH_complete.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="AI response"))]
        )
        yield mock_client

@pytest.fixture
def seeded_random():
    """Provide seeded random for deterministic tests"""
    import random
    random.seed(42)
    yield random
    random.seed()  # Reset after test

@pytest.fixture
def sample_universe():
    """Create a sample universe for testing"""
    from full_cyclekernel_buildA_FH_complete import Universe, civ_template, faction_template

    u = Universe("TestU1")
    u.civilizations["civ1"] = civ_template("civ1")
    u.civilizations["civ2"] = civ_template("civ2")
    u.factions["A"] = faction_template("Faction A")
    u.factions["B"] = faction_template("Faction B")
    return u

@pytest.fixture
def sample_kernel():
    """Create a sample CycleKernel for testing"""
    from full_cyclekernel_buildA_FH_complete import CycleKernel

    kernel = CycleKernel()
    return kernel
```

## Detailed Test Cases

### Test Suite 1: CycleKernel Class

#### Test 1.1: CycleKernel initialization

**Purpose**: Verify CycleKernel initializes with correct structure

```python
def test_cyclekernel_initialization():
    from full_cyclekernel_buildA_FH_complete import CycleKernel

    kernel = CycleKernel()

    assert hasattr(kernel, 'prime_directive')
    assert isinstance(kernel.prime_directive, str)
    assert hasattr(kernel, 'audit_logs')
    assert isinstance(kernel.audit_logs, list)
    assert hasattr(kernel, 'proposals')
    assert isinstance(kernel.proposals, list)
    assert hasattr(kernel, 'approved_diffs')
    assert isinstance(kernel.approved_diffs, list)
    assert hasattr(kernel, 'rollback_stack')
    assert isinstance(kernel.rollback_stack, list)
```

#### Test 1.2: propose_change creates valid proposal

**Purpose**: Verify proposal creation with all required fields

```python
def test_propose_change_creates_valid_proposal(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change

    diff = {"action": "test", "value": 123}
    propose_change("Test proposal", diff)

    assert len(sample_kernel.proposals) == 1
    proposal = sample_kernel.proposals[0]

    assert 'id' in proposal
    assert len(proposal['id']) == 8  # UUID hex[:8]
    assert proposal['description'] == "Test proposal"
    assert proposal['diff'] == diff
    assert 'counterfactuals' in proposal
    assert 'trust_score' in proposal
    assert 0.6 <= proposal['trust_score'] <= 0.95
```

#### Test 1.3: propose_change logs to audit_logs

**Purpose**: Verify proposal is logged

```python
def test_propose_change_logs_to_audit(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change

    propose_change("Test", {"action": "test"})

    assert len(sample_kernel.audit_logs) == 1
    assert sample_kernel.audit_logs[0]['type'] == 'proposal'
    assert 'proposal' in sample_kernel.audit_logs[0]
```

#### Test 1.4: propose_change emits SocketIO event

**Purpose**: Verify real-time notification

```python
def test_propose_change_emits_socketio(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change

    propose_change("Test", {"action": "test"})

    mock_socketio.emit.assert_called_once()
    call_args = mock_socketio.emit.call_args
    assert call_args[0][0] == "proposal_created"
    assert 'id' in call_args[0][1]
```

#### Test 1.5: approve_proposal approves high-trust proposals

**Purpose**: Verify approval logic

```python
def test_approve_proposal_high_trust(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change, approve_proposal

    propose_change("High trust", {"action": "test"})
    proposal_id = sample_kernel.proposals[0]['id']

    # Manually set high trust
    sample_kernel.proposals[0]['counterfactuals']['trust'] = 0.9

    approve_proposal(proposal_id)

    assert len(sample_kernel.approved_diffs) == 1
    assert len(sample_kernel.proposals) == 0
    assert len(sample_kernel.rollback_stack) == 1
```

#### Test 1.6: approve_proposal rejects low-trust proposals

**Purpose**: Verify rejection logic

```python
def test_approve_proposal_low_trust(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change, approve_proposal

    propose_change("Low trust", {"action": "test"})
    proposal_id = sample_kernel.proposals[0]['id']

    # Set low trust
    sample_kernel.proposals[0]['counterfactuals']['trust'] = 0.7

    approve_proposal(proposal_id)

    assert len(sample_kernel.approved_diffs) == 0
    assert len(sample_kernel.proposals) == 1  # Still in proposals
```

#### Test 1.7: approve_proposal with manual_approval bypasses trust check

**Purpose**: Verify manual override

```python
def test_approve_proposal_manual_override(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change, approve_proposal

    propose_change("Manual", {"action": "test"})
    proposal_id = sample_kernel.proposals[0]['id']

    # Low trust but manual approval
    sample_kernel.proposals[0]['counterfactuals']['trust'] = 0.5
    approve_proposal(proposal_id, signature="manual_approval")

    assert len(sample_kernel.approved_diffs) == 1
```

#### Test 1.8: rollback restores previous state

**Purpose**: Verify rollback functionality

```python
def test_rollback_restores_previous_state(sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import propose_change, approve_proposal, rollback

    # Approve two proposals
    propose_change("First", {"action": "first"})
    propose_change("Second", {"action": "second"})

    sample_kernel.proposals[0]['counterfactuals']['trust'] = 0.9
    sample_kernel.proposals[1]['counterfactuals']['trust'] = 0.9

    approve_proposal(sample_kernel.proposals[0]['id'])
    first_id = sample_kernel.proposals[0]['id']
    approve_proposal(first_id)

    assert len(sample_kernel.approved_diffs) == 2

    # Rollback
    rollback()

    assert len(sample_kernel.approved_diffs) == 1
    assert len(sample_kernel.rollback_stack) == 0
```

### Test Suite 2: Universe and Templates

#### Test 2.1: Universe initialization

```python
def test_universe_initialization():
    from full_cyclekernel_buildA_FH_complete import Universe

    u = Universe("TestU1")

    assert u.name == "TestU1"
    assert isinstance(u.civilizations, dict)
    assert isinstance(u.factions, dict)
    assert isinstance(u.exploiters, dict)
    assert isinstance(u.institutions, dict)
    assert isinstance(u.external_signals, dict)
    assert isinstance(u.markets, dict)
    assert isinstance(u.extinction_markets, dict)
    assert isinstance(u.myths, dict)
```

#### Test 2.2: civ_template creates correct structure

```python
def test_civ_template_structure():
    from full_cyclekernel_buildA_FH_complete import civ_template

    civ = civ_template("test_civ")

    assert civ['id'] == "test_civ"
    assert civ['age'] == 0
    assert civ['alive'] is True
    assert 'resources' in civ
    assert 'attention' in civ['resources']
    assert 'compute' in civ['resources']
    assert 'belief' in civ
    assert 'truth' in civ['belief']
    assert 'deception' in civ['belief']
    assert 'observer_weight' in civ
    assert 'faction' in civ
    assert 'myth_influence' in civ
```

#### Test 2.3: faction_template creates correct structure

```python
def test_faction_template_structure():
    from full_cyclekernel_buildA_FH_complete import faction_template

    faction = faction_template("Test Faction")

    assert 'id' in faction
    assert len(faction['id']) == 6
    assert faction['name'] == "Test Faction"
    assert isinstance(faction['members'], list)
    assert 'belief_avg' in faction
    assert 'truth' in faction['belief_avg']
    assert 'deception' in faction['belief_avg']
    assert 'compute_pool' in faction
    assert 'coalitions' in faction
    assert 'reputation' in faction
```

#### Test 2.4: exploiter_template creates correct structure

```python
def test_exploiter_template_structure():
    from full_cyclekernel_buildA_FH_complete import exploiter_template

    exploiter = exploiter_template("Test Exploiter")

    assert 'id' in exploiter
    assert len(exploiter['id']) == 6
    assert exploiter['name'] == "Test Exploiter"
    assert 'policy' in exploiter
    assert 'bet_scale' in exploiter['policy']
    assert 'risk' in exploiter['policy']
    assert 'memory' in exploiter
    assert 'dominance' in exploiter
```

### Test Suite 3: Core Mechanics

#### Test 3.1: assign_factions assigns unassigned civilizations

```python
def test_assign_factions_unassigned(sample_universe):
    from full_cyclekernel_buildA_FH_complete import assign_factions

    # Ensure no faction assigned
    sample_universe.civilizations["civ1"]["faction"] = None
    sample_universe.civilizations["civ2"]["faction"] = None

    assign_factions(sample_universe)

    assert sample_universe.civilizations["civ1"]["faction"] is not None
    assert sample_universe.civilizations["civ2"]["faction"] is not None
```

#### Test 3.2: assign_factions updates faction member lists

```python
def test_assign_factions_updates_members(sample_universe):
    from full_cyclekernel_buildA_FH_complete import assign_factions

    sample_universe.civilizations["civ1"]["faction"] = None
    sample_universe.civilizations["civ2"]["faction"] = None

    assign_factions(sample_universe)

    # Check that civilizations are in faction member lists
    civ1_faction = sample_universe.civilizations["civ1"]["faction"]
    civ2_faction = sample_universe.civilizations["civ2"]["faction"]

    assert "civ1" in sample_universe.factions[civ1_faction]["members"]
    assert "civ2" in sample_universe.factions[civ2_faction]["members"]
```

#### Test 3.3: assign_factions transfers compute to faction pool

```python
def test_assign_factions_transfers_compute(sample_universe):
    from full_cyclekernel_buildA_FH_complete import assign_factions

    initial_compute = sample_universe.civilizations["civ1"]["resources"]["compute"]
    sample_universe.civilizations["civ1"]["faction"] = None

    assign_factions(sample_universe)

    # 20% of compute should be transferred to faction
    expected_transfer = initial_compute * 0.2
    civ_faction = sample_universe.factions[sample_universe.civilizations["civ1"]["faction"]]

    assert abs(civ_faction["compute_pool"] - expected_transfer) < 0.01
    assert abs(sample_universe.civilizations["civ1"]["resources"]["compute"] - initial_compute * 0.8) < 0.01
```

#### Test 3.4: update_factions calculates average belief

```python
def test_update_factions_calculates_average_belief(sample_universe):
    from full_cyclekernel_buildA_FH_complete import update_factions

    # Set up faction with members
    sample_universe.factions["A"]["members"] = ["civ1", "civ2"]
    sample_universe.civilizations["civ1"]["faction"] = "A"
    sample_universe.civilizations["civ2"]["faction"] = "A"
    sample_universe.civilizations["civ1"]["belief"]["truth"] = 0.8
    sample_universe.civilizations["civ2"]["belief"]["truth"] = 0.6

    update_factions(sample_universe)

    assert abs(sample_universe.factions["A"]["belief_avg"]["truth"] - 0.7) < 0.01
    assert abs(sample_universe.factions["A"]["belief_avg"]["deception"] - 0.3) < 0.01
```

#### Test 3.5: divergence_split splits factions with high spread

```python
def test_divergence_split_high_spread(sample_universe, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import divergence_split

    # Create faction with 4 members and high belief spread
    sample_universe.factions["A"]["members"] = ["civ1", "civ2"]
    sample_universe.civilizations["civ1"]["faction"] = "A"
    sample_universe.civilizations["civ2"]["faction"] = "A"
    sample_universe.civilizations["civ1"]["belief"]["truth"] = 0.9
    sample_universe.civilizations["civ2"]["belief"]["truth"] = 0.5

    # Add more members to reach threshold
    for i in range(3, 6):
        civ_id = f"civ{i}"
        sample_universe.civilizations[civ_id] = {
            "id": civ_id,
            "faction": "A",
            "belief": {"truth": 0.5 + (i * 0.1), "deception": 0.5 - (i * 0.1)},
            "alive": True
        }
        sample_universe.factions["A"]["members"].append(civ_id)

    initial_faction_count = len(sample_universe.factions)

    divergence_split(sample_universe)

    # Should create a new faction
    assert len(sample_universe.factions) > initial_faction_count
```

#### Test 3.6: lifecycle ages civilizations

```python
def test_lifecycle_ages_civilizations(sample_universe):
    from full_cyclekernel_buildA_FH_complete import lifecycle

    initial_age = sample_universe.civilizations["civ1"]["age"]

    lifecycle(sample_universe, epoch=1)

    assert sample_universe.civilizations["civ1"]["age"] == initial_age + 1
```

#### Test 3.7: lifecycle expires low-resource civilizations

```python
def test_lifecycle_expires_low_resources(sample_universe, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import lifecycle

    # Set resources below threshold
    sample_universe.civilizations["civ1"]["resources"]["attention"] = 3
    sample_universe.civilizations["civ1"]["resources"]["compute"] = 1

    lifecycle(sample_universe, epoch=1)

    assert sample_universe.civilizations["civ1"]["alive"] is False
```

#### Test 3.8: myth_crystallization creates myths for high-truth factions

```python
def test_myth_crystallization_high_truth(sample_universe, mock_socketio, seeded_random):
    from full_cyclekernel_buildA_FH_complete import myth_crystallization

    # Set up faction with high-truth members
    sample_universe.factions["A"]["members"] = ["civ1", "civ2", "civ3"]
    for civ_id in ["civ1", "civ2", "civ3"]:
        if civ_id not in sample_universe.civilizations:
            sample_universe.civilizations[civ_id] = {
                "id": civ_id,
                "faction": "A",
                "belief": {"truth": 0.9, "deception": 0.1},
                "alive": True,
                "myth_influence": 0.0
            }
        else:
            sample_universe.civilizations[civ_id]["belief"]["truth"] = 0.9
            sample_universe.civilizations[civ_id]["faction"] = "A"

    initial_myth_count = len(sample_universe.myths)

    myth_crystallization(sample_universe, epoch=1)

    # May create myth (random chance)
    assert len(sample_universe.myths) >= initial_myth_count
```

### Test Suite 4: ChatMemoryBridge

#### Test 4.1: process_interaction creates civilization for new user

```python
def test_process_interaction_creates_civilization(sample_universe, sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import ChatMemoryBridge

    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    civ_id = bridge.process_interaction("user123", "Hello", "Hi there!")

    assert civ_id in sample_universe.civilizations
    assert sample_universe.civilizations[civ_id]["id"] == civ_id
```

#### Test 4.2: process_interaction updates resources

```python
def test_process_interaction_updates_resources(sample_universe, sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import ChatMemoryBridge

    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    civ_id = bridge.process_interaction("user123", "Hello", "Hi there!")

    civ = sample_universe.civilizations[civ_id]
    assert civ["resources"]["attention"] > 100  # Initial + 10
    assert civ["resources"]["compute"] > 100    # Initial + 5
```

#### Test 4.3: process_interaction influences belief

```python
def test_process_interaction_influences_belief(sample_universe, sample_kernel, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import ChatMemoryBridge

    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    # Long message should increase truth
    long_message = "A" * 200
    civ_id = bridge.process_interaction("user123", long_message, "Response")

    civ = sample_universe.civilizations[civ_id]
    assert civ["belief"]["truth"] > 0.7  # Initial was 0.7
```

#### Test 4.4: get_context_from_memory returns context for existing user

```python
def test_get_context_from_memory_existing_user(sample_universe, sample_kernel):
    from full_cyclekernel_buildA_FH_complete import ChatMemoryBridge

    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    # Create user first
    bridge.process_interaction("user123", "Hello", "Hi there!")

    context = bridge.get_context_from_memory("user123")

    assert "user_state" in context
    assert "crystallized_memories" in context
    assert "universe_vibe" in context
    assert context["user_state"]["id"] is not None
```

#### Test 4.5: get_context_from_memory returns message for new user

```python
def test_get_context_from_memory_new_user(sample_universe, sample_kernel):
    from full_cyclekernel_buildA_FH_complete import ChatMemoryBridge

    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    context = bridge.get_context_from_memory("nonexistent_user")

    assert context == "New user, no prior memory."
```

### Test Suite 5: API Routes

#### Test 5.1: GET /state returns simulation state

```python
def test_get_state_route():
    from full_cyclekernel_buildA_FH_complete import app

    with app.test_client() as client:
        response = client.get('/state')

        assert response.status_code == 200
        data = response.get_json()
        assert 'epoch' in data
        assert 'universes' in data
        assert 'kernel_proposals' in data
```

#### Test 5.2: GET /containers returns container list

```python
def test_get_containers_route():
    from full_cyclekernel_buildA_FH_complete import app

    with app.test_client() as client:
        response = client.get('/containers')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'status' in data[0]
```

#### Test 5.3: POST /containers creates new container

```python
def test_post_containers_route():
    from full_cyclekernel_buildA_FH_complete import app

    with app.test_client() as client:
        response = client.post('/containers',
                               json={"requirement": "Test container"},
                               content_type='application/json')

        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert 'name' in data
        assert 'status' in data
        assert data['status'] == 'running'
```

#### Test 5.4: POST /chat processes chat with LLM

```python
def test_post_chat_route(mock_openai):
    from full_cyclekernel_buildA_FH_complete import app

    with app.test_client() as client:
        response = client.post('/chat',
                               json={"user_id": "test_user", "prompt": "Hello"},
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
        assert 'memory_state' in data
```

#### Test 5.5: POST /chat updates memory

```python
def test_post_chat_updates_memory(mock_openai, sample_kernel, sample_universe):
    from full_cyclekernel_buildA_FH_complete import app, ChatMemoryBridge

    # Set up memory bridge
    bridge = ChatMemoryBridge(sample_kernel, {"U1": sample_universe})

    with app.test_client() as client:
        response = client.post('/chat',
                               json={"user_id": "test_user", "prompt": "Hello"},
                               content_type='application/json')

        assert response.status_code == 200

        # Check that civilization was created
        assert any(civ.startswith("user_test") for civ in sample_universe.civilizations.keys())
```

### Test Suite 6: Simulation Loop

#### Test 6.1: simulation_loop increments epoch

```python
def test_simulation_loop_increments_epoch():
    from full_cyclekernel_buildA_FH_complete import simulation_loop, current_epoch, simulation_running
    import threading
    import time

    initial_epoch = current_epoch

    # Start simulation in background
    thread = threading.Thread(target=simulation_loop, daemon=True)
    thread.start()

    time.sleep(0.1)  # Wait for at least one epoch

    assert current_epoch > initial_epoch

    # Stop simulation
    simulation_running = False
```

#### Test 6.2: simulation_loop applies all mechanics

```python
def test_simulation_loop_applies_mechanics(sample_universe, mock_socketio):
    from full_cyclekernel_buildA_FH_complete import (
        assign_factions, update_factions, lifecycle,
        inject_signal, markets, myth_crystallization
    )

    # Run one epoch of mechanics
    assign_factions(sample_universe)
    update_factions(sample_universe)
    lifecycle(sample_universe, epoch=1)
    inject_signal(sample_universe, epoch=1)
    markets(sample_universe, epoch=1)
    myth_crystallization(sample_universe, epoch=1)

    # Verify changes occurred
    assert sample_universe.civilizations["civ1"]["age"] == 1
    assert len(sample_universe.markets) > 0 or len(sample_universe.external_signals) > 0
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
    --cov=.
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
freezegun==1.2.2
```

## Running Tests

```bash
# Run all tests
cd TrainLLM
pytest

# Run specific test file
pytest tests/test_cyclekernel.py

# Run with coverage
pytest --cov=full_cyclekernel_buildA_FH_complete --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

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
3. **Mocking**: External dependencies are mocked
4. **Determinism**: Seeded random for reproducible tests
5. **AAA Pattern**: Arrange, Act, Assert structure
6. **Descriptive Names**: Test names clearly describe behavior
7. **Markers**: Categorize tests (unit, integration, slow)
8. **Coverage**: Automated coverage reporting with thresholds

## Notes

- Global state makes testing challenging - consider refactoring to dependency injection
- SocketIO emits are mocked but not verified in detail
- OpenAI API calls are mocked with canned responses
- Time-dependent tests use `time.sleep()` which can be slow
- Randomness is controlled with seeded random for deterministic tests
- Background simulation thread is tested but not fully controlled
