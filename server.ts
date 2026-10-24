import express from 'express';
import { zkAttest, assertZkImplemented } from './zk';
import { signCapability, verifyCapability, publicKeyPem } from './auth';
import { authorize } from './governance';
import { logDisagreement } from './src/model-disagreement-logger';

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', zkImplemented: false });
});

app.get('/.well-known/public-key', (_req, res) => {
  res.type('text/plain').send(publicKeyPem());
});

app.post('/token', (req, res) => {
  res.status(501).json({
    error: 'token issuance requires an authenticated principal; unauthenticated minting removed'
  });
});

app.post('/execute', (req, res) => {
  const { token, action, target } = req.body ?? {};
  if (!token || !action) {
    return res.status(400).json({ error: 'token and action required' });
  }
  let payload: any;
  try {
    payload = verifyCapability(token);
  } catch {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
  if (!authorize(payload.attestation ?? payload, action)) {
    return res.status(403).json({ error: 'action not authorized by attestation' });
  }
  const proof = zkAttest(action, process.env.ZK_SECRET ?? '');
  try {
    assertZkImplemented(proof);
  } catch (err) {
    return res.status(501).json({ error: (err as Error).message, proof });
  }
  res.json({ status: 'executed', action, target: target ?? null, proof });
});

app.post('/unified-action', (req, res) => {
  const { token, action, target } = req.body ?? {};
  if (!token || !action) {
    return res.status(400).json({ error: 'token and action required' });
  }
  let payload: any;
  try {
    payload = verifyCapability(token);
  } catch {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
  if (!authorize(payload.attestation ?? payload, action)) {
    return res.status(403).json({ error: 'action not authorized by attestation' });
  }
  if (target === 'internal') {
    return res.status(501).json({
      error: 'internal targets are not executed by this route; no synthetic executed status'
    });
  }
  res.status(501).json({ error: 'execution backend not wired; refusing to claim executed' });
});

app.post('/log-disagreement', (req, res) => {
  const { model1Output, model2Output, decision } = req.body ?? {};
  if (!model1Output || !model2Output || !decision) {
    return res.status(400).json({ error: 'model1Output, model2Output, decision required' });
  }
  logDisagreement(model1Output, model2Output, decision);
  res.json({ logged: true, agreed: model1Output === model2Output });
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => console.log(`TrainLLM listening on ${port}`));
