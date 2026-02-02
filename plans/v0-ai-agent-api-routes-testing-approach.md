# Detailed Testing Approach: v0-ai-agent-for-servers API Routes

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

### Testing Approach

We'll use Jest with `@testing-library/react` and Next.js testing utilities:
- Mock `NextRequest` and `NextResponse`
- Test route handlers directly as functions
- Verify response status codes and JSON bodies
- Test error conditions and edge cases
- Mock external dependencies if needed

### Test File Structure

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

## Detailed Test Cases

### Test Suite 1: /api/health/route.ts

#### Test 1.1: GET returns 200 status

```typescript
import { GET } from '../health/route';

describe('GET /api/health', () => {
  test('returns 200 status', async () => {
    const response = await GET();

    expect(response.status).toBe(200);
  });
});
```

#### Test 1.2: GET returns component name

```typescript
test('returns component name', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.component).toBe('v0-ai-agent-for-servers');
});
```

#### Test 1.3: GET returns online status

```typescript
test('returns online status', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.status).toBe('online');
});
```

#### Test 1.4: GET returns timestamp

```typescript
test('returns timestamp', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.timestamp).toBeDefined();
  expect(typeof data.timestamp).toBe('string');
  expect(new Date(data.timestamp).toISOString()).toBe(data.timestamp);
});
```

#### Test 1.5: GET returns version

```typescript
test('returns version', async () => {
  const response = await GET();
  const data = await response.json();

  expect(data.version).toBe('1.0.0');
});
```

#### Test 1.6: GET returns endpoints list

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

### Test Suite 2: /api/cross-sync/route.ts

#### Test 2.1: POST returns 200 on success

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

#### Test 2.2: POST returns component name

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

#### Test 2.3: POST returns synced status

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

#### Test 2.4: POST returns timestamp

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

#### Test 2.5: POST returns sync_result

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

#### Test 2.6: POST returns success message

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

#### Test 2.7: POST processes unified_state parameter

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

#### Test 2.8: POST processes component_states parameter

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

#### Test 2.9: POST processes sync_type parameter

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

#### Test 2.10: POST handles missing unified_state

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

#### Test 2.11: POST handles missing component_states

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

#### Test 2.12: POST handles missing sync_type

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

#### Test 2.13: POST processes TrainLLM state updates

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

#### Test 2.14: POST generates resource alerts for low resources

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

#### Test 2.15: POST generates health monitoring recommendations

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

#### Test 2.16: POST handles empty request body

```typescript
test('handles empty request body', async () => {
  const request = createMockRequest({});

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.sync_result).toBeDefined();
});
```

#### Test 2.17: POST handles invalid JSON

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

  expect(response.status).toBe(500);
  const data = await response.json();
  expect(data.error).toBe('Sync failed');
});
```

### Test Suite 3: /api/unified-query/route.ts

#### Test 3.1: POST returns 400 for missing query

```typescript
import { POST } from '../unified-query/route';
import { createMockRequest } from './test-utils';

describe('POST /api/unified-query', () => {
  test('returns 400 for missing query', async () => {
    const request = createMockRequest({
      context: {},
      component: 'test'
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    const data = await response.json();
    expect(data.error).toBe('Query parameter required');
  });
});
```

#### Test 3.2: POST returns 200 on success

```typescript
test('returns 200 on success', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);

  expect(response.status).toBe(200);
});
```

#### Test 3.3: POST returns component name

```typescript
test('returns component name', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.component).toBe('v0-ai-agent-for-servers');
});
```

#### Test 3.4: POST returns query

```typescript
test('returns query', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.query).toBe('test query');
});
```

#### Test 3.5: POST returns response

```typescript
test('returns response', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response).toBeDefined();
  expect(typeof data.response).toBe('object');
});
```

#### Test 3.6: POST returns timestamp

```typescript
test('returns timestamp', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.timestamp).toBeDefined();
  expect(typeof data.timestamp).toBe('string');
});
```

#### Test 3.7: POST returns capabilities

```typescript
test('returns capabilities', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.capabilities).toBeDefined();
  expect(Array.isArray(data.capabilities)).toBe(true);
  expect(data.capabilities).toContain('server_management');
  expect(data.capabilities).toContain('container_operations');
  expect(data.capabilities).toContain('terminal_commands');
  expect(data.capabilities).toContain('ai_orchestration');
});
```

#### Test 3.8: POST processes container queries

```typescript
test('processes container queries', async () => {
  const request = createMockRequest({
    query: 'list containers',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.type).toBe('container_operation');
  expect(data.response.analysis).toContain('container');
});
```

#### Test 3.9: POST processes server queries

```typescript
test('processes server queries', async () => {
  const request = createMockRequest({
    query: 'check server status',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.type).toBe('server_management');
  expect(data.response.analysis).toContain('server');
});
```

#### Test 3.10: POST processes terminal queries

```typescript
test('processes terminal queries', async () => {
  const request = createMockRequest({
    query: 'run command ls',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.type).toBe('terminal_operation');
  expect(data.response.analysis).toContain('terminal');
});
```

#### Test 3.11: POST processes general queries

```typescript
test('processes general queries', async () => {
  const request = createMockRequest({
    query: 'what can you do',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.type).toBe('general_ai_agent_query');
  expect(data.response.analysis).toContain('what can you do');
});
```

#### Test 3.12: POST includes context in response

```typescript
test('includes context in response', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {
      custom_data: 'test value'
    },
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response).toBeDefined();
});
```

#### Test 3.13: POST handles missing context

```typescript
test('handles missing context', async () => {
  const request = createMockRequest({
    query: 'test query'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.response).toBeDefined();
});
```

#### Test 3.14: POST handles missing component

```typescript
test('handles missing component', async () => {
  const request = createMockRequest({
    query: 'test query',
    context: {}
  });

  const response = await POST(request);
  const data = await response.json();

  expect(response.status).toBe(200);
  expect(data.response).toBeDefined();
});
```

#### Test 3.15: POST handles empty query

```typescript
test('handles empty query', async () => {
  const request = createMockRequest({
    query: '',
    context: {},
    component: 'test'
  });

  const response = await POST(request);

  expect(response.status).toBe(200);
});
```

#### Test 3.16: POST handles invalid JSON

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

  expect(response.status).toBe(500);
  const data = await response.json();
  expect(data.error).toBe('Internal server error');
});
```

#### Test 3.17: POST returns recommendations for container queries

```typescript
test('returns recommendations for container queries', async () => {
  const request = createMockRequest({
    query: 'manage containers',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.recommendations).toBeDefined();
  expect(Array.isArray(data.response.recommendations)).toBe(true);
});
```

#### Test 3.18: POST returns actions for container queries

```typescript
test('returns actions for container queries', async () => {
  const request = createMockRequest({
    query: 'manage containers',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.actions).toBeDefined();
  expect(Array.isArray(data.response.actions)).toBe(true);
  expect(data.response.actions[0].type).toBe('container_inspection');
});
```

#### Test 3.19: POST returns integrated_response for general queries

```typescript
test('returns integrated_response for general queries', async () => {
  const request = createMockRequest({
    query: 'general question',
    context: {},
    component: 'test'
  });

  const response = await POST(request);
  const data = await response.json();

  expect(data.response.integrated_response).toBeDefined();
  expect(data.response.integrated_response.query_type).toBe('general');
  expect(data.response.integrated_response.context_awareness).toBe(true);
  expect(data.response.integrated_response.cross_component_coordination).toBe(true);
});
```

## Test Configuration

### jest.config.js

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
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
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
```

### jest.setup.js

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
```

### package.json additions

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "next-jest": "^29.7.0"
  }
}
```

## Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test health.test.ts

# Run specific test
npm test -t "returns 200 status"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

1. **Isolation**: Each test is independent
2. **Mocking**: Next.js request/response objects are mocked
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Descriptive Names**: Test names clearly describe behavior
5. **Edge Cases**: Test missing parameters, empty values, invalid JSON
6. **Error Handling**: Test both success and error paths
7. **Type Safety**: TypeScript ensures type correctness
8. **Coverage**: Automated coverage reporting with thresholds

## Notes

- Next.js App Router routes are tested as async functions
- `NextRequest` and `NextResponse` are mocked for testing
- JSON parsing errors are tested
- All response fields are verified
- Query type detection is tested (container, server, terminal, general)
- Error responses are tested with 500 status codes
- Timestamps are verified to be valid ISO strings
- Complex nested logic in cross-sync is thoroughly tested
