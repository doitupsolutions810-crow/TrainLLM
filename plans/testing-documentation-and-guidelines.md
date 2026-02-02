# Testing Documentation and Guidelines

## Overview

This document provides comprehensive testing guidelines and documentation for the Anti4 ecosystem. It covers testing philosophy, best practices, conventions, and documentation standards for all projects.

---

# Part 1: Testing Philosophy

## Core Principles

### 1. Test What Matters Most
- Focus on critical paths and user-facing functionality
- Prioritize tests for complex logic and external integrations
- Test error conditions and edge cases
- Ensure tests provide value, not just coverage numbers

### 2. Tests Are Code
- Treat tests as first-class citizens
- Maintain tests alongside production code
- Review tests in code reviews
- Refactor tests when production code changes

### 3. Fast Feedback
- Tests should run quickly (seconds, not minutes)
- Use mocking to avoid slow operations
- Parallelize test execution where possible
- Provide clear, actionable failure messages

### 4. Reliability
- Tests should be deterministic (no flakiness)
- Isolate tests from each other
- Clean up after each test
- Use consistent test data

---

# Part 2: Testing Best Practices

## General Guidelines

### 1. AAA Pattern

**Arrange, Act, Assert** - Structure tests clearly:

```typescript
// Arrange
const mockData = createMockData();
const component = render(<Component data={mockData} />);

// Act
await userEvent.click(button);

// Assert
expect(screen.getByText('Success')).toBeInTheDocument();
```

### 2. Descriptive Test Names

Test names should clearly describe what is being tested:

```typescript
// Good
test('logDisagreement sets agreed to true when models match', () => { });

// Bad
test('test1', () => { });
```

### 3. One Assertion Per Test

Keep tests focused on one behavior:

```typescript
// Good
test('returns 200 status', () => {
  expect(response.status).toBe(200);
});

// Bad
test('returns correct response', () => {
  expect(response.status).toBe(200);
  expect(response.body).toHaveProperty('data');
  expect(response.body.data).toBe('test');
});
```

### 4. Test Independence

Each test should be independent and runnable in isolation:

```typescript
beforeEach(() => {
  // Reset state before each test
  jest.clearAllMocks();
  mockData = createFreshMockData();
});
```

### 5. Mock External Dependencies

Mock external services, databases, and APIs:

```typescript
// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({ ok: true, json: () => ({ data: 'test' }) })
);

// Mock file system
jest.mock('fs', () => ({
  writeFileSync: jest.fn(),
  readFileSync: jest.fn(),
}));
```

### 6. Test Error Conditions

Test both success and failure paths:

```typescript
test('handles successful response', async () => {
  mockFetchSuccess({ data: 'success' });
  const result = await fetchData();
  expect(result).toBe('success');
});

test('handles error response', async () => {
  mockFetchError();
  const result = await fetchData();
  expect(result).toBe(null);
});
```

### 7. Use Test Fixtures

Reuse setup code with fixtures:

```typescript
// conftest.py
@pytest.fixture
def mock_kernel():
    return Mock(audit_logs=[])

// test file
def test_with_fixture(mock_kernel):
    assert mock_kernel.audit_logs == []
```

### 8. Test Edge Cases

Test boundary conditions and unusual inputs:

```typescript
test('handles empty input', () => { });
test('handles null input', () => { });
test('handles very long input', () => { });
test('handles special characters', () => { });
test('handles Unicode characters', () => { });
```

---

# Part 3: TypeScript Testing Guidelines

## Jest Configuration

### Test File Location

Place tests next to source code:

```
src/
├── component.ts
└── __tests__/
    └── component.test.ts
```

### Test File Naming

Use `.test.ts` suffix:

```
✅ component.test.ts
❌ component.spec.ts
❌ component.test.js
```

### Import Statements

Import the module being tested:

```typescript
import { functionToTest } from '../module';
```

### Mocking Modules

Use `jest.mock()` for module mocking:

```typescript
jest.mock('fs', () => ({
  writeFileSync: jest.fn(),
  readFileSync: jest.fn(),
}));
```

### Async Testing

Use `async/await` for async functions:

```typescript
test('async function', async () => {
  const result = await asyncFunction();
  expect(result).toBeDefined();
});
```

### React Testing Library

Use user-centric queries:

```typescript
// Good - user-centric
screen.getByRole('button', { name: /submit/i })
screen.getByText('Submit')

// Bad - implementation details
container.querySelector('button.submit-button')
```

---

# Part 4: Python Testing Guidelines

## pytest Configuration

### Test File Location

Place tests in `tests/` directory:

```
project/
├── module.py
└── tests/
    └── test_module.py
```

### Test File Naming

Use `test_` prefix:

```
✅ test_module.py
❌ module_test.py
❌ test_module.py.bak
```

### Test Organization

Group related tests in classes:

```python
class TestModuleName:
    def test_feature_one(self):
        pass

    def test_feature_two(self):
        pass
```

### Fixtures

Use `@pytest.fixture` for reusable setup:

```python
@pytest.fixture
def sample_data():
    return {'key': 'value'}

def test_with_fixture(sample_data):
    assert sample_data['key'] == 'value'
```

### Markers

Use markers to categorize tests:

```python
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_integration():
    pass
```

### Async Testing

Use `pytest-asyncio` for async functions:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

---

# Part 5: React Component Testing Guidelines

## Component Testing

### Test User Interactions

Use `@testing-library/user-event`:

```typescript
import userEvent from '@testing-library/user-event';

test('handles button click', async () => {
  render(<Component />);
  const button = screen.getByRole('button');
  await userEvent.click(button);
  expect(screen.getByText('Success')).toBeInTheDocument();
});
```

### Test State Changes

Verify state changes after interactions:

```typescript
test('updates state on input', async () => {
  render(<Component />);
  const input = screen.getByRole('textbox');
  await userEvent.type(input, 'test value');
  expect(input).toHaveValue('test value');
});
```

### Test Loading States

Verify loading indicators:

```typescript
test('shows loading state', async () => {
  render(<Component />);
  const button = screen.getByRole('button');
  await userEvent.click(button);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
```

### Test Error States

Verify error handling:

```typescript
test('displays error message', async () => {
  mockFetchError();
  render(<Component />);
  const button = screen.getByRole('button');
  await userEvent.click(button);
  expect(screen.getByText(/error/i)).toBeInTheDocument();
});
```

### Test Accessibility

Use role-based queries:

```typescript
test('is accessible', () => {
  render(<Component />);
  expect(screen.getByRole('button')).toBeInTheDocument();
  expect(screen.getByRole('textbox')).toBeInTheDocument();
});
```

---

# Part 6: API Testing Guidelines

## HTTP Testing

### Mock HTTP Requests

Mock `fetch` or HTTP libraries:

```typescript
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => ({ data: 'test' })
  })
);
```

### Test Status Codes

Verify correct HTTP status codes:

```typescript
test('returns 200 on success', async () => {
  mockFetchSuccess();
  const response = await apiCall();
  expect(response.status).toBe(200);
});

test('returns 404 on not found', async () => {
  mockFetchNotFound();
  const response = await apiCall();
  expect(response.status).toBe(404);
});
```

### Test Response Bodies

Verify response structure:

```typescript
test('returns correct response body', async () => {
  mockFetchSuccess({ data: 'test' });
  const response = await apiCall();
  const body = await response.json();
  expect(body).toHaveProperty('data');
  expect(body.data).toBe('test');
});
```

### Test Error Handling

Verify error responses:

```typescript
test('handles network errors', async () => {
  mockFetchNetworkError();
  const response = await apiCall();
  expect(response).toBe(null);
});
```

---

# Part 7: Coverage Guidelines

## Coverage Goals

### Target Coverage Levels

| Type | Target | Description |
|------|---------|-------------|
| Statements | ≥ 80% | Percentage of statements executed |
| Branches | ≥ 75% | Percentage of conditional branches taken |
| Functions | ≥ 80% | Percentage of functions called |
| Lines | ≥ 80% | Percentage of lines executed |

### Critical Path Coverage

Critical paths should have ≥ 90% coverage:
- User-facing features
- Authentication and authorization
- Data persistence
- External API integrations
- Error handling paths

### Exclusions

Exclude from coverage:
- Test files
- Configuration files
- Type definition files
- Generated code
- Third-party libraries

---

# Part 8: Test Documentation

## Test File Documentation

### File Header

Document the purpose of the test file:

```typescript
/**
 * component.test.ts
 * Tests for Component functionality
 *
 * Tests cover:
 * - Component rendering
 * - User interactions
 * - State management
 * - Error handling
 */
```

### Test Documentation

Document complex test logic:

```typescript
test('complex test with multiple steps', async () => {
  // Step 1: Initialize component
  render(<Component />);

  // Step 2: Simulate user input
  const input = screen.getByRole('textbox');
  await userEvent.type(input, 'test value');

  // Step 3: Trigger action
  const button = screen.getByRole('button');
  await userEvent.click(button);

  // Step 4: Verify result
  expect(screen.getByText('Success')).toBeInTheDocument();
});
```

### TODO Comments

Mark areas needing improvement:

```typescript
// TODO: Add test for edge case when input is null
// TODO: Mock external API for better isolation
```

---

# Part 9: CI/CD Integration

## GitHub Actions

### Test Workflow

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - uses: codecov/codecov-action@v3
```

### Coverage Reporting

Upload coverage to Codecov:

```yaml
- uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
    flags: unittests
```

---

# Part 10: Pre-commit Hooks

## Husky Configuration

### Install Husky

```bash
npm install --save-dev husky lint-staged
npx husky install
```

### Pre-commit Hook

```bash
npx husky add .husky/pre-commit "npx lint-staged"
```

### Lint-staged Configuration

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

# Part 11: Troubleshooting

## Common Issues

### Tests Failing Intermittently

**Problem**: Tests pass sometimes but fail other times

**Solutions**:
- Add delays for async operations
- Use `waitFor` instead of fixed timeouts
- Ensure proper cleanup between tests
- Avoid time-dependent assertions

### Tests Running Slowly

**Problem**: Tests take too long to run

**Solutions**:
- Mock external dependencies
- Use test databases instead of real ones
- Parallelize test execution
- Reduce test data size

### Coverage Not Generating

**Problem**: Coverage reports not created

**Solutions**:
- Check `collectCoverageFrom` configuration
- Ensure test files match pattern
- Verify coverage tool is installed
- Check file permissions

### Mocks Not Working

**Problem**: Mocked functions still execute real code

**Solutions**:
- Use `jest.doMock()` before imports
- Ensure mock is in setup file
- Check module path resolution
- Verify mock function signature

---

# Part 12: Test Maintenance

## Regular Maintenance

### Update Tests When Code Changes

- Update tests when production code changes
- Remove tests for deprecated features
- Add tests for new features
- Refactor tests for better maintainability

### Review Test Coverage

- Regularly review coverage reports
- Identify untested critical paths
- Add tests for low-coverage areas
- Remove unnecessary tests

### Keep Tests Fast

- Profile slow tests
- Optimize test setup/teardown
- Reduce test data size
- Use more efficient mocking

---

# Part 13: Project-Specific Guidelines

## TrainLLM (TypeScript)

### Focus Areas
- File system operations (memory-loop, model-disagreement-logger)
- LLM adapter functionality
- Authentication and authorization
- API route handlers

### Key Considerations
- Mock `fs` module for file operations
- Test async operations properly
- Verify JSON structure and format
- Test error conditions

## TrainLLM (Python)

### Focus Areas
- Simulation logic (CycleKernel, Universe)
- Chat memory integration
- API route handlers
- Background simulation loop

### Key Considerations
- Mock global state (kernel, universes)
- Freeze datetime for deterministic tests
- Test complex nested data structures
- Verify SocketIO emits

## v0-ai-agent-for-servers

### Focus Areas
- React components (container-manager, terminal, open-manus)
- API routes (health, cross-sync, unified-query)
- User interactions
- State management

### Key Considerations
- Mock xterm.js for terminal component
- Mock fetch for API calls
- Test React hooks properly
- Verify accessibility

## unified_llm_integration.py

### Focus Areas
- Orchestrator initialization
- Monitoring thread
- LLM query processing
- Action execution
- API route handlers

### Key Considerations
- Mock OpenAI API calls
- Mock HTTP requests to components
- Test background monitoring
- Verify error handling

---

# Part 14: Documentation Standards

## README Updates

### Testing Section

Add testing section to each project's README:

```markdown
## Testing

### Running Tests

```bash
# Run all tests
npm test  # or pytest

# Run with coverage
npm run test:coverage  # or pytest --cov

# Run specific test
npm test -- component.test.ts  # or pytest tests/test_component.py
```

### Test Structure

```
src/__tests__/  # TypeScript tests
tests/            # Python tests
```

### Coverage

Target coverage: ≥ 80%

View coverage report: `coverage/index.html`
```

## CONTRIBUTING.md

Add testing guidelines to CONTRIBUTING:

```markdown
## Testing

### Writing Tests

- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Test both success and failure paths
- Mock external dependencies
- Keep tests independent

### Test Coverage

- Aim for ≥ 80% coverage
- Focus on critical paths
- Test edge cases and error conditions
```

---

# Part 15: Quick Reference

## TypeScript Test Template

```typescript
/**
 * module.test.ts
 * Tests for module functionality
 */

import { functionToTest } from '../module';

describe('module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.resetModules();
  });

  describe('functionToTest', () => {
    test('does something', () => {
      // Arrange
      const input = 'test';

      // Act
      const result = functionToTest(input);

      // Assert
      expect(result).toBe('expected');
    });
  });
});
```

## Python Test Template

```python
"""
test_module.py
Tests for module functionality
"""

import pytest
from module import function_to_test

class TestModule:
    def test_does_something(self):
        # Arrange
        input_value = 'test'

        # Act
        result = function_to_test(input_value)

        # Assert
        assert result == 'expected'
```

## React Component Test Template

```typescript
/**
 * component.test.tsx
 * Tests for Component
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Component } from '../component';

describe('Component', () => {
  test('renders without errors', () => {
    render(<Component />);
    expect(screen.getByText('Component')).toBeInTheDocument();
  });

  test('handles user interaction', async () => {
    render(<Component />);
    const button = screen.getByRole('button');
    await userEvent.click(button);
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```

---

# Summary

This documentation provides:

1. **Testing Philosophy**: Core principles for effective testing
2. **Best Practices**: Guidelines for writing quality tests
3. **TypeScript Guidelines**: Jest-specific conventions
4. **Python Guidelines**: pytest-specific conventions
5. **React Guidelines**: Component testing best practices
6. **API Guidelines**: HTTP testing standards
7. **Coverage Guidelines**: Target coverage levels and exclusions
8. **Documentation Standards**: How to document tests
9. **CI/CD Integration**: GitHub Actions and coverage reporting
10. **Pre-commit Hooks**: Automated testing before commits
11. **Troubleshooting**: Common issues and solutions
12. **Maintenance**: Keeping tests healthy and fast
13. **Project-Specific Guidelines**: Tailored advice for each project
14. **Quick Reference**: Test templates for quick start

All projects should follow these guidelines to ensure:
- ✅ Consistent testing approach
- ✅ High code coverage
- ✅ Reliable, fast tests
- ✅ Clear documentation
- ✅ Automated CI/CD
- ✅ Pre-commit quality gates
