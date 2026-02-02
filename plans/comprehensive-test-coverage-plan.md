# Comprehensive Test Coverage Plan for Anti4 Ecosystem

## Executive Summary

This plan outlines the strategy for adding comprehensive test coverage across all projects in the Anti4 ecosystem. The goal is to achieve high code coverage, ensure reliability, and establish a robust testing infrastructure.

## Current State Analysis

### Existing Test Infrastructure

**TrainLLM (TypeScript)**
- ✅ Jest configured with ts-jest preset
- ✅ Existing tests: [`auth.test.ts`](../TrainLLM/src/__tests__/auth.test.ts), [`server.test.ts`](../TrainLLM/src/__tests__/server.test.ts), [`zk.test.ts`](../TrainLLM/src/__tests__/zk.test.ts)
- ✅ Test script: `npm test`
- ❌ Missing tests for: [`llm-adapter.ts`](../TrainLLM/src/llm-adapter.ts), [`memory-loop.ts`](../TrainLLM/src/memory-loop.ts), [`model-disagreement-logger.ts`](../TrainLLM/src/model-disagreement-logger.ts)

**TrainLLM (Python)**
- ❌ No testing framework configured
- ❌ No existing tests
- Files needing tests: [`chatbot_memory_core.py`](../TrainLLM/chatbot_memory_core.py), [`full_cyclekernel_buildA_FH_complete.py`](../TrainLLM/full_cyclekernel_buildA_FH_complete.py)

**v0-ai-agent-for-servers (Next.js)**
- ❌ No testing framework configured
- ❌ No existing tests
- Files needing tests: API routes, React components

**unified_llm_integration.py**
- ❌ No testing framework configured
- ❌ No existing tests

## Testing Strategy

### 1. TrainLLM TypeScript Tests

#### 1.1 [`llm-adapter.ts`](../TrainLLM/src/llm-adapter.ts) Tests
**File**: `TrainLLM/src/__tests__/llm-adapter.test.ts`

**Test Cases**:
- ✅ `initializeLLM()` returns an object with `generate` method
- ✅ `generate()` method accepts a prompt string
- ✅ `generate()` returns an object with `text` property
- ✅ Mock LLM responses for testing integration

#### 1.2 [`memory-loop.ts`](../TrainLLM/src/memory-loop.ts) Tests
**File**: `TrainLLM/src/__tests__/memory-loop.test.ts`

**Test Cases**:
- ✅ `logAction()` writes valid JSON to action-log.jsonl
- ✅ `logAction()` includes timestamp, action, and result
- ✅ `readActions()` returns empty array when file doesn't exist
- ✅ `readActions()` parses and returns all log entries
- ✅ `readActions()` handles malformed JSON gracefully
- ✅ Multiple log actions are appended correctly

#### 1.3 [`model-disagreement-logger.ts`](../TrainLLM/src/model-disagreement-logger.ts) Tests
**File**: `TrainLLM/src/__tests__/model-disagreement-logger.test.ts`

**Test Cases**:
- ✅ `logDisagreement()` writes valid JSON to disagreement-log.jsonl
- ✅ `logDisagreement()` includes timestamp, model1, model2, decision
- ✅ `logDisagreement()` correctly calculates `agreed` boolean
- ✅ `agreed` is true when model1 equals model2
- ✅ `agreed` is false when model1 differs from model2

### 2. TrainLLM Python Tests

#### 2.1 Setup pytest for Python
**Requirements**:
- Add `pytest` and `pytest-asyncio` to [`requirements.txt`](../TrainLLM/requirements.txt)
- Create `pytest.ini` configuration
- Create `tests/` directory structure

#### 2.2 [`chatbot_memory_core.py`](../TrainLLM/chatbot_memory_core.py) Tests
**File**: `TrainLLM/tests/test_chatbot_memory_core.py`

**Test Cases**:
- ✅ `ChatMemoryBridge.__init__()` initializes kernel and universes
- ✅ `process_interaction()` creates new civilization for new user
- ✅ `process_interaction()` updates existing civilization resources
- ✅ `process_interaction()` increases attention and compute
- ✅ `process_interaction()` influences belief based on message length
- ✅ `process_interaction()` logs interaction to kernel audit_logs
- ✅ `get_context_from_memory()` returns "No prior memory" for new user
- ✅ `get_context_from_memory()` returns user state for existing user
- ✅ `get_context_from_memory()` includes related myths based on faction
- ✅ `get_context_from_memory()` includes universe vibe statistics

#### 2.3 [`full_cyclekernel_buildA_FH_complete.py`](../TrainLLM/full_cyclekernel_buildA_FH_complete.py) Tests
**File**: `TrainLLM/tests/test_full_cyclekernel.py`

**Test Cases**:

**CycleKernel Class**:
- ✅ `CycleKernel.__init__()` initializes with prime_directive
- ✅ `propose_change()` creates proposal with unique ID
- ✅ `propose_change()` simulates counterfactuals
- ✅ `propose_change()` adds to proposals list
- ✅ `propose_change()` logs proposal to audit_logs
- ✅ `approve_proposal()` approves high-trust proposals
- ✅ `approve_proposal()` rejects low-trust proposals
- ✅ `approve_proposal()` moves approved diffs to approved_diffs
- ✅ `approve_proposal()` saves state to rollback_stack
- ✅ `rollback()` restores previous state from rollback_stack
- ✅ `rollback()` logs rollback to audit_logs

**Universe & Templates**:
- ✅ `Universe.__init__()` initializes all data structures
- ✅ `civ_template()` creates civilization with correct structure
- ✅ `faction_template()` creates faction with correct structure
- ✅ `exploiter_template()` creates exploiter with correct structure
- ✅ `institution_template()` creates institution with correct structure
- ✅ `market_template()` creates market with correct structure
- ✅ `extinction_market_template()` creates extinction market with correct structure

**Core Mechanics**:
- ✅ `assign_factions()` assigns unassigned civilizations to factions
- ✅ `assign_factions()` updates faction member lists
- ✅ `assign_factions()` transfers compute to faction pool
- ✅ `update_factions()` calculates average belief for factions
- ✅ `divergence_split()` splits factions with high belief spread
- ✅ `narrative_escalation()` increases belief over time
- ✅ `exploiter_actions()` creates institutions
- ✅ `institution_proof()` updates institution lock based on truth
- ✅ `cross_universe_injection()` injects signals between universes
- ✅ `inject_signal()` creates external signals and markets
- ✅ `markets()` resolves markets and updates reputation
- ✅ `lifecycle()` ages civilizations and expires low-resource ones
- ✅ `extinction_markets_logic()` creates and resolves extinction markets
- ✅ `myth_crystallization()` creates myths for high-truth factions
- ✅ `auto_proposals()` generates resource injection proposals
- ✅ `apply_approved_diffs()` applies approved changes to civilizations

**ChatMemoryBridge**:
- ✅ `process_interaction()` creates civilization for new users
- ✅ `process_interaction()` updates resources for existing users
- ✅ `process_interaction()` updates belief based on message length
- ✅ `process_interaction()` emits socket events
- ✅ `get_context_from_memory()` returns context for users
- ✅ `get_context_from_memory()` includes related myths

**API Routes**:
- ✅ `GET /state` returns full simulation state
- ✅ `GET /containers` returns mock container list
- ✅ `POST /containers` creates new container
- ✅ `POST /chat` processes chat with LLM
- ✅ `POST /chat` updates memory based on interaction
- ✅ `POST /chat` returns response and memory state

### 3. unified_llm_integration.py Tests

#### 3.1 Setup pytest for unified_llm_integration
**File**: `tests/test_unified_llm_integration.py`

**Test Cases**:

**UnifiedLLMOrchestrator Class**:
- ✅ `__init__()` initializes with OpenAI API key
- ✅ `__init__()` sets up component configurations
- ✅ `start_monitoring_thread()` starts background monitoring
- ✅ `_check_component_health()` updates component status
- ✅ `_check_component_health()` handles offline components
- ✅ `_sync_unified_state()` syncs TrainLLM state
- ✅ `_sync_unified_state()` handles connection errors
- ✅ `query_unified_llm()` builds correct system prompt
- ✅ `query_unified_llm()` sends request to OpenAI API
- ✅ `query_unified_llm()` parses JSON responses
- ✅ `query_unified_llm()` handles non-JSON responses
- ✅ `query_unified_llm()` handles API errors
- ✅ `_build_unified_system_prompt()` returns comprehensive prompt
- ✅ `_parse_llm_response()` parses valid JSON
- ✅ `_parse_llm_response()` handles invalid JSON
- ✅ `execute_action()` routes to correct component handler
- ✅ `execute_action()` handles unknown components
- ✅ `_execute_trainllm_action()` handles query_llm actions
- ✅ `_execute_trainllm_action()` handles approve_proposal actions
- ✅ `_execute_trainllm_action()` handles unknown actions
- ✅ `_execute_ai_agent_action()` returns placeholder response
- ✅ `_execute_docs_action()` handles generate_docs actions
- ✅ `_generate_documentation()` generates docs via LLM
- ✅ `get_unified_health_status()` returns comprehensive status
- ✅ `_calculate_overall_health()` returns correct health level

**LLMIntegrationAPI Class**:
- ✅ `__init__()` initializes Flask app with routes
- ✅ `GET /health` returns unified health status
- ✅ `POST /query` requires query parameter
- ✅ `POST /query` returns LLM response
- ✅ `POST /query` handles missing query parameter
- ✅ `POST /execute` requires component and action
- ✅ `POST /execute` executes action on component
- ✅ `POST /execute` handles missing parameters
- ✅ `GET /state` returns unified state and components

### 4. v0-ai-agent-for-servers Tests

#### 4.1 Setup Jest + React Testing Library
**Requirements**:
- Add Jest, React Testing Library, and related dependencies to [`package.json`](../v0-ai-agent-for-servers/package.json)
- Create `jest.config.js` configuration
- Create `__tests__/` directory structure
- Update `package.json` with test scripts

#### 4.2 API Route Tests
**Directory**: `v0-ai-agent-for-servers/src/app/api/__tests__/`

**[`health/route.ts`](../v0-ai-agent-for-servers/src/app/api/health/route.ts) Tests**:
- ✅ `GET /api/health` returns 200 status
- ✅ `GET /api/health` returns component name
- ✅ `GET /api/health` returns online status
- ✅ `GET /api/health` returns timestamp
- ✅ `GET /api/health` returns version
- ✅ `GET /api/health` returns endpoints list

**[`cross-sync/route.ts`](../v0-ai-agent-for-servers/src/app/api/cross-sync/route.ts) Tests**:
- ✅ `POST /api/cross-sync` processes sync request
- ✅ `POST /api/cross-sync` handles unified_state parameter
- ✅ `POST /api/cross-sync` handles component_states parameter
- ✅ `POST /api/cross-sync` handles sync_type parameter
- ✅ `POST /api/cross-sync` processes TrainLLM state updates
- ✅ `POST /api/cross-sync` generates resource alerts for low resources
- ✅ `POST /api/cross-sync` generates health monitoring recommendations
- ✅ `POST /api/cross-sync` returns sync result
- ✅ `POST /api/cross-sync` handles errors gracefully

**[`unified-query/route.ts`](../v0-ai-agent-for-servers/src/app/api/unified-query/route.ts) Tests**:
- ✅ `POST /api/unified-query` requires query parameter
- ✅ `POST /api/unified-query` returns 400 for missing query
- ✅ `POST /api/unified-query` processes container queries
- ✅ `POST /api/unified-query` processes server queries
- ✅ `POST /api/unified-query` processes terminal queries
- ✅ `POST /api/unified-query` processes general queries
- ✅ `POST /api/unified-query` returns agent capabilities
- ✅ `POST /api/unified-query` handles errors gracefully

#### 4.3 Component Tests
**Directory**: `v0-ai-agent-for-servers/src/components/__tests__/`

**[`container-manager.tsx`](../v0-ai-agent-for-servers/src/components/container-manager.tsx) Tests**:
- ✅ Component renders without errors
- ✅ Component displays "No containers running" when empty
- ✅ Component fetches containers on mount
- ✅ Component displays container list
- ✅ Component displays container name
- ✅ Component displays container status
- ✅ Component displays container description
- ✅ Component displays container creation date
- ✅ Component displays compute tokens when available
- ✅ "Create New Container" button triggers creation
- ✅ "Create New Container" button shows loading state
- ✅ "Refresh" button triggers container fetch
- ✅ Component handles fetch errors gracefully
- ✅ Component handles creation errors gracefully
- ✅ Component creates fallback container on error

**[`terminal.tsx`](../v0-ai-agent-for-servers/src/components/terminal.tsx) Tests**:
- ✅ Component renders without errors
- ✅ Terminal initializes with welcome message
- ✅ Terminal displays prompt
- ✅ Terminal handles character input
- ✅ Terminal handles backspace
- ✅ Terminal handles enter key
- ✅ Terminal cleans up on unmount
- ✅ Terminal uses correct theme colors

**[`open-manus.tsx`](../v0-ai-agent-for-servers/src/components/open-manus.tsx) Tests**:
- ✅ Component renders without errors
- ✅ Component displays header with icon
- ✅ Component displays description
- ✅ Component displays input field
- ✅ Component displays "Build App" button
- ✅ Component displays "No applications deployed" when empty
- ✅ Input field updates appRequirement state
- ✅ "Build App" button is disabled when input is empty
- ✅ "Build App" button shows loading state during build
- ✅ "Build App" button calls TrainLLM chat endpoint
- ✅ Component displays built applications
- ✅ Component displays app name
- ✅ Component displays app status
- ✅ Component displays compute tokens
- ✅ Component handles API errors gracefully
- ✅ Component clears input after successful build

### 5. Test Coverage Reporting

#### 5.1 TrainLLM TypeScript Coverage
- Configure Jest to generate coverage reports
- Set coverage thresholds (e.g., 80%)
- Generate HTML coverage reports
- Add coverage script to package.json

#### 5.2 TrainLLM Python Coverage
- Configure pytest-cov for coverage reporting
- Set coverage thresholds (e.g., 80%)
- Generate HTML coverage reports
- Add coverage script to package.json/requirements

#### 5.3 v0-ai-agent-for-servers Coverage
- Configure Jest for coverage reporting
- Set coverage thresholds (e.g., 80%)
- Generate HTML coverage reports
- Add coverage script to package.json

#### 5.4 unified_llm_integration Coverage
- Configure pytest-cov for coverage reporting
- Set coverage thresholds (e.g., 80%)
- Generate HTML coverage reports

### 6. Test Documentation

#### 6.1 Create Testing Guidelines
**File**: `TESTING_GUIDELINES.md`

Contents:
- Testing philosophy and best practices
- How to write unit tests
- How to write integration tests
- How to write component tests
- Mocking strategies
- Test naming conventions
- Coverage requirements

#### 6.2 Create Test Execution Guide
**File**: `TEST_EXECUTION_GUIDE.md`

Contents:
- How to run tests for each project
- How to run specific test suites
- How to run tests in watch mode
- How to generate coverage reports
- CI/CD integration instructions

## Implementation Order

### Phase 1: Infrastructure Setup
1. Set up pytest for Python projects
2. Set up Jest + React Testing Library for v0-ai-agent-for-servers
3. Configure coverage reporting for all projects

### Phase 2: TrainLLM Tests
1. Add TypeScript tests for llm-adapter, memory-loop, model-disagreement-logger
2. Add Python tests for chatbot_memory_core
3. Add Python tests for full_cyclekernel_buildA_FH_complete

### Phase 3: Integration Tests
1. Add tests for unified_llm_integration.py
2. Add API route tests for v0-ai-agent-for-servers

### Phase 4: Component Tests
1. Add component tests for container-manager
2. Add component tests for terminal
3. Add component tests for open-manus

### Phase 5: Documentation
1. Create testing guidelines
2. Create test execution guide
3. Update project READMEs with testing information

## Success Criteria

- ✅ All projects have test coverage ≥ 80%
- ✅ All critical paths have test coverage ≥ 90%
- ✅ All tests pass consistently
- ✅ Coverage reports are generated automatically
- ✅ Documentation is complete and up-to-date
- ✅ Tests can be run locally and in CI/CD

## Testing Tools Summary

| Project | Testing Framework | Coverage Tool | Status |
|---------|------------------|--------------|--------|
| TrainLLM (TS) | Jest | Jest Coverage | ✅ Configured |
| TrainLLM (PY) | pytest | pytest-cov | ❌ Needs Setup |
| v0-ai-agent-for-servers | Jest + RTL | Jest Coverage | ❌ Needs Setup |
| unified_llm_integration | pytest | pytest-cov | ❌ Needs Setup |

## Notes

- All tests should be isolated and independent
- Use mocking for external dependencies (API calls, file system, etc.)
- Tests should be fast and reliable
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names that explain what is being tested
