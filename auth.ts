import jwt from 'jsonwebtoken';
import { generateKeyPairSync } from 'crypto';

type KeyPair = { publicKey: string; privateKey: string };

let cached: KeyPair | null = null;

export function getKeyPair(): KeyPair {
  if (!cached) {
    const { publicKey, privateKey } = generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    cached = { publicKey, privateKey };
  }
  return cached;
}

export function signCapability(payload: object): string {
  const { privateKey } = getKeyPair();
  return jwt.sign(payload, privateKey, { algorithm: 'RS256', expiresIn: '1h' });
}

export function verifyCapability(token: string): object {
  const { publicKey } = getKeyPair();
  return jwt.verify(token, publicKey, { algorithms: ['RS256'] });
}

export function publicKeyPem(): string {
  return getKeyPair().publicKey;
}
