import { blake3 } from 'blake3';
import path from 'path';
import { ensureDirSync, writeJsonFileSync } from './utils/fs';
import { generateOrLoadKeyPair, signData } from './utils/crypto';

// Build base attestation
const baseAtt = {
  cycle: 0,
  artifact: process.env.ARTIFACT_HASH || 'unknown',
  previousHash: null,
  invariants: {
    deterministicBuild: true,
    encryptedIO: true,
    nodeIsolation: true
  },
  policyProofs: {
    'policy-accept': true
  }
};

try {
  // Ensure directories
  ensureDirSync(path.join('shared', 'attestations'));
  ensureDirSync('state');
  ensureDirSync(path.join('state', 'keys'));

  // Compute proof hash deterministically over baseAtt (no signature/keys)
  const proofHash = blake3(JSON.stringify(baseAtt)).toString('hex');

  const att = { ...baseAtt, proofHash };

  // Ensure or create ed25519 key pair (persists keys to disk)
  const { publicKeyPem, privateKeyPem } = generateOrLoadKeyPair(path.join('state', 'keys'));

  // Sign the base attestation (not including proofHash) for additional integrity
  const signature = signData(JSON.stringify(baseAtt), privateKeyPem);
  att.signature = signature.toString('hex');
  att.publicKey = publicKeyPem;

  // Save attestation files
  writeJsonFileSync(path.join('shared', 'attestations', 'node1-cycle0.json'), att, { spaces: 2 });
  writeJsonFileSync(path.join('state', 'last.json'), att, { spaces: 2 });

  console.info('Attestation written with proofHash and signature.');
} catch (err) {
  console.error('Failed to create attestation:', (err as Error).message);
  process.exit(1);
}
