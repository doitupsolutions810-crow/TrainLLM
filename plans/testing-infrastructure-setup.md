# Testing Infrastructure Setup Guide

## Overview

This guide provides detailed instructions for setting up testing infrastructure across all projects in the Anti4 ecosystem:
- **TrainLLM (TypeScript)**: Jest with ts-jest
- **TrainLLM (Python)**: pytest with pytest-cov
- **v0-ai-agent-for-servers**: Jest with React Testing Library
- **unified_llm_integration.py**: pytest with pytest-cov

---

# Part 1: TrainLLM TypeScript Testing Infrastructure

## Current State

TrainLLM already has Jest configured:
- [`jest.config.ts`](../TrainLLM/jest.config.ts) exists
- Test script in [`package.json`](../TrainLLM/package.json): `"test": "jest --runInBand"`
- Existing tests in [`src/__tests__/`](../TrainLLM/src/__tests__/)

## Configuration Files

### jest.config.ts

```typescript
import type { Config } from '@jest/types';

const config: Config.InitialOptions = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**',
  ],
  coverageThresholds: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
};

export default config;
```

### package.json additions

```json
{
  "scripts": {
    "test": "jest --runInBand",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2"
  }
}
```

## Dependencies

### Already installed (from package.json)

```json
{
  "devDependencies": {
    "@types/jest": "^29.5.2",
    "jest": "^29.6.1",
    "ts-jest": "^29.1.0",
    "typescript": "^5.6.2"
  }
}
```

### Additional recommended dependencies

```bash
npm install --save-dev @types/jest-environment-node
```

## Running Tests

```bash
cd TrainLLM

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- memory-loop.test.ts

# Run specific test
npm test -t "logAction writes valid JSON"
```

## Coverage Reports

Coverage reports are generated in:
- `coverage/` directory (HTML report)
- Terminal output (text summary)
- `coverage/lcov.info` (LCOV format)

---

# Part 2: TrainLLM Python Testing Infrastructure

## Current State

TrainLLM has Python files but no testing infrastructure:
- No pytest configuration
- No test dependencies in [`requirements.txt`](../TrainLLM/requirements.txt)
- No test directory

## Setup Steps

### Step 1: Create pytest.ini

Create [`TrainLLM/pytest.ini`](../TrainLLM/pytest.ini):

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

### Step 2: Create requirements-test.txt

Create [`TrainLLM/requirements-test.txt`](../TrainLLM/requirements-test.txt):

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### Step 3: Install test dependencies

```bash
cd TrainLLM
pip install -r requirements-test.txt
```

### Step 4: Create test directory structure

```bash
cd TrainLLM
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
```

### Step 5: Create conftest.py

Create [`TrainLLM/tests/conftest.py`](../TrainLLM/tests/conftest.py):

```python
import pytest
import sys
import os

# Add TrainLLM to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_kernel():
    """Create a mock CycleKernel"""
    from unittest.mock import Mock
    kernel = Mock()
    kernel.audit_logs = []
    kernel.proposals = []
    kernel.approved_diffs = []
    kernel.rollback_stack = []
    return kernel

@pytest.fixture
def mock_universe():
    """Create a mock Universe"""
    from unittest.mock import Mock
    universe = Mock()
    universe.civilizations = {}
    universe.factions = {}
    universe.exploiters = {}
    universe.institutions = {}
    universe.external_signals = {}
    universe.markets = {}
    universe.extinction_markets = {}
    universe.myths = {}
    return universe
```

## Running Tests

```bash
cd TrainLLM

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_chatbot_memory_core.py

# Run specific test
pytest tests/test_chatbot_memory_core.py -k "process_interaction_creates_civilization"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run excluding slow tests
pytest -m "not slow"

# Run in verbose mode
pytest -v

# Run with specific Python version
python3 -m pytest
```

## Coverage Reports

Coverage reports are generated in:
- `htmlcov/` directory (HTML report)
- Terminal output (text summary)
- `.coverage` file (coverage data)

---

# Part 3: v0-ai-agent-for-servers Testing Infrastructure

## Current State

v0-ai-agent-for-servers has no testing infrastructure:
- No Jest configuration
- No test dependencies in [`package.json`](../v0-ai-agent-for-servers/package.json)
- No test directory

## Setup Steps

### Step 1: Create jest.config.js

Create [`v0-ai-agent-for-servers/jest.config.js`](../v0-ai-agent-for-servers/jest.config.js):

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/__tests__/**/*.test.tsx',
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
  ],
  coverageThresholds: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
}

// createJestConfig is exported this way to ensure that next/jest can load Next.js config
module.exports = createJestConfig(customJestConfig)
```

### Step 2: Create jest.setup.js

Create [`v0-ai-agent-for-servers/jest.setup.js`](../v0-ai-agent-for-servers/jest.setup.js):

```javascript
import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return ''
  },
}))

// Mock xterm.js
jest.mock('xterm', () => ({
  Terminal: jest.fn().mockImplementation(() => ({
    open: jest.fn(),
    loadAddon: jest.fn(),
    write: jest.fn(),
    writeln: jest.fn(),
    onData: jest.fn(),
    dispose: jest.fn(),
  })),
}))

// Mock xterm addons
jest.mock('xterm-addon-fit', () => ({
  FitAddon: jest.fn().mockImplementation(() => ({
    fit: jest.fn(),
  })),
}))

jest.mock('xterm-addon-web-links', () => jest.fn())
```

### Step 3: Update package.json

Update [`v0-ai-agent-for-servers/package.json`](../v0-ai-agent-for-servers/package.json):

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2"
  },
  "devDependencies": {
    "@dyad-sh/nextjs-webpack-component-tagger": "^0.8.0",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "postcss": "^8",
    "tailwindcss": "^3.4.1",
    "typescript": "^5",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "next-jest": "^29.7.0"
  }
}
```

### Step 4: Install test dependencies

```bash
cd v0-ai-agent-for-servers
npm install --save-dev @testing-library/jest-dom @testing-library/react @testing-library/user-event jest jest-environment-jsdom next-jest
```

### Step 5: Create test directory structure

```bash
cd v0-ai-agent-for-servers
mkdir -p src/app/api/__tests__
mkdir -p src/components/__tests__
```

## Running Tests

```bash
cd v0-ai-agent-for-servers

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test api/health.test.ts

# Run specific test
npm test -t "returns 200 status"

# Run in verbose mode
npm test -- --verbose
```

## Coverage Reports

Coverage reports are generated in:
- `coverage/` directory (HTML report)
- Terminal output (text summary)
- `coverage/lcov.info` (LCOV format)

---

# Part 4: unified_llm_integration.py Testing Infrastructure

## Current State

unified_llm_integration.py has no testing infrastructure:
- No pytest configuration
- No test dependencies
- No test directory

## Setup Steps

### Step 1: Create pytest.ini

Create [`pytest.ini`](../pytest.ini) in root directory:

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

### Step 2: Create requirements-test.txt

Create [`requirements-test.txt`](../requirements-test.txt) in root directory:

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-flask==1.3.0
```

### Step 3: Install test dependencies

```bash
pip install -r requirements-test.txt
```

### Step 4: Create test directory structure

```bash
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
```

### Step 5: Create conftest.py

Create [`tests/conftest.py`](../tests/conftest.py):

```python
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    import json
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
def sample_orchestrator():
    """Create a sample UnifiedLLMOrchestrator"""
    from unified_llm_integration import UnifiedLLMOrchestrator

    orchestrator = UnifiedLLMOrchestrator("test-api-key")
    return orchestrator
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=unified_llm_integration --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py

# Run specific test
pytest tests/test_orchestrator.py -k "test_orchestrator_initialization"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run excluding slow tests
pytest -m "not slow"
```

## Coverage Reports

Coverage reports are generated in:
- `htmlcov/` directory (HTML report)
- Terminal output (text summary)
- `.coverage` file (coverage data)

---

# Part 5: CI/CD Integration

## GitHub Actions Example

Create [`.github/workflows/test.yml`](../.github/workflows/test.yml):

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-trainllm-ts:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./TrainLLM
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:ci
      - uses: codecov/codecov-action@v3
        with:
          files: ./TrainLLM/coverage/lcov.info
          flags: trainllm-ts

  test-trainllm-py:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./TrainLLM
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      - run: pip install -r requirements-test.txt
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          files: ./TrainLLM/coverage.xml
          flags: trainllm-py

  test-v0-ai-agent:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./v0-ai-agent-for-servers
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:ci
      - uses: codecov/codecov-action@v3
        with:
          files: ./v0-ai-agent-for-servers/coverage/lcov.info
          flags: v0-ai-agent

  test-unified-llm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=unified_llm_integration --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unified-llm
```

---

# Part 6: Pre-commit Hooks

## Using Husky and lint-staged

### Install Husky

```bash
npm install --save-dev husky lint-staged
npx husky install
```

### Create pre-commit hook

```bash
npx husky add .husky/pre-commit "npx lint-staged"
```

### Update package.json

```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "jest --bail --findRelatedTests"
    ],
    "*.{py}": [
      "black",
      "pytest --bail --findRelatedTests"
    ]
  }
}
```

---

# Part 7: VS Code Integration

## Recommended Extensions

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "firsttris.vscode-jest-runner",
    "littlefoxteam.vscode-python-test-adapter"
  ]
}
```

## Settings

Create [`.vscode/settings.json`](../.vscode/settings.json):

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "jest.autoRun": "watch",
  "jest.showCoverageOnLoad": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

# Part 8: Troubleshooting

## Common Issues

### Issue: Jest cannot find modules

**Solution**: Check `moduleNameMapper` in jest.config.js

```javascript
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

### Issue: pytest cannot find modules

**Solution**: Add project to sys.path in conftest.py

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### Issue: Coverage not generating

**Solution**: Check `collectCoverageFrom` configuration

```javascript
collectCoverageFrom: [
  'src/**/*.{js,jsx,ts,tsx}',
  '!src/**/*.d.ts',
  '!src/**/__tests__/**',
],
```

### Issue: Tests timing out

**Solution**: Increase timeout in pytest.ini

```ini
[pytest]
timeout = 300
```

### Issue: Mocks not working

**Solution**: Ensure mocks are in jest.setup.js or conftest.py

```javascript
// jest.setup.js
jest.mock('module-name', () => ({...}))
```

---

# Part 9: Best Practices

## Test Organization

1. **Directory Structure**: Keep tests close to source code
2. **Naming**: Use descriptive test names
3. **Fixtures**: Reuse setup code with fixtures
4. **Markers**: Categorize tests (unit, integration, slow)
5. **Coverage**: Set realistic thresholds (80% is good)

## Test Writing

1. **AAA Pattern**: Arrange, Act, Assert
2. **One Assertion**: One assertion per test when possible
3. **Independence**: Tests should not depend on each other
4. **Mocking**: Mock external dependencies
5. **Cleanup**: Clean up after tests

## CI/CD

1. **Fast Feedback**: Run tests on every push/PR
2. **Parallel**: Run test jobs in parallel
3. **Coverage**: Upload coverage to Codecov
4. **Notifications**: Fail build if tests fail

## Documentation

1. **README**: Document how to run tests
2. **CONTRIBUTING**: Include testing guidelines
3. **Comments**: Explain complex test logic
4. **Examples**: Provide test examples

---

# Summary

This guide provides complete testing infrastructure setup for:

| Project | Framework | Config File | Test Command | Coverage |
|----------|------------|---------------|---------------|-----------|
| TrainLLM (TS) | Jest | jest.config.ts | npm test | npm run test:coverage |
| TrainLLM (PY) | pytest | pytest.ini | pytest | pytest --cov=. |
| v0-ai-agent | Jest | jest.config.js | npm test | npm run test:coverage |
| unified_llm | pytest | pytest.ini | pytest | pytest --cov=unified_llm_integration |

All projects will have:
- ✅ Configured testing framework
- ✅ Coverage reporting
- ✅ CI/CD integration
- ✅ Pre-commit hooks
- ✅ VS Code integration
- ✅ Troubleshooting guide
- ✅ Best practices documentation
