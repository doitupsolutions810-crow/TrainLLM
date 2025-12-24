import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

export function generateOrLoadKeyPair(dir: string) {
  const privPath = path.join(dir, 'private.pem');
  const pubPath = path.join(dir, 'public.pem');

  if (fs.existsSync(privPath) && fs.existsSync(pubPath)) {
    const privateKeyPem = fs.readFileSync(privPath, 'utf8');
    const publicKeyPem = fs.readFileSync(pubPath, 'utf8');
    return { privateKeyPem, publicKeyPem };
  }

  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();
  const privateKeyPem = privateKey.export({ type: 'pkcs8', format: 'pem' }).toString();

  fs.writeFileSync(privPath, privateKeyPem, { mode: 0o600 });
  fs.writeFileSync(pubPath, publicKeyPem);

  return { privateKeyPem, publicKeyPem };
}

export function signData(message: string | Buffer, privateKeyPem: string) {
  // ed25519 uses null algorithm in node's sign when using KeyObject
  const keyObj = crypto.createPrivateKey({ key: privateKeyPem, format: 'pem', type: 'pkcs8' });
  return crypto.sign(null, Buffer.from(message), keyObj);
}

export function verifySignature(message: string | Buffer, signature: Buffer, publicKeyPem: string) {
  const keyObj = crypto.createPublicKey({ key: publicKeyPem, format: 'pem', type: 'spki' });
  return crypto.verify(null, Buffer.from(message), keyObj, signature);
}
