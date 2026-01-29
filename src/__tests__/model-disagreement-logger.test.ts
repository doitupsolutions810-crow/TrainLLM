/**
 * model-disagreement-logger.test.ts
 * Tests for model-disagreement-logger.ts module
 */

import fs from 'fs';

// Mock fs module
jest.mock('fs', () => ({
    writeFileSync: jest.fn(),
}));

describe('model-disagreement-logger', () => {
    let mockWriteFileSync: jest.Mock;

    beforeEach(() => {
        jest.clearAllMocks();
        jest.resetModules();

        mockWriteFileSync = jest.fn();

        jest.doMock('fs', () => ({
            writeFileSync: mockWriteFileSync,
        }));
    });

    describe('logDisagreement', () => {
        test('writes valid JSON to disagreement-log.jsonl', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            expect(mockWriteFileSync).toHaveBeenCalledWith(
                'disagreement-log.jsonl',
                expect.stringMatching(/^{.*}\n$/),
                { flag: 'a' }
            );
        });

        test('includes timestamp, model1, model2, decision, and agreed', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry).toHaveProperty('timestamp');
            expect(logEntry).toHaveProperty('model1', 'model-a');
            expect(logEntry).toHaveProperty('model2', 'model-b');
            expect(logEntry).toHaveProperty('decision', 'decision-x');
            expect(logEntry).toHaveProperty('agreed');
            expect(logEntry.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
        });

        test('sets agreed to true when models agree', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-a', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.agreed).toBe(true);
        });

        test('sets agreed to false when models disagree', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.agreed).toBe(false);
        });

        test('appends to file (not overwrites)', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            expect(mockWriteFileSync).toHaveBeenCalledWith(
                'disagreement-log.jsonl',
                expect.any(String),
                { flag: 'a' }
            );
        });

        test('adds newline after JSON', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            expect(writtenData).toMatch(/\n$/);
        });

        test('handles empty strings for model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('', '', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('');
            expect(logEntry.model2).toBe('');
            expect(logEntry.agreed).toBe(true);
        });

        test('handles special characters in model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-1@#$%', 'model-2^&*()', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('model-1@#$%');
            expect(logEntry.model2).toBe('model-2^&*()');
        });

        test('handles long decision strings', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            const longDecision = 'x'.repeat(1000);
            logDisagreement('model-a', 'model-b', longDecision);

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.decision).toBe(longDecision);
        });

        test('handles unicode characters', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('模型-1', '模型-2', '决策-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('模型-1');
            expect(logEntry.model2).toBe('模型-2');
            expect(logEntry.decision).toBe('决策-x');
        });

        test('multiple log calls append correctly', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-1');
            logDisagreement('model-c', 'model-d', 'decision-2');
            logDisagreement('model-e', 'model-f', 'decision-3');

            expect(mockWriteFileSync).toHaveBeenCalledTimes(3);

            mockWriteFileSync.mock.calls.forEach(call => {
                expect(call[2]).toEqual({ flag: 'a' });
            });
        });

        test('agreed is true for identical model names (case-sensitive)', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('Model-A', 'model-a', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.agreed).toBe(false);
        });

        test('agreed is true for identical model names (case-insensitive check)', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('Model-A', 'Model-A', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.agreed).toBe(true);
        });

        test('handles null-like values in decision', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'null');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.decision).toBe('null');
        });

        test('handles numeric strings in model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('123', '456', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('123');
            expect(logEntry.model2).toBe('456');
            expect(logEntry.agreed).toBe(false);
        });

        test('handles whitespace in model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model a', 'model b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('model a');
            expect(logEntry.model2).toBe('model b');
        });

        test('handles JSON-like strings in decision', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', '{"key": "value"}');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.decision).toBe('{"key": "value"}');
        });

        test('timestamp format is ISO 8601', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            const timestamp = new Date(logEntry.timestamp);
            expect(timestamp.toISOString()).toBe(logEntry.timestamp);
        });

        test('all required fields are present', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            const requiredFields = ['timestamp', 'model1', 'model2', 'decision', 'agreed'];
            requiredFields.forEach(field => {
                expect(logEntry).toHaveProperty(field);
            });
        });

        test('no extra fields are added', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            const expectedFields = ['timestamp', 'model1', 'model2', 'decision', 'agreed'];
            const actualFields = Object.keys(logEntry);

            expect(actualFields).toEqual(expectedFields);
        });

        test('handles very long model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            const longModelName = 'model-' + 'x'.repeat(1000);
            logDisagreement(longModelName, longModelName, 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe(longModelName);
            expect(logEntry.model2).toBe(longModelName);
            expect(logEntry.agreed).toBe(true);
        });

        test('handles newline characters in decision', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model-a', 'model-b', 'decision\nwith\nnewlines');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.decision).toBe('decision\nwith\nnewlines');
        });

        test('handles tab characters in model names', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model\ta', 'model\tb', 'decision-x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('model\ta');
            expect(logEntry.model2).toBe('model\tb');
        });

        test('handles backslash characters', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model\\a', 'model\\b', 'decision\\x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('model\\a');
            expect(logEntry.model2).toBe('model\\b');
            expect(logEntry.decision).toBe('decision\\x');
        });

        test('handles quote characters', () => {
            const { logDisagreement } = require('../model-disagreement-logger');

            logDisagreement('model"a', 'model"b', 'decision"x');

            const writtenData = mockWriteFileSync.mock.calls[0][1];
            const logEntry = JSON.parse(writtenData);

            expect(logEntry.model1).toBe('model"a');
            expect(logEntry.model2).toBe('model"b');
            expect(logEntry.decision).toBe('decision"x');
        });
    });
});
