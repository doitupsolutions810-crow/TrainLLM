import fs from 'fs';
import path from 'path';

export function compileAttestation(att: any) {
  return [
    {
      messages: [
        { role: 'system', content: 'Verify attestation chains.' },
        { role: 'user', content: JSON.stringify(att, null, 2) },
        {
          role: 'assistant',
          content: att.previousHash ? 'Chain valid' : 'Genesis attestation'
        }
      ]
    },
    {
      messages: [
        { role: 'system', content: 'Check invariants.' },
        { role: 'user', content: JSON.stringify(att.invariants) },
        {
          role: 'assistant',
          content: Object.values(att.invariants ?? {}).every(Boolean)
            ? 'Valid state'
            : 'Invalid state'
        }
      ]
    },
    {
      messages: [
        { role: 'system', content: 'Enforce governance.' },
        { role: 'user', content: JSON.stringify(att.policyProofs) },
        {
          role: 'assistant',
          content: att.policyProofs && Object.keys(att.policyProofs).length
            ? 'Governance allowed'
            : 'Governance denied'
        }
      ]
    }
  ];
}

// Process all attestations into a training jsonl
const outPath = path.join('shared', 'attestations', 'training.jsonl');
try {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const out = fs.createWriteStream(outPath);

  for (const f of fs.readdirSync('shared/attestations')) {
    if (!f.endsWith('.json')) continue;
    if (f === path.basename(outPath)) continue; // skip the output file if it's in the same dir

    try {
      const raw = fs.readFileSync(path.join('shared/attestations', f), 'utf8');
      const att = JSON.parse(raw);
      compileAttestation(att).forEach(e => out.write(JSON.stringify(e) + '\n'));
    } catch (err) {
      console.warn('Skipping invalid attestation file', f, (err as Error).message);
      continue;
    }
  }

  out.end();
  console.info('Compiled attestations into', outPath);
} catch (err) {
  console.error('Failed to compile attestations:', (err as Error).message);
}
