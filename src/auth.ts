import jwt from 'jsonwebtoken';

export function signCapability(capability: string, secret: string): string {
  return jwt.sign({ capability }, secret, { algorithm: 'HS256' });
}

export function verifyCapability(token: string, secret: string): boolean {
  try {
    const decoded = jwt.verify(token, secret);
    return (decoded as { capability: string }).capability === 'scale-sla';
  } catch (err) {
    return false;
  }
}
