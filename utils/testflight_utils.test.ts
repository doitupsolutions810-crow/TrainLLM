import { isTestFlight, getRuntimeEnvironment } from './testflight_utils';

describe('TestFlight Utils', () => {
    const originalProcessEnv = process.env;
    const originalWindow = global.window;

    beforeEach(() => {
        jest.resetModules();
        process.env = { ...originalProcessEnv };
        // @ts-ignore
        delete global.window;
    });

    afterAll(() => {
        process.env = originalProcessEnv;
        // @ts-ignore
        global.window = originalWindow;
    });

    test('detects testflight via environment variable', () => {
        process.env.APP_ENVIRONMENT = 'testflight';
        expect(isTestFlight()).toBe(true);
        expect(getRuntimeEnvironment()).toBe('Apple TestFlight (Beta)');
    });

    test('detects testflight via beta distribution flag', () => {
        process.env.IS_BETA_DISTRIBUTION = 'true';
        expect(isTestFlight()).toBe(true);
    });

    test('returns production in production env', () => {
        process.env.NODE_ENV = 'production';
        expect(isTestFlight()).toBe(false);
        expect(getRuntimeEnvironment()).toBe('Production (App Store)');
    });

    test('detects testflight in window environment via location', () => {
        // @ts-ignore
        global.window = {
            location: {
                search: '?env=testflight'
            }
        };
        expect(isTestFlight()).toBe(true);
    });

    test('detects testflight in window environment via flag', () => {
        // @ts-ignore
        global.window = {
            location: {
                search: ''
            },
            __TESTFLIGHT__: true
        };
        expect(isTestFlight()).toBe(true);
    });
});
