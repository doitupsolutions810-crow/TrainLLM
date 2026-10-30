import jwt from 'jsonwebtoken';

/** Capabilities this TrainLLM instance will sign or accept. */
export const ALLOWED_CAPABILITIES = new Set([
  'scale-sla',
  'observe-only',
  'evolve-propose',
]);

export function signCapability(capability: string, secret: string): string {
  if (!ALLOWED_CAPABILITIES.has(capability)) {
    throw new Error(`Refusing to sign unknown capability: ${capability}`);
  }
  return jwt.sign({ capability }, secret, { algorithm: 'HS256' });
}

export function verifyCapability(token: string, secret: string): boolean {
  try {
    const decoded = jwt.verify(token, secret) as { capability: string };
    // Check the token's actual claimed capability against the allow-list,
    // not a hardcoded literal. A validly signed token for any allowed
    // capability must verify.
    return ALLOWED_CAPABILITIES.has(decoded.capability);
  } catch (err) {
    return false;
  }
}

export function capabilityFromToken(token: string, secret: string): string | null {
  try {
    const decoded = jwt.verify(token, secret) as { capability: string };
    return ALLOWED_CAPABILITIES.has(decoded.capability) ? decoded.capability : null;
  } catch (err) {
    return null;
  }
}
