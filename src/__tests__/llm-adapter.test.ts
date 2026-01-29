/**
 * llm-adapter.test.ts
 * Tests for llm-adapter.ts module
 */

describe('llm-adapter', () => {
    describe('initializeLLM', () => {
        test('returns an object with generate method', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            expect(llm).toHaveProperty('generate');
            expect(typeof llm.generate).toBe('function');
        });

        test('generate method is async', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = llm.generate('test prompt');

            expect(result).toBeInstanceOf(Promise);
        });

        test('generate method returns an object with text property', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('test prompt');

            expect(result).toHaveProperty('text');
        });

        test('generate method returns stub-response text', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('test prompt');

            expect(result.text).toBe('stub-response');
        });

        test('generate method accepts any prompt string', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result1 = await llm.generate('');
            const result2 = await llm.generate('Hello, world!');
            const result3 = await llm.generate('Special characters: @#$%^&*()');

            expect(result1.text).toBe('stub-response');
            expect(result2.text).toBe('stub-response');
            expect(result3.text).toBe('stub-response');
        });

        test('generate method handles long prompts', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const longPrompt = 'x'.repeat(10000);
            const result = await llm.generate(longPrompt);

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles unicode prompts', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('你好，世界！🌍');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles multiline prompts', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const multilinePrompt = 'Line 1\nLine 2\nLine 3';
            const result = await llm.generate(multilinePrompt);

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with special characters', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const specialPrompt = 'Test with \t tabs, \n newlines, and \r carriage returns';
            const result = await llm.generate(specialPrompt);

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles JSON-like prompts', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const jsonPrompt = '{"key": "value", "number": 123}';
            const result = await llm.generate(jsonPrompt);

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with null-like strings', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('null');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with undefined-like strings', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('undefined');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with boolean-like strings', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result1 = await llm.generate('true');
            const result2 = await llm.generate('false');

            expect(result1.text).toBe('stub-response');
            expect(result2.text).toBe('stub-response');
        });

        test('generate method handles prompts with numeric strings', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('12345');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with whitespace', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('   spaces   ');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with emojis', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('😀🎉🚀✨');

            expect(result.text).toBe('stub-response');
        });

        test('generate method handles prompts with mixed content', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const mixedPrompt = 'English 中文 🌍 123 {"key": "value"} \n\t';
            const result = await llm.generate(mixedPrompt);

            expect(result.text).toBe('stub-response');
        });

        test('generate method can be called multiple times', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result1 = await llm.generate('prompt 1');
            const result2 = await llm.generate('prompt 2');
            const result3 = await llm.generate('prompt 3');

            expect(result1.text).toBe('stub-response');
            expect(result2.text).toBe('stub-response');
            expect(result3.text).toBe('stub-response');
        });

        test('generate method returns consistent results', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result1 = await llm.generate('test');
            const result2 = await llm.generate('test');

            expect(result1.text).toBe(result2.text);
        });

        test('generate method does not modify the prompt', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const originalPrompt = 'original prompt';
            const promptCopy = originalPrompt;

            await llm.generate(originalPrompt);

            expect(originalPrompt).toBe(promptCopy);
        });

        test('generate method returns object with only text property', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm = await initializeLLM();

            const result = await llm.generate('test prompt');

            const expectedKeys = ['text'];
            const actualKeys = Object.keys(result);

            expect(actualKeys).toEqual(expectedKeys);
        });

        test('initializeLLM can be called multiple times', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm1 = await initializeLLM();
            const llm2 = await initializeLLM();

            expect(llm1).toHaveProperty('generate');
            expect(llm2).toHaveProperty('generate');

            const result1 = await llm1.generate('test');
            const result2 = await llm2.generate('test');

            expect(result1.text).toBe('stub-response');
            expect(result2.text).toBe('stub-response');
        });

        test('initializeLLM returns a new object each time', async () => {
            const { initializeLLM } = require('../llm-adapter');

            const llm1 = await initializeLLM();
            const llm2 = await initializeLLM();

            expect(llm1).not.toBe(llm2);
        });
    });
});
