import request from 'supertest';
import app from '../server';

describe('server', () => {
  test('health check', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
  });
});
