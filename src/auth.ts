import jwt from 'jsonwebtoken';

export function signCapability(capability: string, secret: string, action?: string): string {
  return jwt.sign(
    { capability, action },
    secret,
    { algorithm: 'HS256', expiresIn: '60s', issuer: 'trainllm', audience: 'trainllm' }
  );
}

export function verifyCapability(token: string, secret: string, requiredAction?: string): boolean {
  try {
    const decoded = jwt.verify(token, secret, {
      algorithms: ['HS256'],
      issuer: 'trainllm',
      audience: 'trainllm'
    }) as jwt.JwtPayload;

    if (decoded.capability !== 'scale-sla') return false;
    if (requiredAction !== undefined && decoded.action !== requiredAction) return false;
    return true;
  } catch {
    return false;
  }
}
