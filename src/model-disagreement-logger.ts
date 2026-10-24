import fs from 'fs';

export function logDisagreement(model1Output: string, model2Output: string, decision: string) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    model1Output,
    model2Output,
    decision,
    agreed: model1Output === model2Output,
    mismatch: model1Output !== model2Output
  };

  fs.writeFileSync('disagreement-log.jsonl', JSON.stringify(logEntry) + '\n', { flag: 'a' });
}
