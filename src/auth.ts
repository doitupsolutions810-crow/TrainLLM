import jwt from 'jsonwebtoken';

function requireAction(action: string): string {
  if (typeof action !== 'string' || !action.trim()) {
    throw new Error('an exact action is required for every capability token');
  }
  return action.trim();
}

export function signCapability(capability: string, secret: string, action: string): string {
  return jwt.sign(
    { capability, action: requireAction(action) },
    secret,
    { algorithm: 'HS256', expiresIn: '60s', issuer: 'trainllm', audience: 'trainllm' }
  );
}

export function verifyCapability(token: string, secret: string, requiredAction: string): boolean {
  try {
    const action = requireAction(requiredAction);
    const decoded = jwt.verify(token, secret, {
      algorithms: ['HS256'],
      issuer: 'trainllm',
      audience: 'trainllm'
    }) as jwt.JwtPayload;

    return decoded.capability === 'scale-sla' && decoded.action === action;
  } catch {
    return false;
  }
}
