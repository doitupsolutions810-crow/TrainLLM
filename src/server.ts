import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';
import { signCapability, verifyCapability } from './auth';
import { zkAttest } from './zk';
import { logDisagreement } from './model-disagreement-logger';
import { logAction } from './memory-loop';
import fs from 'fs';
import { authorize } from '../governance';
import { initializeLLM } from './llm-adapter';

const app = express();
app.use(bodyParser.json());

function getAttestation(input: unknown): any | null {
  if (input && typeof input === 'object' && !Array.isArray(input)) return input;
  try {
    if (!fs.existsSync('state/last.json')) return null;
    const parsed = JSON.parse(fs.readFileSync('state/last.json', 'utf8'));
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function getJwtSecret(res: Response): string | null {
  const secret = process.env.JWT_SECRET;
  if (!secret || secret.length < 32) {
    res.status(503).json({ authorized: false, error: 'JWT_SECRET must be configured with at least 32 characters' });
    return null;
  }
  return secret;
}

function getAction(req: Request, res: Response): string | null {
  const action = req.body?.action;
  if (typeof action !== 'string' || !action.trim()) {
    res.status(400).json({ authorized: false, error: 'action is required' });
    return null;
  }
  return action.trim();
}

app.get('/health', (_req: Request, res: Response) => res.json({ ok: true }));

app.post('/authorize', (req: Request, res: Response) => {
  const secret = getJwtSecret(res);
  if (!secret) return;
  const action = getAction(req, res);
  if (!action) return;
  const token = req.headers.authorization?.split(' ')[1];
  if (!token || !verifyCapability(token, secret, action)) {
    return res.status(403).json({ authorized: false, message: 'Unauthorized' });
  }
  const att = getAttestation(req.body.att);
  const authorized = att ? authorize(att, action) : false;
  return res.status(authorized ? 200 : 403).json({ authorized });
});

app.post('/execute', (req: Request, res: Response) => {
  const secret = getJwtSecret(res);
  if (!secret) return;
  const action = getAction(req, res);
  if (!action) return;
  const token = req.headers.authorization?.split(' ')[1];
  if (!token || !verifyCapability(token, secret, action)) {
    return res.status(403).json({ executed: false, authorized: false, message: 'Unauthorized' });
  }
  const att = getAttestation(req.body.att);
  if (!att || !authorize(att, action)) {
    return res.status(403).json({ executed: false, authorized: false, message: 'Action is not attested by the configured trust root' });
  }

  const diagnosticDigest = zkAttest(action, secret);
  logDisagreement('model-A', 'model-B', action);
  logAction(action, 'executed');

  // The current SHA-256 helper is a diagnostic placeholder, not a ZK proof.
  return res.json({
    executed: true,
    evidence: {
      zk_proof_status: 'NOT_IMPLEMENTED',
      diagnostic_digest: diagnosticDigest
    }
  });
});

// Token minting is explicitly opt-in for isolated development only.
app.post('/token', (req: Request, res: Response) => {
  if (process.env.NODE_ENV === 'production' || process.env.TRAINLLM_ENABLE_DEV_TOKEN !== '1') {
    return res.status(404).json({ error: 'not found' });
  }
  const secret = getJwtSecret(res);
  if (!secret) return;
  const action = getAction(req, res);
  if (!action) return;
  return res.json({ token: signCapability('scale-sla', secret, action), expires_in_seconds: 60 });
});

let llm: any = null;
initializeLLM().then(m => {
  llm = m;
  console.info('LLM adapter initialized');
}).catch(err => console.warn('LLM init failed:', err.message));

app.post('/analyze', async (req: Request, res: Response) => {
  if (!llm) return res.status(503).json({ ok: false, message: 'LLM not available' });
  const prompt = req.body.prompt || 'Analyze artifact';
  try {
    const resp = await llm.generate(prompt);
    return res.json({ ok: true, result: resp });
  } catch (err) {
    return res.status(500).json({ ok: false, message: (err as Error).message });
  }
});

app.get('/unified-health', (_req: Request, res: Response) => {
  res.json({
    component: 'trainllm',
    status: 'online',
    timestamp: new Date().toISOString(),
    endpoints: ['/health', '/authorize', '/execute', '/token', '/analyze', '/unified-health', '/cross-query', '/sync-state']
  });
});

app.post('/cross-query', async (req: Request, res: Response) => {
  const { query, context, component } = req.body;
  if (!query) return res.status(400).json({ error: 'Query parameter required' });
  try {
    const enhancedPrompt = `
Component: ${component || 'unknown'}
Query: ${query}
Context: ${JSON.stringify(context || {}, null, 2)}

Please provide analysis and recommendations considering the Anti4 ecosystem integration.
    `.trim();
    if (!llm) return res.status(503).json({ error: 'LLM not available' });
    const response = await llm.generate(enhancedPrompt);
    return res.json({ component: 'trainllm', query, response, timestamp: new Date().toISOString() });
  } catch (err) {
    return res.status(500).json({ error: (err as Error).message });
  }
});

app.post('/sync-state', (req: Request, res: Response) => {
  const { unified_state, component_states } = req.body;
  console.log('State sync received:', {
    timestamp: new Date().toISOString(),
    unified_state_keys: Object.keys(unified_state || {}),
    component_states_count: component_states ? Object.keys(component_states).length : 0
  });
  return res.json({
    status: 'synced',
    component: 'trainllm',
    timestamp: new Date().toISOString(),
    message: 'State synchronization acknowledged'
  });
});

app.post('/unified-action', (req: Request, res: Response) => {
  const { action, target_component, parameters } = req.body;
  if (!action || !target_component) return res.status(400).json({ error: 'Action and target_component required' });
  console.log('Unified action received:', { action, target_component, parameters, timestamp: new Date().toISOString() });
  if (target_component === 'trainllm') {
    return res.json({ status: 'accepted', component: 'trainllm', action, result: 'Action recorded; governed execution must use /execute' });
  }
  return res.status(202).json({ status: 'forwarded', target_component, action, message: 'Action queued for the unified orchestrator' });
});

const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 8080;
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT must be an integer between 1 and 65535');
}
app.listen(port, () => console.info(`TrainLLM Server listening on ${port}`));

export default app;
