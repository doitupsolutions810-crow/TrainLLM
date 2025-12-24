import fs from 'fs';

export function logAction(action: string, result: string) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    action,
    result
  };

  fs.writeFileSync('action-log.jsonl', JSON.stringify(logEntry) + '\n', { flag: 'a' });
}

export function readActions(): Array<{timestamp:string, action:string, result:string}> {
  try {
    const raw = fs.readFileSync('action-log.jsonl', 'utf8');
    return raw.trim().split('\n').map(l => JSON.parse(l));
  } catch (err) {
    return [];
  }
}
