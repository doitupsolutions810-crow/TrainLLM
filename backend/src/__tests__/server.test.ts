import request from 'supertest';
import app from '../server';

describe('backend server', () => {
  test('attestation endpoint', async () => {
    const res = await request(app).get('/api/attestation');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('proofHash');
  });
});
