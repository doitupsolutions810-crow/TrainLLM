/**
 * TestFlight Runtime Detection Utilities
 * 
 * Provides methods to identify if the current environment is an Apple TestFlight build.
 */

/**
 * Detects if the current environment is likely TestFlight.
 * This is primarily for iOS/macOS apps, but can be simulated in web environments
 * via specific URL parameters or environment variables.
 */
export function isTestFlight(): boolean {
    if (typeof window !== 'undefined') {
        // Web detection: Check for 'testflight' in URL or a custom flag
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('env') === 'testflight' || urlParams.get('beta') === 'true') {
            return true;
        }

        // Check for specific window flags (often set by CI/CD during build)
        if ((window as any).__TESTFLIGHT__) {
            return true;
        }
    }

    // Node.js / Server-side detection: Check environment variables
    if (typeof process !== 'undefined' && process.env) {
        if (process.env.APP_ENVIRONMENT === 'testflight' || process.env.IS_BETA_DISTRIBUTION === 'true') {
            return true;
        }
    }

    return false;
}

/**
 * Returns a detailed environment description string.
 */
export function getRuntimeEnvironment(): string {
    if (isTestFlight()) {
        return 'Apple TestFlight (Beta)';
    }

    if (typeof process !== 'undefined' && process.env.NODE_ENV === 'production') {
        return 'Production (App Store)';
    }

    return 'Development / Local';
}
