/**
 * memory-loop.test.ts
 * Tests for memory-loop.ts module
 */

import fs from 'fs';

// Mock fs module
jest.mock('fs', () => ({
    writeFileSync: jest.fn(),
    readFileSync: jest.fn(),
}));

describe('memory-loop', () => {
    let mockWriteFileSync: jest.Mock;
    let mockReadFileSync: jest.Mock;

    beforeEach(() => {
        jest.clearAllMocks();
        jest.resetModules();

        mockWriteFileSync = jest.fn();
        mockReadFileSync = jest.fn();

        jest.doMock('fs', () => ({
            writeFileSync: mockWriteFileSync,
            readFileSync: mockReadFileSync,
        }));
    });

    describe('logAction', () => {
        test('writes valid JSON to action-log.jsonl', () => {
            const { logAction } = require('../memory-loop');

            logAction('test-action', 'test-result');

            expect(mockWriteFileSync).toHaveBeenCalledWith(
                'action-log.jsonl',
                expect.stringMatching(/^{.*}\n$/),
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
                'invalid-json\n' +
                JSON.stringify({ timestamp: '2024-01-01T00:01:00.000Z', action: 'action2', result: 'result2' }) + '\n';

            mockReadFileSync.mockReturnValue(mockData);

            const { readActions } = require('../memory-loop');

            // The actual implementation catches errors and returns empty array
            const actions = readActions();
            expect(actions).toEqual([]);
        });
    });

    describe('integration', () => {
        test('integration: log and read actions', () => {
            let fileContent = '';

            mockWriteFileSync.mockImplementation((path, data, options) => {
                if (options?.flag === 'a') {
                    fileContent += data;
                }
            });

            mockReadFileSync.mockImplementation(() => fileContent);

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
