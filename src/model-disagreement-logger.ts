import fs from 'fs';

export function logDisagreement(model1: string, model2: string, decision: string) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    model1,
    model2,
    decision,
    agreed: model1 === model2
  };

  fs.writeFileSync('disagreement-log.jsonl', JSON.stringify(logEntry) + '\n', { flag: 'a' });
}
