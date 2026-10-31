import { signCapability, verifyCapability } from '../auth';

describe('action-scoped capability tokens', () => {
  test('signs and verifies only the exact action', () => {
    const secret = 'test-secret';
    const token = signCapability('scale-sla', secret, 'deployment.promote');
    expect(verifyCapability(token, secret, 'deployment.promote')).toBe(true);
    expect(verifyCapability(token, secret, 'capability.issue')).toBe(false);
  });

  test('rejects tokens when the requested action is missing', () => {
    const secret = 'test-secret';
    const token = signCapability('scale-sla', secret, 'deployment.promote');
    expect(verifyCapability(token, secret, '')).toBe(false);
  });

  test('invalid token', () => {
    expect(verifyCapability('bad-token', 'test-secret', 'deployment.promote')).toBe(false);
  });
});
