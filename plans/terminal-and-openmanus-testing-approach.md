# Detailed Testing Approach: terminal.tsx and open-manus.tsx

## Component Overview

### terminal.tsx ([`XTerminal`](../v0-ai-agent-for-servers/src/components/terminal.tsx))
A React component that wraps the xterm.js terminal emulator:
- Initializes xterm with custom theme
- Loads FitAddon and WebLinksAddon
- Displays welcome message and prompt
- Handles user input (characters, backspace, enter)
- Cleans up on unmount

### open-manus.tsx ([`OpenManus`](../v0-ai-agent-for-servers/src/components/open-manus.tsx))
A React component for building applications via AI:
- Input field for app requirements
- "Build App" button with loading state
- Displays built applications list
- Calls TrainLLM chat endpoint
- Handles API errors with fallback

## Testing Challenges

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

### Testing Approach

We'll use React Testing Library with Jest:
- **terminal.tsx**: Mock xterm.js to avoid DOM manipulation
- **open-manus.tsx**: Mock `fetch` API for API calls
- Test component rendering and user interactions
- Verify state changes and side effects
- Test error handling and fallback behavior

### Test File Structure

```
v0-ai-agent-for-servers/src/components/__tests__/
├── terminal.test.tsx
└── open-manus.test.tsx
```

---

# Part 1: terminal.tsx Testing

## Test Setup

### Imports and Mocks

```typescript
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { XTerminal } from '../terminal';

// Mock xterm.js
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

// Mock xterm addons
jest.mock('xterm-addon-fit', () => ({
  FitAddon: jest.fn().mockImplementation(() => ({
    fit: jest.fn(),
  })),
}));

jest.mock('xterm-addon-web-links', () => jest.fn());
```

## Detailed Test Cases for terminal.tsx

### Test Suite 1: Component Rendering

#### Test 1.1: Component renders without errors

```typescript
describe('XTerminal', () => {
  test('renders without errors', () => {
    render(<XTerminal />);

    // Component should render without throwing
    const container = screen.getByRole('generic');
    expect(container).toBeInTheDocument();
  });
});
```

#### Test 1.2: Component renders container div

```typescript
test('renders container div', () => {
  const { container } = render(<XTerminal />);

  expect(container.firstChild).toBeInTheDocument();
  expect(container.firstChild?.nodeName).toBe('DIV');
});
```

### Test Suite 2: Terminal Initialization

#### Test 2.1: Initializes Terminal with correct options

```typescript
test('initializes Terminal with correct options', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  expect(Terminal).toHaveBeenCalledWith(
    expect.objectContaining({
      cursorBlink: true,
      theme: expect.objectContaining({
        background: expect.any(String),
        foreground: expect.any(String),
      }),
    })
  );
});
```

#### Test 2.2: Initializes FitAddon

```typescript
test('initializes FitAddon', () => {
  const { FitAddon } = require('xterm-addon-fit');

  render(<XTerminal />);

  expect(FitAddon).toHaveBeenCalled();
});
```

#### Test 2.3: Initializes WebLinksAddon

```typescript
test('initializes WebLinksAddon', () => {
  const WebLinksAddon = require('xterm-addon-web-links');

  render(<XTerminal />);

  expect(WebLinksAddon).toHaveBeenCalled();
});
```

#### Test 2.4: Loads FitAddon to terminal

```typescript
test('loads FitAddon to terminal', () => {
  const { Terminal } = require('xterm');
  const { FitAddon } = require('xterm-addon-fit');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const fitAddonInstance = FitAddon.mock.results[0].value;

  expect(terminalInstance.loadAddon).toHaveBeenCalledWith(fitAddonInstance);
});
```

#### Test 2.5: Loads WebLinksAddon to terminal

```typescript
test('loads WebLinksAddon to terminal', () => {
  const { Terminal } = require('xterm');
  const WebLinksAddon = require('xterm-addon-web-links');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const webLinksAddonInstance = WebLinksAddon.mock.results[0].value;

  expect(terminalInstance.loadAddon).toHaveBeenCalledWith(webLinksAddonInstance);
});
```

### Test Suite 3: Terminal Display

#### Test 3.1: Opens terminal in container

```typescript
test('opens terminal in container', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;

  expect(terminalInstance.open).toHaveBeenCalled();
});
```

#### Test 3.2: Fits terminal to container

```typescript
test('fits terminal to container', () => {
  const { FitAddon } = require('xterm-addon-fit');

  render(<XTerminal />);

  const fitAddonInstance = FitAddon.mock.results[0].value;

  expect(fitAddonInstance.fit).toHaveBeenCalled();
});
```

#### Test 3.3: Displays welcome message

```typescript
test('displays welcome message', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;

  expect(terminalInstance.writeln).toHaveBeenCalledWith(
    'Welcome to VM Terminal Hub'
  );
});
```

#### Test 3.4: Displays prompt

```typescript
test('displays prompt', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;

  expect(terminalInstance.write).toHaveBeenCalledWith('$ ');
});
```

### Test Suite 4: Input Handling

#### Test 4.1: Registers onData handler

```typescript
test('registers onData handler', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;

  expect(terminalInstance.onData).toHaveBeenCalled();
});
```

#### Test 4.2: Handles character input

```typescript
test('handles character input', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const onDataHandler = terminalInstance.onData.mock.calls[0][0];

  // Simulate character input
  onDataHandler('a');

  expect(terminalInstance.write).toHaveBeenCalledWith('a');
});
```

#### Test 4.3: Handles backspace

```typescript
test('handles backspace', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const onDataHandler = terminalInstance.onData.mock.calls[0][0];

  // Simulate backspace
  onDataHandler('\u007f');

  expect(terminalInstance.write).toHaveBeenCalledWith('\b \b');
});
```

#### Test 4.4: Handles enter key

```typescript
test('handles enter key', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const onDataHandler = terminalInstance.onData.mock.calls[0][0];

  // Simulate enter key
  onDataHandler('\r');

  expect(terminalInstance.write).toHaveBeenCalledWith('\r\n$ ');
});
```

#### Test 4.5: Ignores other characters

```typescript
test('ignores other characters', () => {
  const { Terminal } = require('xterm');

  render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;
  const onDataHandler = terminalInstance.onData.mock.calls[0][0];

  // Simulate other character
  onDataHandler('\t');

  // Should not write anything
  expect(terminalInstance.write).not.toHaveBeenCalledWith('\t');
});
```

### Test Suite 5: Cleanup

#### Test 5.1: Disposes terminal on unmount

```typescript
test('disposes terminal on unmount', () => {
  const { Terminal } = require('xterm');

  const { unmount } = render(<XTerminal />);

  const terminalInstance = Terminal.mock.results[0].value;

  unmount();

  expect(terminalInstance.dispose).toHaveBeenCalled();
});
```

---

# Part 2: open-manus.tsx Testing

## Test Setup

### Imports and Mocks

```typescript
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { OpenManus } from '../open-manus';

// Mock fetch globally
global.fetch = jest.fn();

/**
 * Create mock app data
 */
function createMockApp(overrides = {}) {
  return {
    id: 'app-1',
    name: 'Test App',
    status: 'Deployed',
    compute: '150 CK-Tokens',
    ...overrides
  };
}

/**
 * Mock successful fetch response
 */
function mockFetchSuccess(data: any) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  } as Response);
}

/**
 * Mock failed fetch response
 */
function mockFetchError() {
  (global.fetch as jest.Mock).mockRejectedValueOnce(
    new Error('Network error')
  );
}
```

## Detailed Test Cases for open-manus.tsx

### Test Suite 1: Component Rendering

#### Test 1.1: Component renders without errors

```typescript
describe('OpenManus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without errors', () => {
    render(<OpenManus />);

    // Component should render without throwing
    expect(screen.getByText(/OpenManus/i)).toBeInTheDocument();
  });
});
```

#### Test 1.2: Component displays header with icon

```typescript
test('displays header with icon', () => {
  render(<OpenManus />);

  expect(screen.getByText(/OpenManus/i)).toBeInTheDocument();
  expect(screen.getByText(/Building the Hyper-Simulation/i)).toBeInTheDocument();
});
```

#### Test 1.3: Component displays description

```typescript
test('displays description', () => {
  render(<OpenManus />);

  expect(screen.getByText(/Describe an application to trigger autonomous kernel proposals/i)).toBeInTheDocument();
});
```

#### Test 1.4: Component displays input field

```typescript
test('displays input field', () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  expect(input).toBeInTheDocument();
  expect(input.tagName).toBe('INPUT');
});
```

#### Test 1.5: Component displays "Build App" button

```typescript
test('displays "Build App" button', () => {
  render(<OpenManus />);

  const button = screen.getByText('Build App');
  expect(button).toBeInTheDocument();
  expect(button.tagName).toBe('BUTTON');
});
```

#### Test 1.6: Component displays "Simulation Infrastructure" section

```typescript
test('displays "Simulation Infrastructure" section', () => {
  render(<OpenManus />);

  expect(screen.getByText(/Simulation Infrastructure/i)).toBeInTheDocument();
});
```

#### Test 1.7: Component displays "No applications deployed" when empty

```typescript
test('displays "No applications deployed" when empty', () => {
  render(<OpenManus />);

  expect(screen.getByText(/No applications deployed yet/i)).toBeInTheDocument();
});
```

### Test Suite 2: Input Handling

#### Test 2.1: Input field updates appRequirement state

```typescript
test('input field updates appRequirement state', async () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  expect(input).toHaveValue('Test App');
});
```

#### Test 2.2: Input field accepts long text

```typescript
test('input field accepts long text', async () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  const longText = 'A'.repeat(1000);

  await userEvent.type(input, longText);

  expect(input).toHaveValue(longText);
});
```

#### Test 2.3: Input field clears after successful build

```typescript
test('input field clears after successful build', async () => {
  mockFetchSuccess({ response: 'App built successfully' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(input).toHaveValue('');
  });
});
```

### Test Suite 3: Build App Functionality

#### Test 3.1: "Build App" button is disabled when input is empty

```typescript
test('"Build App" button is disabled when input is empty', () => {
  render(<OpenManus />);

  const button = screen.getByText('Build App');
  expect(button).toBeDisabled();
});
```

#### Test 3.2: "Build App" button is enabled when input has text

```typescript
test('"Build App" button is enabled when input has text', async () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  expect(button).not.toBeDisabled();
});
```

#### Test 3.3: "Build App" button triggers API call

```typescript
test('"Build App" button triggers API call', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/chat',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });
});
```

#### Test 3.4: "Build App" button sends correct request body

```typescript
test('"Build App" button sends correct request body', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Build a trading app');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    const callArgs = (global.fetch as jest.Mock).mock.calls[0];
    const requestBody = JSON.parse(callArgs[1].body);

    expect(requestBody.prompt).toBe('Build application: Build a trading app');
  });
});
```

#### Test 3.5: "Build App" button shows loading state

```typescript
test('"Build App" button shows loading state', async () => {
  // Mock fetch that never resolves
  (global.fetch as jest.Mock).mockImplementation(
    () => new Promise(() => {})
  );

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Generating...')).toBeInTheDocument();
  });
});
```

#### Test 3.6: "Build App" button is disabled during loading

```typescript
test('"Build App" button is disabled during loading', async () => {
  // Mock fetch that never resolves
  (global.fetch as jest.Mock).mockImplementation(
    () => new Promise(() => {})
  );

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(button).toBeDisabled();
  });
});
```

#### Test 3.7: "Build App" button clears loading state after success

```typescript
test('"Build App" button clears loading state after success', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  // Wait for loading state
  await waitFor(() => {
    expect(screen.getByText('Generating...')).toBeInTheDocument();
  });

  // Wait for loading to clear
  await waitFor(() => {
    expect(screen.queryByText('Generating...')).not.toBeInTheDocument();
  });
});
```

#### Test 3.8: "Build App" button clears loading state after error

```typescript
test('"Build App" button clears loading state after error', async () => {
  mockFetchError();

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  // Wait for loading to clear
  await waitFor(() => {
    expect(screen.queryByText('Generating...')).not.toBeInTheDocument();
  });
});
```

### Test Suite 4: App Display

#### Test 4.1: Displays built applications

```typescript
test('displays built applications', async () => {
  mockFetchSuccess({ response: 'App built successfully' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Test App')).toBeInTheDocument();
  });
});
```

#### Test 4.2: Displays app name

```typescript
test('displays app name', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'My Custom App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('My Custom App')).toBeInTheDocument();
  });
});
```

#### Test 4.3: Displays app status

```typescript
test('displays app status', async () => {
  mockFetchSuccess({ response: 'Deployed to Hyper-Simulation' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(/Deployed to Hyper-Simulation/i)).toBeInTheDocument();
  });
});
```

#### Test 4.4: Displays compute tokens

```typescript
test('displays compute tokens', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('150 CK-Tokens')).toBeInTheDocument();
  });
});
```

#### Test 4.5: Displays multiple apps

```typescript
test('displays multiple apps', async () => {
  mockFetchSuccess({ response: 'App 1 built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);

  // Build first app
  await userEvent.type(input, 'App 1');
  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('App 1')).toBeInTheDocument();
  });

  // Build second app
  await userEvent.clear(input);
  await userEvent.type(input, 'App 2');
  mockFetchSuccess({ response: 'App 2 built' });
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('App 2')).toBeInTheDocument();
  });
});
```

#### Test 4.6: Hides "No applications deployed" when apps exist

```typescript
test('hides "No applications deployed" when apps exist', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.queryByText(/No applications deployed yet/i)).not.toBeInTheDocument();
  });
});
```

### Test Suite 5: Error Handling

#### Test 5.1: Handles API errors gracefully

```typescript
test('handles API errors gracefully', async () => {
  mockFetchError();

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(/Error: TrainLLM Backend Offline/i)).toBeInTheDocument();
  });
});
```

#### Test 5.2: Creates fallback app on error

```typescript
test('creates fallback app on error', async () => {
  mockFetchError();

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Test App')).toBeInTheDocument();
    expect(screen.getByText(/0 CK-Tokens/)).toBeInTheDocument();
  });
});
```

#### Test 5.3: Logs API errors to console

```typescript
test('logs API errors to console', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
  mockFetchError();

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to connect to TrainLLM backend')
    );
  });

  consoleSpy.mockRestore();
});
```

### Test Suite 6: Edge Cases

#### Test 6.1: Handles empty input after typing

```typescript
test('handles empty input after typing', async () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');
  await userEvent.clear(input);

  const button = screen.getByText('Build App');
  expect(button).toBeDisabled();
});
```

#### Test 6.2: Handles rapid button clicks

```typescript
test('handles rapid button clicks', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test App');

  const button = screen.getByText('Build App');

  // Click multiple times rapidly
  await userEvent.click(button);
  await userEvent.click(button);
  await userEvent.click(button);

  // Should only make one request (button disabled during loading)
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});
```

#### Test 6.3: Handles special characters in input

```typescript
test('handles special characters in input', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  await userEvent.type(input, 'Test @#$%^&*() App');

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText('Test @#$%^&*() App')).toBeInTheDocument();
  });
});
```

#### Test 6.4: Handles very long input

```typescript
test('handles very long input', async () => {
  mockFetchSuccess({ response: 'App built' });

  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  const longText = 'A'.repeat(10000);

  await userEvent.type(input, longText);

  const button = screen.getByText('Build App');
  await userEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(longText.substring(0, 30))).toBeInTheDocument();
  });
});
```

### Test Suite 7: Accessibility

#### Test 7.1: Input field has accessible label

```typescript
test('input field has accessible label', () => {
  render(<OpenManus />);

  const input = screen.getByPlaceholderText(/e.g. Build a decentralized trade market/i);
  expect(input).toBeInTheDocument();
});
```

#### Test 7.2: Button has accessible label

```typescript
test('button has accessible label', () => {
  render(<OpenManus />);

  const button = screen.getByRole('button', { name: /build app/i });
  expect(button).toBeInTheDocument();
});
```

## Test Configuration

### jest.config.js (same as other components)

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

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

module.exports = createJestConfig(customJestConfig)
```

## Running Tests

```bash
# Run all component tests
npm test

# Run specific test file
npm test terminal.test.tsx
npm test open-manus.test.tsx

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test
npm test -t "displays welcome message"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

### terminal.tsx
1. **Mocking**: Mock xterm.js to avoid DOM manipulation
2. **Initialization**: Verify terminal is initialized correctly
3. **Event Handling**: Test input handling (characters, backspace, enter)
4. **Cleanup**: Verify proper disposal on unmount
5. **Theme**: Verify custom theme is applied

### open-manus.tsx
1. **User-Centric**: Test from user's perspective
2. **Async Handling**: Properly wait for async operations
3. **Mocking**: Mock `fetch` to avoid real HTTP requests
4. **Error Testing**: Test both success and error paths
5. **Edge Cases**: Test empty input, rapid clicks, special characters
6. **Accessibility**: Verify accessible labels and structure
7. **Loading States**: Test loading states for good UX

## Notes

### terminal.tsx
- xterm.js is mocked to avoid complex DOM manipulation
- Terminal initialization is verified with correct options
- Input handling is tested for different key types
- Cleanup is verified to prevent memory leaks
- Theme colors use CSS variables for customization

### open-manus.tsx
- `fetch` is mocked globally to avoid real HTTP requests
- `userEvent` is used for realistic user interactions
- `waitFor` is used to handle async operations
- Tests verify what users see, not internal state
- Error handling is tested with fallback behavior
- Loading states are tested to ensure good UX
- Accessibility is verified with role-based queries
