import { blake3 } from 'blake3';
import { verifySignature } from './utils/crypto';

/**
 * Verify an action-scoped attestation against an operator-pinned trust root.
 * The public key embedded in the attestation is metadata only; it is never
 * used as the trust anchor.
 */
export function authorize(
  att: any,
  action: string,
  trustedPublicKeyInput?: string
): boolean {
  try {
    const trustedPublicKey = (trustedPublicKeyInput ?? process.env.TRAINLLM_ATTESTATION_PUBLIC_KEY ?? '')
      .replace(/\\n/g, '\n')
      .trim();

    if (!trustedPublicKey || !att || typeof att !== 'object') return false;
    if (typeof action !== 'string' || !action.trim()) return false;
    if (typeof att.publicKey !== 'string' || att.publicKey.trim() !== trustedPublicKey) return false;
    if (typeof att.proofHash !== 'string' || !/^[0-9a-f]{64}$/i.test(att.proofHash)) return false;
    if (typeof att.signature !== 'string' || !/^[0-9a-f]{128}$/i.test(att.signature)) return false;

    const invariants = att.invariants;
    if (!invariants || typeof invariants !== 'object' || Array.isArray(invariants)) return false;
    const invariantEntries = Object.entries(invariants);
    if (invariantEntries.length === 0 || !invariantEntries.every(([, value]) => value === true)) return false;

    const policyProofs = att.policyProofs;
    if (!policyProofs || typeof policyProofs !== 'object' || Array.isArray(policyProofs)) return false;
    if (policyProofs[action] !== true) return false;

    const copy = { ...att };
    delete copy.proofHash;
    delete copy.signature;
    delete copy.publicKey;

    const payload = JSON.stringify(copy);
    const expected = blake3(payload).toString('hex');
    if (expected !== att.proofHash) return false;

    return verifySignature(payload, Buffer.from(att.signature, 'hex'), trustedPublicKey);
  } catch (err) {
    console.error('authorize error:', (err as Error).message);
    return false;
  }
}

export function validateAction(att: any, action: string): boolean {
  return authorize(att, action);
}
