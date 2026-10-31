import { generateKeyPairSync, sign } from 'crypto';
import { blake3 } from 'blake3';
import { authorize } from '../../governance';

function makeAttestation(action: string, includePublicKey = true) {
  const { publicKey, privateKey } = generateKeyPairSync('ed25519');
  const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();
  const privateKeyPem = privateKey.export({ type: 'pkcs8', format: 'pem' }).toString();
  const base = {
    cycle: 1,
    invariants: { deterministicBuild: true, encryptedIO: true },
    policyProofs: { [action]: true }
  };
  const proofHash = blake3(JSON.stringify(base)).toString('hex');
  const signature = sign(null, Buffer.from(JSON.stringify(base)), privateKey).toString('hex');
  return {
    att: { ...base, proofHash, signature, ...(includePublicKey ? { publicKey: publicKeyPem } : {}) },
    publicKeyPem
  };
}

describe('action-bound attestation governance', () => {
  test('accepts only an attestation signed by the configured trust root for the exact action', () => {
    const { att, publicKeyPem } = makeAttestation('deployment.promote');
    expect(authorize(att, 'deployment.promote', publicKeyPem)).toBe(true);
  });

  test('rejects a different action even when the attestation is otherwise valid', () => {
    const { att, publicKeyPem } = makeAttestation('deployment.promote');
    expect(authorize(att, 'capability.issue', publicKeyPem)).toBe(false);
  });

  test('rejects a self-signed attacker key that is not the configured trust root', () => {
    const { att } = makeAttestation('deployment.promote');
    const attacker = makeAttestation('deployment.promote');
    expect(authorize(att, 'deployment.promote', attacker.publicKeyPem)).toBe(false);
  });

  test('rejects attestations when no trust root is configured', () => {
    const { att } = makeAttestation('deployment.promote');
    expect(authorize(att, 'deployment.promote', '')).toBe(false);
  });

  test('rejects missing or empty policy proofs', () => {
    const { att, publicKeyPem } = makeAttestation('deployment.promote');
    att.policyProofs = {};
    expect(authorize(att, 'deployment.promote', publicKeyPem)).toBe(false);
  });

  test('rejects truthy non-boolean invariant values', () => {
    const { att, publicKeyPem } = makeAttestation('deployment.promote');
    att.invariants.deterministicBuild = 'true' as unknown as boolean;
    expect(authorize(att, 'deployment.promote', publicKeyPem)).toBe(false);
  });

  test('rejects payload tampering after signing', () => {
    const { att, publicKeyPem } = makeAttestation('deployment.promote');
    att.cycle = 2;
    expect(authorize(att, 'deployment.promote', publicKeyPem)).toBe(false);
  });
});
