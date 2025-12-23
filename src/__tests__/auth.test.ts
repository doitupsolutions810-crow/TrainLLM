import { signCapability, verifyCapability } from '../auth';

describe('auth capability', () => {
  test('sign and verify', () => {
    const secret = 'test-secret';
    const token = signCapability('scale-sla', secret);
    expect(verifyCapability(token, secret)).toBe(true);
  });

  test('invalid token', () => {
    expect(verifyCapability('bad-token', 'test-secret')).toBe(false);
  });
});
