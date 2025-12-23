import { signCapability } from '../src/auth';
import { zkAttest } from '../src/zk';
import { logAction, readActions } from '../src/memory-loop';
import { logDisagreement } from '../src/model-disagreement-logger';
import fs from 'fs';

function run() {
  const secret = 'smoke-secret';
  const token = signCapability('scale-sla', secret);
  console.info('Token:', token.slice(0, 30) + '...');

  const z = zkAttest('scale-sla', secret);
  console.info('ZK placeholder:', z.slice(0, 16));

  logDisagreement('model-A', 'model-B', 'scale-sla');
  logAction('scale-sla', 'ok');

  const actions = readActions();
  console.info('Actions:', actions.length);

  // check attestation file exists
  if (fs.existsSync('state/last.json')) console.info('Attestation present');
  else console.warn('No attestation found (run attestor.ts)');
}

run();
