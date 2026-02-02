# v0-ai-agent-for-servers Testing Approach Review

## Overview

This document provides a comprehensive review of the testing approach for the v0-ai-agent-for-servers project.

---

## Components Covered

| Component | Type | Test Cases | Status |
|-----------|------|------------|--------|
| [`/api/health/route.ts`](../v0-ai-agent-for-servers/src/app/api/health/route.ts) | API Route | 6 | ✅ Complete |
| [`/api/cross-sync/route.ts`](../v0-ai-agent-for-servers/src/app/api/cross-sync/route.ts) | API Route | 17 | ✅ Complete |
| [`/api/unified-query/route.ts`](../v0-ai-agent-for-servers/src/app/api/unified-query/route.ts) | API Route | 19 | ✅ Complete |
| [`container-manager.tsx`](../v0-ai-agent-for-servers/src/components/container-manager.tsx) | React Component | 35 | ✅ Complete |
| [`terminal.tsx`](../v0-ai-agent-for-servers/src/components/terminal.tsx) | React Component | 11 | ✅ Complete |
| [`open-manus.tsx`](../v0-ai-agent-for-servers/src/components/open-manus.tsx) | React Component | 30 | ✅ Complete |

**Total**: 118 test cases across 6 components

---

# Part 1: API Routes Testing

## Component Overview

The v0-ai-agent-for-servers project has three Next.js API routes:
- [`/api/health/route.ts`](../v0-ai-agent-for-servers/src/app/api/health/route.ts) - Health check endpoint
- [`/api/cross-sync/route.ts`](../v0-ai-agent-for-servers/src/app/api/cross-sync/route.ts) - Cross-component state synchronization
- [`/api/unified-query/route.ts`](../v0-ai-agent-for-servers/src/app/api/unified-query/route.ts) - Unified query processing

## Testing Challenges

1. **Next.js App Router**: Testing Next.js 13+ app router routes
2. **Async Functions**: All route handlers are async
3. **Request/Response Objects**: Next.js specific `NextRequest` and `NextResponse`
4. **JSON Parsing**: Request body parsing and validation
5. **Error Handling**: Try-catch blocks with error responses
6. **Complex Logic**: cross-sync has nested async functions

## Testing Strategy

We'll use Jest with `@testing-library/react` and Next.js testing utilities:
- Mock `NextRequest` and `NextResponse`
- Test route handlers directly as functions
- Verify response status codes and JSON bodies
- Test error conditions and edge cases
- Mock external dependencies if needed

## Test File Structure

```
v0-ai-agent-for-servers/src/app/api/__tests__/
├── health.test.ts
├── cross-sync.test.ts
└── unified-query.test.ts
```

## Shared Test Utilities

### test-utils.ts

```typescript
import { NextRequest } from 'next/server';

/**
 * Create a mock NextRequest with JSON body
 */
export function createMockRequest(body: any, method: string = 'POST'): NextRequest {
  return {
    json: async () => body,
    method,
    headers: new Headers(),
    url: 'http://localhost:3000/api/test',
    clone: jest.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: jest.fn(),
    blob: jest.fn(),
    formData: jest.fn(),
    text: jest.fn(),
  } as unknown as NextRequest;
}

/**
 * Extract JSON from NextResponse
 */
export async function getResponseJson(response: Response): Promise<any> {
  return response.json();
}
```

---

## Test Suite 1: /api/health/route.ts (6 tests)

### Test 1.1: GET returns 200 status

```typescript
import { GET } from '../health/route';

describe('GET /api/health', () => {
  test('returns 200 status', async () => {
    const response = await GET();

    expect(response.status).toBe(200);
  });
});
```

### Test 1.2: GET returns component name

```typescript
test('returns component name', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.component).toBe('v0-ai-agent-for-servers');
});
```

### Test 1.3: GET returns online status

```typescript
test('returns online status', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.status).toBe('online');
});
```

### Test 1.4: GET returns timestamp

```typescript
test('returns timestamp', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.timestamp).toBeDefined();
  expect(typeof data.timestamp).toBe('string');
  expect(new Date(data.timestamp).toISOString()).toBe(data.timestamp);
});
```

### Test 1.5: GET returns version

```typescript
test('returns version', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.version).toBe('1.0.0');
});
```

### Test 1.6: GET returns endpoints list

```typescript
test('returns endpoints list', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.endpoints).toBeDefined();
  expect(Array.isArray(data.endpoints)).toBe(true);
  expect(data.endpoints).toContain('/api/health');
  expect(data.endpoints).toContain('/api/execute');
  expect(data.endpoints).toContain('/api/containers');
  expect(data.endpoints).toContain('/api/terminal');
  expect(data.endpoints).toContain('/api/unified-query');
  expect(data.endpoints).toContain('/api/cross-sync');
});
```

---

## Test Suite 2: /api/cross-sync/route.ts (17 tests)

### Test 2.1: POST returns 200 on success

```typescript
import { POST } from '../cross-sync/route';
import { createMockRequest } from './test-utils';

describe('POST /api/cross-sync', () => {
  test('returns 200 on success', async () => {
    const request = createMockRequest({
      unified_state: {},
      component_states: {},
      sync_type: 'standard'
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
  });
});
```

### Test 2.2: POST returns component name

```typescript
test('returns component name', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.component).toBe('v0-ai-agent-for-servers');
});
```

### Test 2.3: POST returns synced status

```typescript
test('returns synced status', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.status).toBe('synced');
});
```

### Test 2.4: POST returns timestamp

```typescript
test('returns timestamp', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.timestamp).toBeDefined();
  expect(typeof data.timestamp).toBe('string');
});
```

### Test 2.5: POST returns sync_result

```typescript
test('returns sync_result', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.sync_result).toBeDefined();
  expect(typeof data.sync_result).toBe('object');
});
```

### Test 2.6: POST returns success message

```typescript
test('returns success message', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.message).toBe('State synchronization completed successfully');
});
```

### Test 2.7: POST processes unified_state parameter

```typescript
test('processes unified_state parameter', async () => {
  const request = createMockRequest({
    unified_state: {
      trainllm: { status: 'online' },
      docs: { status: 'online' }
    },
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.sync_result).toBeDefined();
});
```

### Test 2.8: POST processes component_states parameter

```typescript
test('processes component_states parameter', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {
      trainllm: {
        epoch: 42,
        universes: {
          U1: {
            civilizations: {
              civ1: {
                attention: 100,
                compute: 100
              }
            }
          }
        }
      }
    },
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.sync_result.processed_components).toContain('trainllm');
});
```

### Test 2.9: POST processes sync_type parameter

```typescript
test('processes sync_type parameter', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {},
    sync_type: 'priority'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.sync_result).toBeDefined();
});
```

### Test 2.10: POST handles missing unified_state

```typescript
test('handles missing unified_state', async () => {
  const request = createMockRequest({
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.sync_result).toBeDefined();
});
```

### Test 2.11: POST handles missing component_states

```typescript
test('handles missing component_states', async () => {
  const request = createMockRequest({
    unified_state: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.sync_result).toBeDefined();
});
```

### Test 2.12: POST handles missing sync_type

```typescript
test('handles missing sync_type', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {}
  });

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.sync_result).toBeDefined();
});
```

### Test 2.13: POST processes TrainLLM state updates

```typescript
test('processes TrainLLM state updates', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {
      trainllm: {
        epoch: 42,
        universes: {
          U1: {
            civilizations: {
              civ1: {
                attention: 100,
                compute: 100
              }
            }
          }
        }
      }
    },
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.sync_result.processed_components).toContain('trainllm');
  expect(data.sync_result.state_updates).toBeDefined();
  expect(Array.isArray(data.sync_result.state_updates)).toBe(true);
});
```

### Test 2.14: POST generates resource alerts for low resources

```typescript
test('generates resource alerts for low resources', async () => {
  const request = createMockRequest({
    unified_state: {},
    component_states: {
      trainllm: {
        epoch: 42,
        universes: {
          U1: {
            civilizations: {
              civ1: {
                attention: 10,  // Below threshold
                compute: 10     // Below threshold
              }
            }
          }
        }
      }
    },
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  const resourceAlerts = data.sync_result.state_updates.filter(
    (update: any) => update.type === 'resource_alert'
  );

  expect(resourceAlerts.length).toBeGreaterThan(0);
  expect(resourceAlerts[0].alert).toBe('critical_resources');
});
```

### Test 2.15: POST generates health monitoring recommendations

```typescript
test('generates health monitoring recommendations', async () => {
  const request = createMockRequest({
    unified_state: {
      trainllm: { status: 'offline' },
      docs: { status: 'online' }
    },
    component_states: {},
    sync_type: 'standard'
  });

  const response = await POST(request);
  const data = await response.json();

  const healthRecs = data.sync_result.recommendations.filter(
    (rec: any) => rec.type === 'health_monitoring'
  );

  expect(healthRecs.length).toBeGreaterThan(0);
  expect(healthRecs[0].priority).toBe('high');
});
```

### Test 2.16: POST handles empty request body

```typescript
test('handles empty request body', async () => {
  const request = createMockRequest({});

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.sync_result).toBeDefined();
});
```

### Test 2.17: POST handles invalid JSON

```typescript
test('handles invalid JSON', async () => {
  const request = {
    json: async () => {
      throw new Error('Invalid JSON');
    },
    method: 'POST',
    headers: new Headers(),
    url: 'http://localhost:3000/api/cross-sync',
  } as unknown as NextRequest;

  const response = await POST(request);

  expect(response.status).toBe(400);
  const data = await response.json();
  expect(data.error).toBeDefined();
});
```

---

## Test Suite 3: /api/unified-query/route.ts (19 tests)

### Test 3.1: POST returns 200 on success

```typescript
import { POST } from '../unified-query/route';
import { createMockRequest } from './test-utils';

describe('POST /api/unified-query', () => {
  test('returns 200 on success', async () => {
    const request = createMockRequest({
      query: 'test query'
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
  });
});
```

### Test 3.2: POST returns component name

```typescript
test('returns component name', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.component).toBe('v0-ai-agent-for-servers');
});
```

### Test 3.3: POST returns processed status

```typescript
test('returns processed status', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.status).toBe('processed');
});
```

### Test 3.4: POST returns timestamp

```typescript
test('returns timestamp', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.timestamp).toBeDefined();
  expect(typeof data.timestamp).toBe('string');
});
```

### Test 3.5: POST returns query_result

```typescript
test('returns query_result', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result).toBeDefined();
  expect(typeof data.query_result).toBe('object');
});
```

### Test 3.6: POST processes query parameter

```typescript
test('processes query parameter', async () => {
  const request = createMockRequest({
    query: 'What is the current epoch?'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result).toBeDefined();
});
```

### Test 3.7: POST handles missing query parameter

```typescript
test('handles missing query parameter', async () => {
  const request = createMockRequest({});

  const response = await POST(request);

  expect(response.status).toBe(400);
  const data = await response.json();
  expect(data.error).toBeDefined();
});
```

### Test 3.8: POST handles empty query

```typescript
test('handles empty query', async () => {
  const request = createMockRequest({
    query: ''
  });

  const response = await POST(request);

  expect(response.status).toBe(400);
  const data = await response.json();
  expect(data.error).toBeDefined();
});
```

### Test 3.9: POST handles very long query

```typescript
test('handles very long query', async () => {
  const longQuery = 'A'.repeat(10000);

  const request = createMockRequest({
    query: longQuery
  });

  const response = await POST(request);

  expect(response.status).toBe(200);
  const data = await response.json();
  expect(data.query_result).toBeDefined();
});
```

### Test 3.10: POST handles special characters in query

```typescript
test('handles special characters in query', async () => {
  const specialQuery = 'Hello @#$%^&*() World!';

  const request = createMockRequest({
    query: specialQuery
  });

  const response = await POST(request);

  expect(response.status).toBe(200);
  const data = await response.json();
  expect(data.query_result).toBeDefined();
});
```

### Test 3.11: POST handles Unicode in query

```typescript
test('handles Unicode in query', async () => {
  const unicodeQuery = 'Hello 世界 🌍';

  const request = createMockRequest({
    query: unicodeQuery
  });

  const response = await POST(request);

  expect(response.status).toBe(200);
  const data = await response.json();
  expect(data.query_result).toBeDefined();
});
```

### Test 3.12: POST includes context in result

```typescript
test('includes context in result', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {
      trainllm: { epoch: 42 }
    }
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result).toBeDefined();
});
```

### Test 3.13: POST handles missing context

```typescript
test('handles missing context', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result).toBeDefined();
});
```

### Test 3.14: POST returns analysis

```typescript
test('returns analysis', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result.analysis).toBeDefined();
  expect(typeof data.query_result.analysis).toBe('string');
});
```

### Test 3.15: POST returns recommendations

```typescript
test('returns recommendations', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result.recommendations).toBeDefined();
  expect(Array.isArray(data.query_result.recommendations)).toBe(true);
});
```

### Test 3.16: POST returns actions

```typescript
test('returns actions', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query_result.actions).toBeDefined();
  expect(Array.isArray(data.query_result.actions)).toBe(true);
});
```

### Test 3.17: POST handles invalid JSON

```typescript
test('handles invalid JSON', async () => {
  const request = {
    json: async () => {
      throw new Error('Invalid JSON');
    },
    method: 'POST',
    headers: new Headers(),
    url: 'http://localhost:3000/api/unified-query',
  } as unknown as NextRequest;

  const response = await POST(request);

  expect(response.status).toBe(400);
  const data = await response.json();
  expect(data.error).toBeDefined();
});
```

### Test 3.18: POST handles processing errors

```typescript
test('handles processing errors', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  // Mock processing error
  jest.spyOn(global, 'Date').mockImplementation(() => {
    throw new Error('Processing error');
  });

  const response = await POST(request);

  expect(response.status).toBe(500);
  const data = await response.json();
  expect(data.error).toBeDefined();

  jest.restoreAllMocks();
});
```

### Test 3.19: POST returns success message

```typescript
test('returns success message', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.message).toBe('Query processed successfully');
});
```

---

# Part 2: React Components Testing

## Component Overview

### container-manager.tsx

[`container-manager.tsx`](../v0-ai-agent-for-servers/src/components/container-manager.tsx) is a React component that:
- Fetches and displays containers from TrainLLM backend
- Creates new containers via API
- Handles loading states
- Displays container information (name, status, description, compute tokens)
- Handles API errors with fallback behavior

### terminal.tsx

[`terminal.tsx`](../v0-ai-agent-for-servers/src/components/terminal.tsx) is a React component that wraps xterm.js terminal emulator:
- Initializes xterm with custom theme
- Loads FitAddon and WebLinksAddon
- Displays welcome message and prompt
- Handles user input (characters, backspace, enter)
- Cleans up on unmount

### open-manus.tsx

[`open-manus.tsx`](../v0-ai-agent-for-servers/src/components/open-manus.tsx) is a React component for building applications via AI:
- Input field for app requirements
- "Build App" button with loading state
- Displays built applications list
- Calls TrainLLM chat endpoint
- Handles API errors with fallback

## Testing Challenges

### container-manager.tsx
1. **API Calls**: Component makes HTTP requests to external backend
2. **Async Operations**: `fetchContainers` and `createContainer` are async
3. **State Management**: Multiple state variables (containers, isLoading)
4. **Side Effects**: `useEffect` hook for initial fetch
5. **Error Handling**: Fallback behavior when backend is offline
6. **User Interactions**: Button clicks trigger API calls
7. **Date Formatting**: Displays formatted creation dates

### terminal.tsx
1. **Third-Party Library**: xterm.js is a complex library
2. **DOM Manipulation**: xterm directly manipulates DOM
3. **Refs**: Uses `useRef` for terminal instance
4. **Event Handlers**: Terminal input handling
5. **Cleanup**: Proper disposal on unmount
6. **Theme**: Custom theme colors using CSS variables

### open-manus.tsx
1. **API Calls**: Makes HTTP requests to TrainLLM backend
2. **Async Operations**: `buildApp` is async
3. **State Management**: Multiple state variables
4. **Loading States**: Button disabled during API call
5. **Error Handling**: Fallback behavior when backend is offline
6. **User Input**: Form input and button interactions

## Testing Strategy

We'll use React Testing Library (`@testing-library/react`) with Jest:
- **container-manager.tsx**: Mock `fetch` API to avoid real HTTP requests
- **terminal.tsx**: Mock xterm.js to avoid DOM manipulation
- **open-manus.tsx**: Mock `fetch` API for API calls
- Test component rendering and user interactions
- Verify state changes and side effects
- Test error handling and fallback behavior
- Mock `Date` for consistent date formatting

## Test File Structure

```
v0-ai-agent-for-servers/src/components/__tests__/
├── container-manager.test.tsx
├── terminal.test.tsx
└── open-manus.test.tsx
```

---

## Test Suite 4: container-manager.tsx (35 tests)

### Test Suite 4.1: Component Rendering (4 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Renders without errors | Basic rendering | Component renders without throwing |
| Displays "No containers running" when empty | Empty state | Empty message displayed |
| Displays "Create New Container" button | Button rendering | Button present |
| Displays "Refresh" button | Button rendering | Button present |

### Test Suite 4.2: Container Fetching (8 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Fetches containers on mount | useEffect hook | Fetch called on mount |
| Displays fetched containers | Data display | Containers displayed |
| Displays container name | Data display | Name displayed |
| Displays container status | Data display | Status displayed |
| Displays container description | Data display | Description displayed |
| Displays container creation date | Data display | Date displayed |
| Displays compute tokens when available | Data display | Compute tokens displayed |
| Handles missing compute tokens | Data display | Compute tokens not displayed |

### Test Suite 4.3: Container Creation (9 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| "Create New Container" button triggers creation | User interaction | API call made |
| "Create New Container" button shows loading state | Loading state | "Creating..." displayed |
| "Create New Container" button is disabled during loading | Loading state | Button disabled |
| "Create New Container" sends correct request body | API request | Correct body sent |
| "Create New Container" adds new container to list | State update | New container displayed |
| "Create New Container" handles API errors gracefully | Error handling | Fallback container created |
| "Create New Container" creates fallback container on error | Error handling | Fallback structure correct |
| "Create New Container" fallback has correct structure | Error handling | Fallback data correct |
| "Create New Container" clears loading state after error | Loading state | Loading cleared |

### Test Suite 4.4: Refresh Functionality (4 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| "Refresh" button triggers container fetch | User interaction | Fetch called |
| "Refresh" button shows loading state | Loading state | "Refreshing..." displayed |
| "Refresh" button is disabled during loading | Loading state | Button disabled |
| "Refresh" updates container list | State update | List updated |

### Test Suite 4.5: Error Handling (6 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Handles fetch errors gracefully | Error handling | Fallback containers displayed |
| Handles create errors gracefully | Error handling | Fallback container created |
| Displays error message on fetch error | Error display | Error message shown |
| Displays error message on create error | Error display | Error message shown |
| Recovers from fetch errors | Error recovery | Retry works |
| Recovers from create errors | Error recovery | Retry works |

### Test Suite 4.6: Edge Cases (4 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Handles empty container list | Empty state | Empty message displayed |
| Handles single container | Single item | Container displayed |
| Handles many containers | Multiple items | All containers displayed |
| Handles container with missing fields | Missing data | Graceful handling |

---

## Test Suite 5: terminal.tsx (11 tests)

### Test Suite 5.1: Component Rendering (2 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Renders without errors | Basic rendering | Component renders without throwing |
| Renders container div | DOM structure | Container div present |

### Test Suite 5.2: Terminal Initialization (5 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Initializes Terminal with correct options | Initialization | Options correct |
| Initializes FitAddon | Initialization | FitAddon initialized |
| Initializes WebLinksAddon | Initialization | WebLinksAddon initialized |
| Loads FitAddon to terminal | Initialization | Addon loaded |
| Loads WebLinksAddon to terminal | Initialization | Addon loaded |

### Test Suite 5.3: Terminal Display (4 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Opens terminal in container | Display | Terminal opened |
| Fits terminal to container | Display | Terminal fitted |
| Displays welcome message | Display | Welcome message shown |
| Displays prompt | Display | Prompt shown |

### Test Suite 5.4: Input Handling (5 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Registers onData handler | Event handling | Handler registered |
| Handles character input | Input handling | Character displayed |
| Handles backspace | Input handling | Backspace handled |
| Handles enter key | Input handling | Enter handled |
| Ignores other characters | Input handling | Other chars ignored |

### Test Suite 5.5: Cleanup (1 test)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Disposes terminal on unmount | Cleanup | Terminal disposed |

---

## Test Suite 6: open-manus.tsx (30 tests)

### Test Suite 6.1: Component Rendering (7 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Renders without errors | Basic rendering | Component renders without throwing |
| Displays header with icon | Header rendering | Header displayed |
| Displays description | Description rendering | Description displayed |
| Displays input field | Input rendering | Input field present |
| Displays "Build App" button | Button rendering | Button present |
| Displays "Simulation Infrastructure" section | Section rendering | Section displayed |
| Displays "No applications deployed" when empty | Empty state | Empty message displayed |

### Test Suite 6.2: App Building (8 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| "Build App" button triggers build | User interaction | API call made |
| "Build App" button shows loading state | Loading state | "Building..." displayed |
| "Build App" button is disabled during loading | Loading state | Button disabled |
| "Build App" sends correct request body | API request | Correct body sent |
| "Build App" adds new app to list | State update | New app displayed |
| "Build App" handles API errors gracefully | Error handling | Fallback app created |
| "Build App" creates fallback app on error | Error handling | Fallback structure correct |
| "Build App" clears loading state after error | Loading state | Loading cleared |

### Test Suite 6.3: App Display (6 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Displays app name | Data display | Name displayed |
| Displays app status | Data display | Status displayed |
| Displays app compute tokens | Data display | Compute tokens displayed |
| Displays app description | Data display | Description displayed |
| Handles missing compute tokens | Data display | Compute tokens not displayed |
| Handles missing description | Data display | Description not displayed |

### Test Suite 6.4: Input Handling (4 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Accepts text input | Input handling | Text accepted |
| Handles empty input | Input handling | Empty input handled |
| Handles very long input | Input handling | Long input handled |
| Handles special characters in input | Input handling | Special chars handled |

### Test Suite 6.5: Error Handling (3 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Handles build errors gracefully | Error handling | Fallback app created |
| Displays error message on build error | Error display | Error message shown |
| Recovers from build errors | Error recovery | Retry works |

### Test Suite 6.6: Edge Cases (2 tests)

| Test | Purpose | Key Assertion |
|------|---------|---------------|
| Handles empty app list | Empty state | Empty message displayed |
| Handles many apps | Multiple items | All apps displayed |

---

## Common Testing Patterns

### Pattern 1: Mocking NextRequest

```typescript
export function createMockRequest(body: any, method: string = 'POST'): NextRequest {
  return {
    json: async () => body,
    method,
    headers: new Headers(),
    url: 'http://localhost:3000/api/test',
    clone: jest.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: jest.fn(),
    blob: jest.fn(),
    formData: jest.fn(),
    text: jest.fn(),
  } as unknown as NextRequest;
}
```

### Pattern 2: Mocking fetch API

```typescript
global.fetch = jest.fn();

function mockFetchSuccess(data: any) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  } as Response);
}

function mockFetchError() {
  (global.fetch as jest.Mock).mockRejectedValueOnce(
    new Error('Network error')
  );
}
```

### Pattern 3: Mocking xterm.js

```typescript
jest.mock('xterm', () => {
  return {
    Terminal: jest.fn().mockImplementation(() => ({
      open: jest.fn(),
      loadAddon: jest.fn(),
      write: jest.fn(),
      writeln: jest.fn(),
      onData: jest.fn(),
      dispose: jest.fn(),
    })),
  };
});
```

### Pattern 4: Testing React Components

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('component renders', () => {
  render(<Component />);

  expect(screen.getByText('text')).toBeInTheDocument();
});

test('handles user interaction', async () => {
  render(<Component />);

  const button = screen.getByText('Button');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Result')).toBeInTheDocument();
  });
});
```

### Pattern 5: Testing API Routes

```typescript
import { GET, POST } from '../route';
import { createMockRequest } from './test-utils';

test('API route works', async () => {
  const request = createMockRequest({ data: 'test' });

  const response = await POST(request);

  expect(response.status).toBe(200);
  const data = await response.json();
  expect(data.result).toBe('test');
});
```

---

## Running Tests

```bash
cd v0-ai-agent-for-servers

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test api/__tests__/health.test.ts

# Run specific test suite
npm test -- --testNamePattern="GET /api/health"

# Run with verbose output
npm test -- --verbose

# Run in watch mode
npm test -- --watch
```

---

## Coverage Goals

| Metric | Target |
|--------|--------|
| Statements | 80% |
| Branches | 75% |
| Functions | 80% |
| Lines | 80% |

---

## Implementation Checklist

### API Routes
- [ ] Create `v0-ai-agent-for-servers/src/app/api/__tests__/health.test.ts`
- [ ] Create `v0-ai-agent-for-servers/src/app/api/__tests__/cross-sync.test.ts`
- [ ] Create `v0-ai-agent-for-servers/src/app/api/__tests__/unified-query.test.ts`
- [ ] Create `v0-ai-agent-for-servers/src/app/api/__tests__/test-utils.ts`

### React Components
- [ ] Create `v0-ai-agent-for-servers/src/components/__tests__/container-manager.test.tsx`
- [ ] Create `v0-ai-agent-for-servers/src/components/__tests__/terminal.test.tsx`
- [ ] Create `v0-ai-agent-for-servers/src/components/__tests__/open-manus.test.tsx`

### Configuration
- [ ] Create `v0-ai-agent-for-servers/jest.config.js`
- [ ] Create `v0-ai-agent-for-servers/jest.setup.js`
- [ ] Update `v0-ai-agent-for-servers/package.json` with test scripts

### Testing
- [ ] Run tests and verify all pass
- [ ] Generate coverage report
- [ ] Verify coverage meets 80% goal
- [ ] Update `v0-ai-agent-for-servers/README.md` with testing instructions

---

## Notes

- All API route tests use mock `NextRequest` objects
- All React component tests use React Testing Library
- `fetch` API is mocked globally to avoid real HTTP requests
- xterm.js is mocked to avoid DOM manipulation
- Tests are isolated with `beforeEach` hooks
- Mocks are reset between tests to prevent interference
- Edge cases are thoroughly tested (empty, long, special characters, Unicode)
- Error handling is tested with fallback behavior
- Loading states are tested for user feedback
- Integration tests verify end-to-end workflows

**Status**: ✅ Testing Approach Complete - Ready for Implementation
