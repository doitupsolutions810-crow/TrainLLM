# Detailed Testing Approach: model-disagreement-logger.ts

## Component Overview

[`model-disagreement-logger.ts`](../TrainLLM/src/model-disagreement-logger.ts) is a TypeScript module that logs model disagreements:
- Logs disagreements between two AI models
- Records model outputs and final decision
- Calculates whether models agreed
- Writes to JSONL file (disagreement-log.jsonl)
- Includes timestamp for each log entry

## Testing Challenges

1. **File System Dependencies**: Uses `fs` module for file I/O
2. **Side Effects**: `logDisagreement` writes to disk
3. **Date/Time**: Uses `new Date()` which varies between test runs
4. **JSON Format**: Writes JSONL format (one JSON object per line)
5. **Boolean Logic**: Calculates `agreed` based on model comparison

## Testing Strategy

### Mocking Approach

We'll use Jest's `jest.mock()` to mock `fs` module:
- Mock `fs.writeFileSync` to capture writes
- Avoid actual disk I/O
- Verify file operations without side effects
- Test JSON structure and format

### Test File Structure

```
TrainLLM/src/__tests__/
└── model-disagreement-logger.test.ts
```

## Detailed Test Cases

### Test Suite 1: logDisagreement - Basic Functionality

#### Test 1.1: logDisagreement writes valid JSON to file

```typescript
import { logDisagreement } from '../model-disagreement-logger';

describe('model-disagreement-logger', () => {
  let mockWriteFileSync: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.resetModules();

    mockWriteFileSync = jest.fn();
    jest.doMock('fs', () => ({
      writeFileSync: mockWriteFileSync,
      readFileSync: jest.fn(),
    }));
  });

  test('logDisagreement writes valid JSON to disagreement-log.jsonl', () => {
    const { logDisagreement } = require('../model-disagreement-logger');

    logDisagreement('model1', 'model2', 'decision1');

    expect(mockWriteFileSync).toHaveBeenCalledWith(
      'disagreement-log.jsonl',
      expect.stringMatching(/^{.*}$/),
      { flag: 'a' }
    );
  });
});
```

#### Test 1.2: logDisagreement includes timestamp

```typescript
test('logDisagreement includes timestamp', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('timestamp');
  expect(typeof logEntry.timestamp).toBe('string');
  expect(logEntry.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
});
```

#### Test 1.3: logDisagreement includes model1

```typescript
test('logDisagreement includes model1', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('gpt-4', 'claude-3', 'final-decision');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('model1');
  expect(logEntry.model1).toBe('gpt-4');
});
```

#### Test 1.4: logDisagreement includes model2

```typescript
test('logDisagreement includes model2', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('gpt-4', 'claude-3', 'final-decision');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('model2');
  expect(logEntry.model2).toBe('claude-3');
});
```

#### Test 1.5: logDisagreement includes decision

```typescript
test('logDisagreement includes decision', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'use-model-1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('decision');
  expect(logEntry.decision).toBe('use-model-1');
});
```

#### Test 1.6: logDisagreement appends to file

```typescript
test('logDisagreement appends to file', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'decision1');

  expect(mockWriteFileSync).toHaveBeenCalledWith(
    'disagreement-log.jsonl',
    expect.any(String),
    { flag: 'a' }
  );
});
```

#### Test 1.7: logDisagreement adds newline after JSON

```typescript
test('logDisagreement adds newline after JSON', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  expect(writtenData).toMatch(/\n$/);
});
```

### Test Suite 2: logDisagreement - Agreement Calculation

#### Test 2.1: logDisagreement sets agreed to true when models match

```typescript
test('logDisagreement sets agreed to true when models match', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('same-output', 'same-output', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('agreed');
  expect(logEntry.agreed).toBe(true);
});
```

#### Test 2.2: logDisagreement sets agreed to false when models differ

```typescript
test('logDisagreement sets agreed to false when models differ', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('output1', 'output2', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('agreed');
  expect(logEntry.agreed).toBe(false);
});
```

#### Test 2.3: logDisagreement handles case-sensitive comparison

```typescript
test('logDisagreement handles case-sensitive comparison', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('Output', 'output', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.agreed).toBe(false); // Case-sensitive, so not equal
});
```

#### Test 2.4: logDisagreement handles whitespace differences

```typescript
test('logDisagreement handles whitespace differences', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('output', 'output ', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.agreed).toBe(false); // Whitespace difference
});
```

#### Test 2.5: logDisagreement handles empty strings

```typescript
test('logDisagreement handles empty strings', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('', '', 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.agreed).toBe(true); // Both empty, so equal
});
```

#### Test 2.6: logDisagreement handles null values

```typescript
test('logDisagreement handles null values', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement(null as any, null as any, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.agreed).toBe(true); // Both null, so equal
});
```

### Test Suite 3: logDisagreement - Multiple Calls

#### Test 3.1: Multiple logDisagreement calls append correctly

```typescript
test('multiple logDisagreement calls append correctly', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'decision1');
  logDisagreement('model3', 'model4', 'decision2');
  logDisagreement('model5', 'model6', 'decision3');

  expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

  // Verify all calls use append mode
  mockWriteFileSync.mock.calls.forEach(call => {
    expect(call[2]).toEqual({ flag: 'a' });
  });
});
```

#### Test 3.2: Multiple logDisagreement calls have different timestamps

```typescript
test('multiple logDisagreement calls have different timestamps', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'decision1');

  // Wait a bit to ensure different timestamp
  return new Promise(resolve => setTimeout(resolve, 10)).then(() => {
    logDisagreement('model3', 'model4', 'decision2');

    const firstEntry = JSON.parse(mockWriteFileSync.mock.calls[0][1]);
    const secondEntry = JSON.parse(mockWriteFileSync.mock.calls[1][1]);

    expect(firstEntry.timestamp).not.toBe(secondEntry.timestamp);
  });
});
```

### Test Suite 4: logDisagreement - Edge Cases

#### Test 4.1: logDisagreement handles very long model outputs

```typescript
test('logDisagreement handles very long model outputs', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const longOutput = 'A'.repeat(10000);
  logDisagreement(longOutput, longOutput, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.model1).toBe(longOutput);
  expect(logEntry.model2).toBe(longOutput);
  expect(logEntry.agreed).toBe(true);
});
```

#### Test 4.2: logDisagreement handles special characters

```typescript
test('logDisagreement handles special characters', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const specialOutput = 'Hello @#$%^&*() World!';
  logDisagreement(specialOutput, specialOutput, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.model1).toBe(specialOutput);
  expect(logEntry.model2).toBe(specialOutput);
});
```

#### Test 4.3: logDisagreement handles Unicode characters

```typescript
test('logDisagreement handles Unicode characters', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const unicodeOutput = 'Hello 世界 🌍';
  logDisagreement(unicodeOutput, unicodeOutput, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.model1).toBe(unicodeOutput);
  expect(logEntry.model2).toBe(unicodeOutput);
});
```

#### Test 4.4: logDisagreement handles JSON in model outputs

```typescript
test('logDisagreement handles JSON in model outputs', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const jsonOutput = '{"key": "value"}';
  logDisagreement(jsonOutput, jsonOutput, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.model1).toBe(jsonOutput);
  expect(logEntry.model2).toBe(jsonOutput);
});
```

#### Test 4.5: logDisagreement handles newlines in model outputs

```typescript
test('logDisagreement handles newlines in model outputs', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const multilineOutput = 'Line 1\nLine 2\nLine 3';
  logDisagreement(multilineOutput, multilineOutput, 'decision1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.model1).toBe(multilineOutput);
  expect(logEntry.model2).toBe(multilineOutput);
});
```

### Test Suite 5: logDisagreement - Decision Parameter

#### Test 5.1: logDisagreement includes decision parameter

```typescript
test('logDisagreement includes decision parameter', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', 'use-model-1');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry).toHaveProperty('decision');
  expect(logEntry.decision).toBe('use-model-1');
});
```

#### Test 5.2: logDisagreement handles empty decision

```typescript
test('logDisagreement handles empty decision', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', '');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.decision).toBe('');
});
```

#### Test 5.3: logDisagreement handles null decision

```typescript
test('logDisagreement handles null decision', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('model1', 'model2', null as any);

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.decision).toBe(null);
});
```

#### Test 5.4: logDisagreement handles decision with special characters

```typescript
test('logDisagreement handles decision with special characters', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  const specialDecision = 'Decision @#$%^&*()';
  logDisagreement('model1', 'model2', specialDecision);

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  expect(logEntry.decision).toBe(specialDecision);
});
```

### Test Suite 6: Integration Tests

#### Test 6.1: Integration - log and verify structure

```typescript
test('integration: log and verify complete structure', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  logDisagreement('gpt-4', 'claude-3', 'use-gpt-4');

  const writtenData = mockWriteFileSync.mock.calls[0][1];
  const logEntry = JSON.parse(writtenData);

  // Verify all required fields
  expect(logEntry).toHaveProperty('timestamp');
  expect(logEntry).toHaveProperty('model1');
  expect(logEntry).toHaveProperty('model2');
  expect(logEntry).toHaveProperty('decision');
  expect(logEntry).toHaveProperty('agreed');

  // Verify values
  expect(logEntry.model1).toBe('gpt-4');
  expect(logEntry.model2).toBe('claude-3');
  expect(logEntry.decision).toBe('use-gpt-4');
  expect(logEntry.agreed).toBe(false);
});
```

#### Test 6.2: Integration - multiple logs with different scenarios

```typescript
test('integration: multiple logs with different scenarios', () => {
  const { logDisagreement } = require('../model-disagreement-logger');

  // Scenario 1: Agreement
  logDisagreement('same', 'same', 'decision1');

  // Scenario 2: Disagreement
  logDisagreement('diff1', 'diff2', 'decision2');

  // Scenario 3: Empty models
  logDisagreement('', '', 'decision3');

  expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

  const entry1 = JSON.parse(mockWriteFileSync.mock.calls[0][1]);
  const entry2 = JSON.parse(mockWriteFileSync.mock.calls[1][1]);
  const entry3 = JSON.parse(mockWriteFileSync.mock.calls[2][1]);

  expect(entry1.agreed).toBe(true);
  expect(entry2.agreed).toBe(false);
  expect(entry3.agreed).toBe(true);
});
```

## Complete Test File

```typescript
/**
 * model-disagreement-logger.test.ts
 * Tests for model-disagreement-logger.ts module
 */

import { logDisagreement } from '../model-disagreement-logger';

describe('model-disagreement-logger', () => {
  let mockWriteFileSync: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.resetModules();

    mockWriteFileSync = jest.fn();
    jest.doMock('fs', () => ({
      writeFileSync: mockWriteFileSync,
      readFileSync: jest.fn(),
    }));
  });

  describe('logDisagreement', () => {
    test('writes valid JSON to disagreement-log.jsonl', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('model1', 'model2', 'decision1');

      expect(mockWriteFileSync).toHaveBeenCalledWith(
        'disagreement-log.jsonl',
        expect.stringMatching(/^{.*}$/),
        { flag: 'a' }
      );
    });

    test('includes timestamp', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('model1', 'model2', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('timestamp');
      expect(typeof logEntry.timestamp).toBe('string');
    });

    test('includes model1', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('gpt-4', 'claude-3', 'final-decision');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('model1');
      expect(logEntry.model1).toBe('gpt-4');
    });

    test('includes model2', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('gpt-4', 'claude-3', 'final-decision');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('model2');
      expect(logEntry.model2).toBe('claude-3');
    });

    test('includes decision', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('model1', 'model2', 'use-model-1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('decision');
      expect(logEntry.decision).toBe('use-model-1');
    });

    test('appends to file', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('model1', 'model2', 'decision1');

      expect(mockWriteFileSync).toHaveBeenCalledWith(
        'disagreement-log.jsonl',
        expect.any(String),
        { flag: 'a' }
      );
    });

    test('adds newline after JSON', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('model1', 'model2', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      expect(writtenData).toMatch(/\n$/);
    });

    test('sets agreed to true when models match', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('same-output', 'same-output', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('agreed');
      expect(logEntry.agreed).toBe(true);
    });

    test('sets agreed to false when models differ', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('output1', 'output2', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('agreed');
      expect(logEntry.agreed).toBe(false);
    });

    test('handles case-sensitive comparison', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('Output', 'output', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.agreed).toBe(false);
    });

    test('handles empty strings', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('', '', 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.agreed).toBe(true);
    });

    test('handles null values', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement(null as any, null as any, 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.agreed).toBe(true);
    });

    test('handles very long model outputs', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      const longOutput = 'A'.repeat(10000);
      logDisagreement(longOutput, longOutput, 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.model1).toBe(longOutput);
      expect(logEntry.model2).toBe(longOutput);
    });

    test('handles special characters', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      const specialOutput = 'Hello @#$%^&*() World!';
      logDisagreement(specialOutput, specialOutput, 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.model1).toBe(specialOutput);
      expect(logEntry.model2).toBe(specialOutput);
    });

    test('handles Unicode characters', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      const unicodeOutput = 'Hello 世界 🌍';
      logDisagreement(unicodeOutput, unicodeOutput, 'decision1');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry.model1).toBe(unicodeOutput);
      expect(logEntry.model2).toBe(unicodeOutput);
    });
  });

  describe('integration', () => {
    test('log and verify complete structure', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('gpt-4', 'claude-3', 'use-gpt-4');

      const writtenData = mockWriteFileSync.mock.calls[0][1];
      const logEntry = JSON.parse(writtenData);

      expect(logEntry).toHaveProperty('timestamp');
      expect(logEntry).toHaveProperty('model1');
      expect(logEntry).toHaveProperty('model2');
      expect(logEntry).toHaveProperty('decision');
      expect(logEntry).toHaveProperty('agreed');
    });

    test('multiple logs with different scenarios', () => {
      const { logDisagreement } = require('../model-disagreement-logger');

      logDisagreement('same', 'same', 'decision1');
      logDisagreement('diff1', 'diff2', 'decision2');
      logDisagreement('', '', 'decision3');

      expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

      const entry1 = JSON.parse(mockWriteFileSync.mock.calls[0][1]);
      const entry2 = JSON.parse(mockWriteFileSync.mock.calls[1][1]);
      const entry3 = JSON.parse(mockWriteFileSync.mock.calls[2][1]);

      expect(entry1.agreed).toBe(true);
      expect(entry2.agreed).toBe(false);
      expect(entry3.agreed).toBe(true);
    });
  });
});
```

## Test Configuration

### jest.config.ts (already exists)

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

## Running Tests

```bash
cd TrainLLM

# Run all tests
npm test

# Run specific test file
npm test -- model-disagreement-logger.test.ts

# Run specific test
npm test -t "logDisagreement writes valid JSON"

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Coverage Goals

- **Statement Coverage**: 100% (simple module)
- **Branch Coverage**: 100% (all paths tested)
- **Function Coverage**: 100% (single function tested)

## Testing Best Practices Applied

1. **Isolation**: Each test is independent with fresh mocks
2. **Mocking**: `fs` module is mocked to avoid side effects
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Descriptive Names**: Test names clearly describe behavior
5. **Edge Cases**: Test empty values, null values, special characters
6. **Integration Tests**: Test complete workflows
7. **Coverage**: 100% coverage achievable for simple module
8. **Verification**: Verify all fields and values in log entries

## Notes

- The module is simple with only one function: `logDisagreement`
- File system operations are mocked to avoid actual disk I/O
- Timestamps are verified for format but not exact value (varies)
- Boolean logic is tested with various scenarios
- Edge cases include empty strings, null values, special characters, Unicode
- JSONL format is verified (one JSON per line with newline)
- Multiple calls are tested to verify append behavior
- Case sensitivity and whitespace differences are tested
- Very long outputs are tested to ensure no truncation
