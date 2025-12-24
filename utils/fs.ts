import fs from 'fs';
import path from 'path';

export function ensureDirSync(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

export function writeJsonFileSync(filePath: string, data: any, opts?: { spaces?: number }) {
  ensureDirSync(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, opts?.spaces ?? 2));
}

export function safeReadJsonSync(filePath: string) {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    return null;
  }
}
