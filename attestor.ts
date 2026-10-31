import { blake3 } from 'blake3';
import path from 'path';
import { ensureDirSync, writeJsonFileSync } from './utils/fs';
import { generateOrLoadKeyPair, signData } from './utils/crypto';

const authorizedActions = [...new Set(
  (process.env.TRAINLLM_ATTESTED_ACTIONS || '')
    .split(',')
    .map(action => action.trim())
    .filter(Boolean)
)];

const baseAtt = {
  cycle: 0,
  artifact: process.env.ARTIFACT_HASH || 'unknown',
  previousHash: null,
  invariants: {
    deterministicBuild: true,
    encryptedIO: true,
    nodeIsolation: true
  },
  // No action is authorized by default. A trusted signer must explicitly
  // configure the actions included in this signed attestation.
  policyProofs: Object.fromEntries(authorizedActions.map(action => [action, true]))
};

try {
  ensureDirSync(path.join('shared', 'attestations'));
  ensureDirSync('state');
  ensureDirSync(path.join('state', 'keys'));

  const proofHash = blake3(JSON.stringify(baseAtt)).toString('hex');
  const att: Record<string, unknown> = { ...baseAtt, proofHash };

  const { publicKeyPem, privateKeyPem } = generateOrLoadKeyPair(path.join('state', 'keys'));
  const signature = signData(JSON.stringify(baseAtt), privateKeyPem);
  att.signature = signature.toString('hex');
  att.publicKey = publicKeyPem;

  writeJsonFileSync(path.join('shared', 'attestations', 'node1-cycle0.json'), att, { spaces: 2 });
  writeJsonFileSync(path.join('state', 'last.json'), att, { spaces: 2 });

  console.info('Attestation written with action-scoped policy proofs.');
} catch (err) {
  console.error('Failed to create attestation:', (err as Error).message);
  process.exit(1);
}
