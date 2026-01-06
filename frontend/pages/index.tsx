import React, { useEffect, useState } from 'react';

export default function Home() {
  const [att, setAtt] = useState<any>(null);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetch('/api/attestation').then(r => r.json()).then(setAtt).catch(() => {});
  }, []);

  async function scale() {
    setMsg('Scaling...');
    const res = await fetch('/api/governance', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ action: 'scale' }) });
    const j = await res.json();
    setMsg(JSON.stringify(j));
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>System Proof Dashboard</h1>
      <pre>{att ? JSON.stringify(att, null, 2) : 'No attestation yet'}</pre>
      <button onClick={scale}>Request Scale</button>
      <div>{msg}</div>
    </main>
  );
}
