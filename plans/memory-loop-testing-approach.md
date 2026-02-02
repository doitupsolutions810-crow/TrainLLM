# Detailed Testing Approach: memory-loop.ts

## Component Overview

[`memory-loop.ts`](../TrainLLM/src/memory-loop.ts) is a TypeScript module that handles logging and reading action logs to/from a JSONL (JSON Lines) file. It performs file system operations which require careful mocking and isolation in tests.

## Source Code Analysis

```typescript
import fs from 'fs';

export function logAction(action: string, result: string) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    action,
    result
  };

  fs.writeFileSync('action-log.jsonl', JSON.stringify(logEntry) + '\n', { flag: 'a' });
}

export function readActions(): Array<{timestamp:string, action:string, result:string}> {
  try {
    const raw = fs.readFileSync('action-log.jsonl', 'utf8');
    return raw.trim().split('\n').map(l => JSON.parse(l));
  } catch (err) {
    return [];
  }
}
```

## Testing Challenges

1. **File System Dependencies**: The module directly uses `fs` module
2. **Side Effects**: `logAction` writes to disk, creating persistent state
3. **Error Handling**: `readActions` has a try-catch that needs testing
4. **Date/Time**: Uses `new Date()` which varies between test runs
5. **File Format**: JSONL format (one JSON object per line)

## Testing Strategy

### Mocking Approach

We'll use Jest's `jest.mock()` to mock the `fs` module, allowing us to:
- Control file system behavior in tests
- Avoid actual disk I/O
- Test error conditions
- Verify file operations without side effects

### Test File Structure

```
TrainLLM/src/__tests__/
└── memory-loop.test.ts
```

## Detailed Test Cases

### Test 1: logAction writes valid JSON to file

**Purpose**: Verify that `logAction` creates a properly formatted JSON entry

**Approach**:
- Mock `fs.writeFileSync` to capture calls
- Call `logAction` with test data
- Verify `writeFileSync` was called with correct parameters
- Verify the JSON structure is valid

```typescript
test('logAction writes valid JSON to action-log.jsonl', () => {
  const mockWriteFileSync = jest.fn();
  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: jest.fn()
  }));

  const { logAction } = require('../memory-loop');

  logAction('test-action', 'test-result');

  expect(mockWriteFileSync).toHaveBeenCalledWith(
    'action-log.jsonl',
    expect.stringMatching(/^{.*}$/),
    { flag: 'a' }
  );
});
```

### Test 2: logAction includes timestamp, action, and result

**Purpose**: Verify all required fields are present in the log entry

**Approach**:
- Mock `fs.writeFileSync` to capture the written data
- Call `logAction` with specific values
- Parse the captured JSON and verify all fields
- Verify timestamp format (ISO 8601)

```typescript
test('logAction includes timestamp, action, and result', () => {
  const mockWriteFileSync = jest.fn();
  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: jest.fn()
  }));

  const { logAction } = require('../memory-loop');

  logAction('deploy-container', 'success');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('timestamp');
  expect(logEntry).toHaveProperty('action', 'deploy-container');
  expect(logEntry).toHaveProperty('result', 'success');
  expect(logEntry.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
});
```

### Test 3: logAction appends to file (not overwrites)

**Purpose**: Verify the append flag is used correctly

**Approach**:
- Mock `fs.writeFileSync` and verify the flag parameter
- Ensure `{ flag: 'a' }` is passed to append mode

```typescript
test('logAction appends to file (not overwrites)', () => {
  const mockWriteFileSync = jest.fn();
  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: jest.fn()
  }));

  const { logAction } = require('../memory-loop');

  logAction('action1', 'result1');

  expect(mockWriteFileSync).toHaveBeenCalledWith(
    'action-log.jsonl',
    expect.any(String),
    { flag: 'a' }  // Append mode
  );
});
```

### Test 4: logAction adds newline after JSON

**Purpose**: Verify JSONL format (one JSON per line)

**Approach**:
- Capture the written data
- Verify it ends with a newline character

```typescript
test('logAction adds newline after JSON', () => {
  const mockWriteFileSync = jest.fn();
  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: jest.fn()
  }));

  const { logAction } = require('../memory-loop');

  logAction('test', 'result');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  expect(writtenData).toMatch(/\n$/);
});
```

### Test 5: readActions returns empty array when file doesn't exist

**Purpose**: Verify graceful handling of missing file

**Approach**:
- Mock `fs.readFileSync` to throw an error (simulating missing file)
- Call `readActions`
- Verify it returns an empty array

```typescript
test('readActions returns empty array when file does not exist', () => {
  const mockReadFileSync = jest.fn(() => {
    throw new Error('ENOENT: no such file');
  });
  jest.doMock('fs', () => ({
    writeFileSync: jest.fn(),
    readFileSync: mockReadFileSync
  }));

  const { readActions } = require('../memory-loop');

  const actions = readActions();

  expect(actions).toEqual([]);
  expect(mockReadFileSync).toHaveBeenCalledWith('action-log.jsonl', 'utf8');
});
```

### Test 6: readActions parses and returns all log entries

**Purpose**: Verify correct parsing of JSONL format

**Approach**:
- Mock `fs.readFileSync` to return multiple JSON lines
- Call `readActions`
- Verify all entries are parsed correctly

```typescript
test('readActions parses and returns all log entries', () => {
  const mockData = JSON.stringify({ timestamp: '2024-01-01T00:00:00.000Z', action: 'action1', result: 'result1' }) + '\n' +
                  JSON.stringify({ timestamp: '2024-01-01T00:01:00.000Z', action: 'action2', result: 'result2' }) + '\n';

  const mockReadFileSync = jest.fn(() => mockData);
  jest.doMock('fs', () => ({
    writeFileSync: jest.fn(),
    readFileSync: mockReadFileSync
  }));

  const { readActions } = require('../memory-loop');

  const actions = readActions();

  expect(actions).toHaveLength(2);
  expect(actions[0]).toEqual({
    timestamp: '2024-01-01T00:00:00.000Z',
    action: 'action1',
    result: 'result1'
  });
  expect(actions[1]).toEqual({
    timestamp: '2024-01-01T00:01:00.000Z',
    action: 'action2',
    result: 'result2'
  });
});
```

### Test 7: readActions handles empty file

**Purpose**: Verify handling of empty log file

**Approach**:
- Mock `fs.readFileSync` to return empty string
- Call `readActions`
- Verify it returns empty array

```typescript
test('readActions handles empty file', () => {
  const mockReadFileSync = jest.fn(() => '');
  jest.doMock('fs', () => ({
    writeFileSync: jest.fn(),
    readFileSync: mockReadFileSync
  }));

  const { readActions } = require('../memory-loop');

  const actions = readActions();

  expect(actions).toEqual([]);
});
```

### Test 8: readActions handles malformed JSON gracefully

**Purpose**: Verify error handling for corrupted log file

**Approach**:
- Mock `fs.readFileSync` to return invalid JSON
- Call `readActions`
- Verify it throws or handles the error appropriately

```typescript
test('readActions handles malformed JSON gracefully', () => {
  const mockData = JSON.stringify({ timestamp: '2024-01-01T00:00:00.000Z', action: 'action1', result: 'result1' }) + '\n' +
                  'invalid-json\n' +
                  JSON.stringify({ timestamp: '2024-01-01T00:01:00.000Z', action: 'action2', result: 'result2' }) + '\n';

  const mockReadFileSync = jest.fn(() => mockData);
  jest.doMock('fs', () => ({
    writeFileSync: jest.fn(),
    readFileSync: mockReadFileSync
  }));

  const { readActions } = require('../memory-loop');

  // This should throw an error when parsing invalid JSON
  expect(() => readActions()).toThrow();
});
```

### Test 9: Multiple log actions are appended correctly

**Purpose**: Verify sequential logging works correctly

**Approach**:
- Mock `fs.writeFileSync`
- Call `logAction` multiple times
- Verify each call appends to the file

```typescript
test('multiple log actions are appended correctly', () => {
  const mockWriteFileSync = jest.fn();
  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: jest.fn()
  }));

  const { logAction } = require('../memory-loop');

  logAction('action1', 'result1');
  logAction('action2', 'result2');
  logAction('action3', 'result3');

  expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

  // Verify each call was made with append flag
  mockWriteFileSync.mock.calls.forEach(call => {
    expect(call[2]).toEqual({ flag: 'a' });
  });
});
```

### Test 10: Integration test - log and read actions

**Purpose**: Verify end-to-end workflow

**Approach**:
- Mock both `writeFileSync` and `readFileSync`
- Log multiple actions
- Read them back
- Verify data integrity

```typescript
test('integration: log and read actions', () => {
  let fileContent = '';

  const mockWriteFileSync = jest.fn((path, data, options) => {
    if (options?.flag === 'a') {
      fileContent += data;
    }
  });

  const mockReadFileSync = jest.fn(() => fileContent);

  jest.doMock('fs', () => ({
    writeFileSync: mockWriteFileSync,
    readFileSync: mockReadFileSync
  }));

  const { logAction, readActions } = require('../memory-loop');

  // Log actions
  logAction('deploy', 'success');
  logAction('configure', 'completed');
  logAction('start', 'running');

  // Read actions
  const actions = readActions();

  expect(actions).toHaveLength(3);
  expect(actions[0].action).toBe('deploy');
  expect(actions[1].action).toBe('configure');
  expect(actions[2].action).toBe('start');
});
```

## Complete Test File

```typescript
/**
 * memory-loop.test.ts
 * Tests for memory-loop.ts module
 */

describe('memory-loop', () => {
  let mockWriteFileSync: jest.Mock;
  let mockReadFileSync: jest.Mock;

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    jest.resetModules();

    // Create fresh mocks
    mockWriteFileSync = jest.fn();
    mockReadFileSync = jest.fn();

    // Mock fs module
    jest.doMock('fs', () => ({
      writeFileSync: mockWriteFileSync,
      readFileSync: mockReadFileSync
    }));
  });

  describe('logAction', () => {
    test('writes valid JSON to action-log.jsonl', () => {
      const { logAction } = require('../memory-loop');

      logAction('test-action', 'test-result');

      expect(mockWriteFileSync).toHaveBeenCalledWith(
        'action-log.jsonl',
        expect.stringMatching(/^{.*}$/),
        { flag: 'a' }
      );
    });

    test('includes timestamp, action, and result', () => {
      const { logAction } = require('../memory-loop');

      logAction('deploy-container', 'success');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('timestamp');
      expect(logEntry).toHaveProperty('action', 'deploy-container');
      expect(logEntry).toHaveProperty('result', 'success');
      expect(logEntry.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });

    test('appends to file (not overwrites)', () => {
      const { logAction } = require('../memory-loop');

      logAction('action1', 'result1');

      expect(mockWriteFileSync).toHaveBeenCalledWith(
        'action-log.jsonl',
        expect.any(String),
        { flag: 'a' }
      );
    });

    test('adds newline after JSON', () => {
      const { logAction } = require('../memory-loop');

      logAction('test', 'result');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      expect(writtenData).toMatch(/\n$/);
    });

    test('multiple log actions are appended correctly', () => {
      const { logAction } = require('../memory-loop');

      logAction('action1', 'result1');
      logAction('action2', 'result2');
      logAction('action3', 'result3');

      expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

      mockWriteFileSync.mock.calls.forEach(call => {
        expect(call[2]).toEqual({ flag: 'a' });
      });
    });
  });

  describe('readActions', () => {
    test('returns empty array when file does not exist', () => {
      mockReadFileSync.mockImplementation(() => {
        throw new Error('ENOENT: no such file');
      });

      const { readActions } = require('../memory-loop');

      const actions = readActions();

      expect(actions).toEqual([]);
      expect(mockReadFileSync).toHaveBeenCalledWith('action-log.jsonl', 'utf8');
    });

    test('parses and returns all log entries', () => {
      const mockData = JSON.stringify({ timestamp: '2024-01-01T00:00:00.000Z', action: 'action1', result: 'result1' }) + '\n' +
                      JSON.stringify({ timestamp: '2024-01-01T00:01:00.000Z', action: 'action2', result: 'result2' }) + '\n';

      mockReadFileSync.mockReturnValue(mockData);

      const { readActions } = require('../memory-loop');

      const actions = readActions();

      expect(actions).toHaveLength(2);
      expect(actions[0]).toEqual({
        timestamp: '2024-01-01T00:00:00.000Z',
        action: 'action1',
        result: 'result1'
      });
      expect(actions[1]).toEqual({
        timestamp: '2024-01-01T00:01:00.000Z',
        action: 'action2',
        result: 'result2'
      });
    });

    test('handles empty file', () => {
      mockReadFileSync.mockReturnValue('');

      const { readActions } = require('../memory-loop');

      const actions = readActions();

      expect(actions).toEqual([]);
    });

    test('handles malformed JSON gracefully', () => {
      const mockData = JSON.stringify({ timestamp: '2024-01-01T00:00:00.000Z', action: 'action1', result: 'result1' }) + '\n' +
                      'invalid-json\n';

      mockReadFileSync.mockReturnValue(mockData);

      const { readActions } = require('../memory-loop');

      expect(() => readActions()).toThrow();
    });
  });

  describe('integration', () => {
    test('log and read actions workflow', () => {
      let fileContent = '';

      mockWriteFileSync.mockImplementation((path, data, options) => {
        if (options?.flag === 'a') {
          fileContent += data;
        }
      });

      mockReadFileSync.mockReturnValue(fileContent);

      const { logAction, readActions } = require('../memory-loop');

      logAction('deploy', 'success');
      logAction('configure', 'completed');
      logAction('start', 'running');

      const actions = readActions();

      expect(actions).toHaveLength(3);
      expect(actions[0].action).toBe('deploy');
      expect(actions[1].action).toBe('configure');
      expect(actions[2].action).toBe('start');
    });
  });
});
```

## Testing Best Practices Applied

1. **Isolation**: Each test is independent with fresh mocks
2. **AAA Pattern**: Arrange (setup mocks), Act (call function), Assert (verify results)
3. **Descriptive Names**: Test names clearly describe what is being tested
4. **Mock Verification**: Verify mock calls with exact parameters
5. **Edge Cases**: Test empty files, missing files, malformed data
6. **Integration Tests**: Test the complete log-and-read workflow
7. **Error Handling**: Verify graceful error handling

## Coverage Goals

- **Statement Coverage**: 100% (all code paths tested)
- **Branch Coverage**: 100% (all conditional branches tested)
- **Function Coverage**: 100% (both functions tested)

## Running the Tests

```bash
cd TrainLLM
npm test -- memory-loop.test.ts
```

## Notes

- The `jest.doMock()` and `jest.resetModules()` pattern is used to ensure fresh mocks for each test
- File path is hardcoded as 'action-log.jsonl' - consider making it configurable for better testability
- The current implementation doesn't handle JSON parsing errors in `readActions` - this could be improved
- Timestamps use `new Date()` which varies between runs - we verify format but not exact value
