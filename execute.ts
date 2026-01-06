import { authorize } from './governance';
import { safeReadJsonSync } from './utils/fs';

const att = safeReadJsonSync('state/last.json');

if (!att || !authorize(att, 'scale-sla')) {
  console.error('Authorization failed for scale-sla; aborting.');
  process.exit(1);
}

try {
  require('./actions/scale-sla').run();
} catch (err) {
  console.error('Failed to execute action scale-sla:', (err as Error).message);
  process.exit(1);
}

// Additional execution logic
export function executeAction(att: any, action: string) {
  if (authorize(att, action)) {
    try {
      return require(`./actions/${action}`).run();
    } catch (err) {
      console.error('Action execution failed:', (err as Error).message);
      return false;
    }
  }
  return false;
}
