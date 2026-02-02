# Detailed Testing Approach: container-manager.tsx

## Component Overview

[`container-manager.tsx`](../v0-ai-agent-for-servers/src/components/container-manager.tsx) is a React component that:
- Fetches and displays containers from TrainLLM backend
- Creates new containers via API
- Handles loading states
- Displays container information (name, status, description, compute tokens)
- Handles API errors with fallback behavior

## Testing Challenges

1. **API Calls**: Component makes HTTP requests to external backend
2. **Async Operations**: `fetchContainers` and `createContainer` are async
3. **State Management**: Multiple state variables (containers, isLoading)
4. **Side Effects**: `useEffect` hook for initial fetch
5. **Error Handling**: Fallback behavior when backend is offline
6. **User Interactions**: Button clicks trigger API calls
7. **Date Formatting**: Displays formatted creation dates

## Testing Strategy

### Testing Approach

We'll use React Testing Library (`@testing-library/react`) with Jest:
- Mock `fetch` API to avoid real HTTP requests
- Test component rendering and user interactions
- Verify state changes and side effects
- Test error handling and fallback behavior
- Mock `Date` for consistent date formatting

### Test File Structure

```
v0-ai-agent-for-servers/src/components/__tests__/
└── container-manager.test.tsx
```

## Test Setup

### Imports and Mocks

```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContainerManager } from '../container-manager';

// Mock fetch globally
global.fetch = jest.fn();
```

### Helper Functions

```typescript
/**
 * Create mock container data
 */
function createMockContainer(overrides = {}) {
  return {
    id: 'test-container-1',
    name: 'Test Container',
    status: 'running',
    createdAt: '2024-01-18T10:00:00Z',
    compute: '250 CK-Tokens',
    description: 'Test description',
    ...overrides
  };
}

/**
 * Mock successful fetch response
 */
function mockFetchSuccess(data: any) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  } as Response);
}

/**
 * Mock failed fetch response
 */
function mockFetchError() {
  (global.fetch as jest.Mock).mockRejectedValueOnce(
    new Error('Network error')
  );
}
```

## Detailed Test Cases

### Test Suite 1: Component Rendering

#### Test 1.1: Component renders without errors

```typescript
describe('ContainerManager', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without errors', () => {
    render(<ContainerManager />);

    // Component should render without throwing
    expect(screen.getByText('Create New Container')).toBeInTheDocument();
  });
});
```

#### Test 1.2: Component displays "No containers running" when empty

```typescript
test('displays "No containers running" when empty', async () => {
  mockFetchSuccess([]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText(/No containers running/)).toBeInTheDocument();
  });
});
```

#### Test 1.3: Component displays "Create New Container" button

```typescript
test('displays "Create New Container" button', () => {
  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  expect(button).toBeInTheDocument();
  expect(button.tagName).toBe('BUTTON');
});
```

#### Test 1.4: Component displays "Refresh" button

```typescript
test('displays "Refresh" button', () => {
  render(<ContainerManager />);

  const button = screen.getByText('Refresh');
  expect(button).toBeInTheDocument();
  expect(button.tagName).toBe('BUTTON');
});
```

### Test Suite 2: Container Fetching

#### Test 2.1: Component fetches containers on mount

```typescript
test('fetches containers on mount', async () => {
  const mockContainers = [createMockContainer()];
  mockFetchSuccess(mockContainers);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/containers'
    );
  });
});
```

#### Test 2.2: Component displays fetched containers

```typescript
test('displays fetched containers', async () => {
  const mockContainers = [
    createMockContainer({ id: 'container-1', name: 'Container 1' }),
    createMockContainer({ id: 'container-2', name: 'Container 2' }),
  ];
  mockFetchSuccess(mockContainers);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('Container 1')).toBeInTheDocument();
    expect(screen.getByText('Container 2')).toBeInTheDocument();
  });
});
```

#### Test 2.3: Component displays container name

```typescript
test('displays container name', async () => {
  const mockContainer = createMockContainer({ name: 'My Test Container' });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('My Test Container')).toBeInTheDocument();
  });
});
```

#### Test 2.4: Component displays container status

```typescript
test('displays container status', async () => {
  const mockContainer = createMockContainer({ status: 'running' });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText(/status: running/i)).toBeInTheDocument();
  });
});
```

#### Test 2.5: Component displays container description

```typescript
test('displays container description', async () => {
  const mockContainer = createMockContainer({
    description: 'This is a test container'
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('This is a test container')).toBeInTheDocument();
  });
});
```

#### Test 2.6: Component displays container creation date

```typescript
test('displays container creation date', async () => {
  const mockContainer = createMockContainer({
    createdAt: '2024-01-18T10:00:00Z'
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText(/created:/i)).toBeInTheDocument();
  });
});
```

#### Test 2.7: Component displays compute tokens when available

```typescript
test('displays compute tokens when available', async () => {
  const mockContainer = createMockContainer({
    compute: '250 CK-Tokens'
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('250 CK-Tokens')).toBeInTheDocument();
  });
});
```

#### Test 2.8: Component handles missing compute tokens

```typescript
test('handles missing compute tokens', async () => {
  const mockContainer = createMockContainer({
    compute: undefined
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    // Should not display compute tokens
    const computeElement = screen.queryByText(/CK-Tokens/);
    expect(computeElement).not.toBeInTheDocument();
  });
});
```

### Test Suite 3: Container Creation

#### Test 3.1: "Create New Container" button triggers creation

```typescript
test('"Create New Container" button triggers creation', async () => {
  mockFetchSuccess([]);

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/containers',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });
});
```

#### Test 3.2: "Create New Container" button shows loading state

```typescript
test('"Create New Container" button shows loading state', async () => {
  // Mock fetch that never resolves
  (global.fetch as jest.Mock).mockImplementation(
    () => new Promise(() => {})
  );

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Creating...')).toBeInTheDocument();
  });
});
```

#### Test 3.3: "Create New Container" button is disabled during loading

```typescript
test('"Create New Container" button is disabled during loading', async () => {
  // Mock fetch that never resolves
  (global.fetch as jest.Mock).mockImplementation(
    () => new Promise(() => {})
  );

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(button).toBeDisabled();
  });
});
```

#### Test 3.4: "Create New Container" sends correct request body

```typescript
test('"Create New Container" sends correct request body', async () => {
  mockFetchSuccess({ id: 'new-container' });

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    const callArgs = (global.fetch as jest.Mock).mock.calls[1];
    const requestBody = JSON.parse(callArgs[1].body);

    expect(requestBody.requirement).toBe(
      'New autonomous container for multi-universe simulation'
    );
  });
});
```

#### Test 3.5: "Create New Container" adds new container to list

```typescript
test('"Create New Container" adds new container to list', async () => {
  const existingContainer = createMockContainer({ id: 'existing-1' });
  const newContainer = createMockContainer({ id: 'new-1', name: 'New Container' });

  // First call: fetch existing containers
  mockFetchSuccess([existingContainer]);
  // Second call: create container
  mockFetchSuccess(newContainer);

  render(<ContainerManager />);

  // Wait for initial fetch
  await waitFor(() => {
    expect(screen.getByText('existing-1')).toBeInTheDocument();
  });

  // Create new container
  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  // Wait for new container to appear
  await waitFor(() => {
    expect(screen.getByText('New Container')).toBeInTheDocument();
  });
});
```

#### Test 3.6: "Create New Container" handles API errors gracefully

```typescript
test('"Create New Container" handles API errors gracefully', async () => {
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  // Should create fallback container
  await waitFor(() => {
    const fallbackContainers = screen.getAllByText(/Fallback:/i);
    expect(fallbackContainers.length).toBeGreaterThan(0);
  });
});
```

#### Test 3.7: "Create New Container" creates fallback container on error

```typescript
test('"Create New Container" creates fallback container on error', async () => {
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(/Fallback: Local container/)).toBeInTheDocument();
  });
});
```

#### Test 3.8: "Create New Container" fallback has correct structure

```typescript
test('"Create New Container" fallback has correct structure', async () => {
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(/100 CK-Tokens/)).toBeInTheDocument();
    expect(screen.getByText(/TrainLLM backend offline/)).toBeInTheDocument();
  });
});
```

#### Test 3.9: "Create New Container" clears loading state after error

```typescript
test('"Create New Container" clears loading state after error', async () => {
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  // Wait for loading state
  await waitFor(() => {
    expect(screen.getByText('Creating...')).toBeInTheDocument();
  });

  // Wait for loading to clear
  await waitFor(() => {
    expect(screen.queryByText('Creating...')).not.toBeInTheDocument();
  });
});
```

### Test Suite 4: Refresh Functionality

#### Test 4.1: "Refresh" button triggers container fetch

```typescript
test('"Refresh" button triggers container fetch', async () => {
  const mockContainers = [createMockContainer()];
  mockFetchSuccess(mockContainers);

  render(<ContainerManager />);

  // Wait for initial fetch
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  const button = screen.getByText('Refresh');
  await userEvent.click(button);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});
```

#### Test 4.2: "Refresh" button updates container list

```typescript
test('"Refresh" button updates container list', async () => {
  const initialContainers = [createMockContainer({ id: 'container-1' })];
  const updatedContainers = [
    createMockContainer({ id: 'container-1' }),
    createMockContainer({ id: 'container-2', name: 'New Container' }),
  ];

  // First call: initial containers
  mockFetchSuccess(initialContainers);

  render(<ContainerManager />);

  // Wait for initial fetch
  await waitFor(() => {
    expect(screen.getByText('container-1')).toBeInTheDocument();
  });

  // Second call: updated containers
  mockFetchSuccess(updatedContainers);

  const button = screen.getByText('Refresh');
  await userEvent.click(button);

  // Wait for updated list
  await waitFor(() => {
    expect(screen.getByText('New Container')).toBeInTheDocument();
  });
});
```

#### Test 4.3: "Refresh" button handles errors gracefully

```typescript
test('"Refresh" button handles errors gracefully', async () => {
  // First call: initial containers
  mockFetchSuccess([createMockContainer()]);

  render(<ContainerManager />);

  // Wait for initial fetch
  await waitFor(() => {
    expect(screen.getByText(/container/i)).toBeInTheDocument();
  });

  // Second call: refresh fails
  mockFetchError();

  const button = screen.getByText('Refresh');
  await userEvent.click(button);

  // Should show empty list (fallback behavior)
  await waitFor(() => {
    expect(screen.getByText(/No containers running/)).toBeInTheDocument();
  });
});
```

### Test Suite 5: Error Handling

#### Test 5.1: Component handles fetch errors on mount

```typescript
test('handles fetch errors on mount', async () => {
  mockFetchError();

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText(/No containers running/)).toBeInTheDocument();
  });
});
```

#### Test 5.2: Component logs fetch errors to console

```typescript
test('logs fetch errors to console', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
  mockFetchError();

  render(<ContainerManager />);

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to fetch containers')
    );
  });

  consoleSpy.mockRestore();
});
```

#### Test 5.3: Component handles create errors gracefully

```typescript
test('handles create errors gracefully', async () => {
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  // Should create fallback container
  await waitFor(() => {
    expect(screen.getByText(/Fallback:/i)).toBeInTheDocument();
  });
});
```

#### Test 5.4: Component logs create errors to console

```typescript
test('logs create errors to console', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
  // First call: fetch existing containers
  mockFetchSuccess([]);
  // Second call: create container fails
  mockFetchError();

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');
  await userEvent.click(button);

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to create container')
    );
  });

  consoleSpy.mockRestore();
});
```

### Test Suite 6: Edge Cases

#### Test 6.1: Component handles empty container list

```typescript
test('handles empty container list', async () => {
  mockFetchSuccess([]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText(/No containers running/)).toBeInTheDocument();
  });
});
```

#### Test 6.2: Component handles large container list

```typescript
test('handles large container list', async () => {
  const mockContainers = Array.from({ length: 50 }, (_, i) =>
    createMockContainer({ id: `container-${i}`, name: `Container ${i}` })
  );
  mockFetchSuccess(mockContainers);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('Container 0')).toBeInTheDocument();
    expect(screen.getByText('Container 49')).toBeInTheDocument();
  });
});
```

#### Test 6.3: Component handles container with missing fields

```typescript
test('handles container with missing fields', async () => {
  const mockContainer = {
    id: 'container-1',
    name: 'Minimal Container',
    status: 'running',
    createdAt: '2024-01-18T10:00:00Z',
    // Missing: compute, description
  };
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('Minimal Container')).toBeInTheDocument();
    expect(screen.getByText(/status: running/i)).toBeInTheDocument();
  });
});
```

#### Test 6.4: Component handles container with null values

```typescript
test('handles container with null values', async () => {
  const mockContainer = createMockContainer({
    description: null,
    compute: null,
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    expect(screen.getByText('Test Container')).toBeInTheDocument();
    // Should not display null values
    expect(screen.queryByText('null')).not.toBeInTheDocument();
  });
});
```

#### Test 6.5: Component handles rapid button clicks

```typescript
test('handles rapid button clicks', async () => {
  mockFetchSuccess([]);

  render(<ContainerManager />);

  const button = screen.getByText('Create New Container');

  // Click multiple times rapidly
  await userEvent.click(button);
  await userEvent.click(button);
  await userEvent.click(button);

  // Should only make one request (button disabled during loading)
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(2); // 1 initial fetch + 1 create
  });
});
```

### Test Suite 7: Accessibility

#### Test 7.1: Component has accessible button labels

```typescript
test('has accessible button labels', () => {
  render(<ContainerManager />);

  const createButton = screen.getByRole('button', { name: /create new container/i });
  const refreshButton = screen.getByRole('button', { name: /refresh/i });

  expect(createButton).toBeInTheDocument();
  expect(refreshButton).toBeInTheDocument();
});
```

#### Test 7.2: Component displays container information in accessible format

```typescript
test('displays container information in accessible format', async () => {
  const mockContainer = createMockContainer({
    name: 'Accessible Container',
    status: 'running',
  });
  mockFetchSuccess([mockContainer]);

  render(<ContainerManager />);

  await waitFor(() => {
    const containerElement = screen.getByText('Accessible Container');
    expect(containerElement).toBeInTheDocument();
  });
});
```

## Test Configuration

### jest.config.js (same as API routes)

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

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
}

module.exports = createJestConfig(customJestConfig)
```

## Running Tests

```bash
# Run all component tests
npm test container-manager.test.tsx

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test
npm test -t "displays container name"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

1. **User-Centric**: Test from user's perspective (what they see and do)
2. **No Implementation Details**: Don't test internal state, test rendered output
3. **Async Handling**: Properly wait for async operations with `waitFor`
4. **Mocking**: Mock `fetch` to avoid real HTTP requests
5. **Error Testing**: Test both success and error paths
6. **Edge Cases**: Test empty lists, large lists, missing fields
7. **Accessibility**: Verify accessible labels and structure
8. **Isolation**: Each test is independent with proper cleanup
9. **Descriptive Names**: Test names clearly describe behavior
10. **AAA Pattern**: Arrange, Act, Assert structure

## Notes

- `fetch` is mocked globally to avoid real HTTP requests
- `userEvent` is used instead of `fireEvent` for more realistic user interactions
- `waitFor` is used to handle async operations and state updates
- Tests verify what users see, not internal implementation details
- Error handling is tested with fallback behavior
- Loading states are tested to ensure good UX
- Accessibility is verified with role-based queries
- Date formatting is tested but exact format may vary by locale
- Rapid button clicks are tested to prevent duplicate requests
