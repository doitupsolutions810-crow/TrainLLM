import fs from 'fs';
import path from 'path';
import { blake3 } from 'blake3';
import { Attestation } from './types';

export function createGenesis(): Attestation {
  const base: Attestation = {
    cycle: 0,
    artifact: process.env.ARTIFACT_HASH || 'unknown',
    previousHash: null,
    invariants: {
      deterministicBuild: true,
      encryptedIO: true,
      nodeIsolation: true
    },
    policyProofs: { 'policy-accept': true }
  };

  const proofHash = blake3(JSON.stringify(base)).toString('hex');
  const att = { ...base, proofHash };
  const outDir = path.join(process.cwd(), 'state');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, 'last.json'), JSON.stringify(att, null, 2));
  return att;
}

export function readLast(): Attestation | null {
  const p = path.join(process.cwd(), 'state', 'last.json');
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8')) as Attestation;
  } catch (err) {
    return null;
  }
}
