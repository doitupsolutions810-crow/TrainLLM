import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end();
  try {
    const backend = process.env.NEXTPUBLICBACKEND_URL || 'http://localhost:4000';
    const r = await fetch(`${backend}/api/governance/scale`, { method: 'POST', body: JSON.stringify(req.body), headers: { 'Content-Type': 'application/json' } });
    const j = await r.json();
    res.status(r.status).json(j);
  } catch (err) {
    res.status(500).json({ ok: false, message: 'proxy failed' });
  }
}
