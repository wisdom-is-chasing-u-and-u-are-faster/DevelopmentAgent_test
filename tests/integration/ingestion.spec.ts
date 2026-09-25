import request from 'supertest';
import { app } from '../../src/server';

describe('Ingestion & API Integration Tests', () => {
  it('GET /health should return 200 UP', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('UP');
    expect(res.body.service).toBe('enterprise-ticketing-platform');
  });

  it('POST /api/v1/tickets without X-Idempotency-Key should return 400 RFC-7807', async () => {
    const res = await request(app)
      .post('/api/v1/tickets')
      .send({
        title: 'Network latency spike in us-central1',
        description: 'VPC connector egress packet drop observed',
        category: 'NETWORK',
        priority: 'P1',
        department_id: '11111111-1111-1111-1111-111111111111'
      });

    expect(res.status).toBe(400);
    expect(res.body.type).toBe('https://tools.ietf.org/html/rfc7807');
    expect(res.body.title).toBe('Missing Required Header');
    expect(res.body.detail).toContain('X-Idempotency-Key');
  });

  it('POST /api/v1/tickets with invalid schema should return 400 RFC-7807 with invalid_params', async () => {
    const res = await request(app)
      .post('/api/v1/tickets')
      .set('X-Idempotency-Key', 'test-key-invalid-payload')
      .send({
        title: 'Hi', // too short (<3)
        description: 'No', // too short (<5)
        category: '',
        department_id: 'not-a-uuid'
      });

    expect(res.status).toBe(400);
    expect(res.body.type).toBe('https://tools.ietf.org/html/rfc7807');
    expect(res.body.title).toBe('Validation Error');
    expect(res.body.invalid_params).toBeDefined();
    expect(res.body.invalid_params.length).toBeGreaterThan(0);
  });
});
