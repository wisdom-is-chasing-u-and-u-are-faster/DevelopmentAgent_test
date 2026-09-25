import request from 'supertest';
import { app } from '../../src/server';

describe('Concurrency & State Transition Integration Tests', () => {
  it('PATCH /api/v1/tickets/:id/status with invalid target status should return 400', async () => {
    const res = await request(app)
      .patch('/api/v1/tickets/11111111-1111-1111-1111-111111111111/status')
      .send({
        status: 'NON_EXISTENT_STATUS',
        expected_version: 1
      });

    expect(res.status).toBe(400);
    expect(res.body.type).toBe('https://tools.ietf.org/html/rfc7807');
    expect(res.body.title).toBe('Validation Error');
  });

  it('PATCH /api/v1/tickets/:id/status with missing expected_version should return 400', async () => {
    const res = await request(app)
      .patch('/api/v1/tickets/11111111-1111-1111-1111-111111111111/status')
      .send({
        status: 'TRIAGED'
      });

    expect(res.status).toBe(400);
  });
});
