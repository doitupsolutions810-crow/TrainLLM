import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';
import { createGenesis, readLast } from './attestor';

const app = express();
app.use(bodyParser.json());

app.get('/api/attestation', (req: Request, res: Response) => {
  const att = readLast() || createGenesis();
  res.json(att);
});

app.post('/api/governance/scale', (req: Request, res: Response) => {
  // placeholder for governance scaling action
  const att = readLast();
  if (!att) return res.status(500).json({ ok: false, message: 'No attestation' });
  // For demo, accept if invariants all true
  const ok = Object.values(att.invariants ?? {}).every(Boolean);
  if (!ok) return res.status(403).json({ ok: false, message: 'Invariants invalid' });

  // perform scaling (stub)
  res.json({ ok: true, message: 'Scale action accepted' });
});

const port = process.env.PORT ? parseInt(process.env.PORT) : 4000;
app.listen(port, () => console.info(`Backend listening on ${port}`));

export default app;
