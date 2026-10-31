import { signCapability, verifyCapability } from '../src/auth';
import { zkAttest } from '../src/zk';
import { logAction, readActions } from '../src/memory-loop';
import { logDisagreement } from '../src/model-disagreement-logger';
import fs from 'fs';

function run() {
  const secret = 'smoke-secret';
  const action = 'smoke.verify';
  const token = signCapability('scale-sla', secret, action);
  if (!verifyCapability(token, secret, action)) throw new Error('action-scoped token verification failed');
  if (verifyCapability(token, secret, 'smoke.escalate')) throw new Error('action substitution was accepted');
  console.info('Action-scoped token verification passed');

  const diagnostic = zkAttest(action, secret);
  console.info('ZK placeholder diagnostic:', diagnostic.slice(0, 16));

  logDisagreement('model-A', 'model-B', action);
  logAction(action, 'authorized_not_executed');

  const actions = readActions();
  console.info('Actions:', actions.length);

  if (fs.existsSync('state/last.json')) console.info('Attestation present');
  else console.warn('No attestation found (run attestor.ts)');
}

run();
