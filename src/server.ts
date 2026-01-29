import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';
import { signCapability, verifyCapability } from './auth';
import { zkAttest } from './zk';
import { logDisagreement } from './model-disagreement-logger';
import { logAction } from './memory-loop';
import fs from 'fs';
import { authorize } from '../governance';

const app = express();
app.use(bodyParser.json());

app.get('/health', (req: Request, res: Response) => res.json({ ok: true }));

app.post('/authorize', (req: Request, res: Response) => {
  const token = req.headers.authorization?.split(' ')[1];
  const secret = process.env.JWT_SECRET || 'dev-secret';
  const action = req.body.action;
  const att = req.body.att || (fs.existsSync('state/last.json') ? JSON.parse(fs.readFileSync('state/last.json', 'utf8')) : null);

  if (!token || !verifyCapability(token, secret)) {
    return res.status(403).json({ authorized: false, message: 'Unauthorized' });
  }

  const authorized = att ? authorize(att, action) : false;
  res.json({ authorized });
});

app.post('/execute', (req: Request, res: Response) => {
  const token = req.headers.authorization?.split(' ')[1];
  const secret = process.env.JWT_SECRET || 'dev-secret';
  const action = req.body.action;

  if (!token || !verifyCapability(token, secret)) {
    return res.status(403).json({ authorized: false, message: 'Unauthorized' });
  }

  const zKHash = zkAttest(action, secret);
  logDisagreement('model-A', 'model-B', action);
  logAction(action, 'executed');

  res.json({ executed: true, zk: zKHash });
});

// simple route to generate a capability token (dev only)
app.post('/token', (req: Request, res: Response) => {
  const secret = process.env.JWT_SECRET || 'dev-secret';
  const token = signCapability('scale-sla', secret);
  res.json({ token });
});

import { initializeLLM } from './llm-adapter';

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
    res.json({ ok: true, result: resp });
  } catch (err) {
    res.status(500).json({ ok: false, message: (err as Error).message });
  }
});

// Unified LLM Integration Endpoints
app.get('/unified-health', (req: Request, res: Response) => {
  res.json({
    component: 'trainllm',
    status: 'online',
    timestamp: new Date().toISOString(),
    endpoints: [
      '/health',
      '/authorize',
      '/execute',
      '/token',
      '/analyze',
      '/unified-health',
      '/cross-query',
      '/sync-state'
    ]
  });
});

app.post('/cross-query', async (req: Request, res: Response) => {
  const { query, context, component } = req.body;

  if (!query) {
    return res.status(400).json({ error: 'Query parameter required' });
  }

  try {
    // Enhanced LLM query with cross-component context
    const enhancedPrompt = `
Component: ${component || 'unknown'}
Query: ${query}
Context: ${JSON.stringify(context || {}, null, 2)}

Please provide analysis and recommendations considering the Anti4 ecosystem integration.
    `.trim();

    if (!llm) {
      return res.status(503).json({ error: 'LLM not available' });
    }

    const response = await llm.generate(enhancedPrompt);
    res.json({
      component: 'trainllm',
      query: query,
      response: response,
      timestamp: new Date().toISOString()
    });

  } catch (err) {
    res.status(500).json({ error: (err as Error).message });
  }
});

app.post('/sync-state', (req: Request, res: Response) => {
  const { unified_state, component_states } = req.body;

  // Log cross-component state synchronization
  console.log('State sync received:', {
    timestamp: new Date().toISOString(),
    unified_state_keys: Object.keys(unified_state || {}),
    component_states_count: component_states ? Object.keys(component_states).length : 0
  });

  res.json({
    status: 'synced',
    component: 'trainllm',
    timestamp: new Date().toISOString(),
    message: 'State synchronization acknowledged'
  });
});

app.post('/unified-action', (req: Request, res: Response) => {
  const { action, target_component, parameters } = req.body;

  if (!action || !target_component) {
    return res.status(400).json({ error: 'Action and target_component required' });
  }

  // Log unified actions
  console.log('Unified action received:', {
    action,
    target_component,
    parameters,
    timestamp: new Date().toISOString()
  });

  // Execute action based on target component
  if (target_component === 'trainllm') {
    // Handle internal TrainLLM actions
    res.json({
      status: 'executed',
      component: 'trainllm',
      action: action,
      result: 'Action processed internally'
    });
  } else {
    // Forward to other components via unified orchestrator
    res.json({
      status: 'forwarded',
      target_component,
      action,
      message: 'Action forwarded to unified orchestrator'
    });
  }
});

const port = process.env.PORT ? parseInt(process.env.PORT) : 8080;
app.listen(port, () => console.info(`TrainLLM Server listening on ${port}`));

export default app;
