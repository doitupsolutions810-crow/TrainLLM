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

const port = process.env.PORT ? parseInt(process.env.PORT) : 8080;
app.listen(port, () => console.info(`Server listening on ${port}`));

export default app;
