import { blake3 } from 'blake3';
import { verifySignature } from './utils/crypto';

export function authorize(att: any, action: string) {
  try {
    if (!Object.values(att.invariants ?? {}).every(Boolean)) return false;
    if (!att.policyProofs || !Object.keys(att.policyProofs).length) return false;

    const copy = { ...att } as any;
    delete copy.proofHash;
    delete copy.signature;
    delete copy.publicKey;

    // Incorporate action into the authorized binding
    copy.authorizedAction = action;

    const expected = blake3(JSON.stringify(copy)).toString('hex);
    if (expected !== att.proofHash) return false;

    if (att.signature && att.publicKey) {
      const sigBuf = Buffer.from(att.signature, 'hex);
      const ok = verifySignature(JSON.stringify(copy), sigBuf, att.publicKey);
      if (!ok) return false;
    }

    return true;
  } catch (err) {
    console.error('authorize error:', (err as Error).message);
    return false;
  }
}

export function validateAction(att: any, action: string) {
  if (!authorize(att, action)) {
    console.error('Unauthorized action:', action);
    return false;
  }
  return true;
}
