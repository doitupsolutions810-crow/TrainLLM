# CycleKernel TestFlight Integration Guide

## Overview

TestFlight is Apple's beta distribution platform. For cross-platform or web-based components of CycleKernel, we simulate the "TestFlight Runtime" to enable beta-only features, advanced logging, or experimental simulation mechanics.

## Runtime Detection

We use a utility routine to detect if the application is running in a beta/testflight environment.

### TypeScript Integration

The utility is located at [testflight_utils.ts](file:///Users/crownest/Desktop/anti2/Anti4/TrainLLM/utils/testflight_utils.ts).

```typescript
import { isTestFlight, getRuntimeEnvironment } from './utils/testflight_utils';

if (isTestFlight()) {
  console.log("Running in TestFlight mode. Enabling experimental features...");
  // Enable high-verbosity logging or alternate API endpoints
}
```

### Methods of Triggering TestFlight Mode

1.  **URL Parameter (Web)**:
    Append `?env=testflight` or `?beta=true` to the URL.
2.  **Environment Variable (Server/Node)**:
    Set `APP_ENVIRONMENT=testflight` or `IS_BETA_DISTRIBUTION=true` in your `.env` file.
3.  **Build Flag**:
    Inject `window.__TESTFLIGHT__ = true` during the build process.

## Handling "Runtie" Logic

If your "runtie" (runtime routine) needs to behave differently during beta testing:

-   **Simulation Speed**: You might want to decrease `CK_EPOCH_DELAY` in TestFlight to gather data faster.
-   **Debug Mode**: Enable `DEBUG` level logging for the Kernel and Manus AI.
-   **Safe Rollbacks**: Ensure that in TestFlight, any kernel changes are strictly logged to `audit_logs` for review.

## Common Issues

-   **Environment Leak**: Ensure that TestFlight-specific logic is guarded by `isTestFlight()` to prevent accidental activation in production.
-   **Mock Data**: When testing in "TestFlight runtime", prefer using test datasets to avoid polluting production simulation history.
