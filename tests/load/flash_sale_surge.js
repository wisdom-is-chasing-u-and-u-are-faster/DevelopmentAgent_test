import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 5000 },
    { duration: '2m', target: 25000 },
    { duration: '3m', target: 50000 }, // 50k Concurrent Virtual Users Flash Surge
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'http_req_duration{type:cart_reserve}': ['p(99)<180'],
    'http_req_duration{type:checkout}': ['p(99)<250'],
    http_req_failed: ['rate<0.001'], // Zero unhandled failures (<0.1% for normal out-of-stock)
  },
};

export default function () {
  const BASE_URL = 'http://localhost:3000';

  group('Flash Drop Cart Reservation Workflow', () => {
    const reservationId = `res_${__VU}_${__ITER}`;
    const payload = JSON.stringify({
      reservation_id: reservationId,
      customer_id: `cust_${__VU}`,
      variant_id: 'var_01',
      quantity: 1,
    });

    const headers = { 'Content-Type': 'application/json' };
    const res = http.post(`${BASE_URL}/v1/cart/reserve`, payload, {
      headers,
      tags: { type: 'cart_reserve' },
    });

    check(res, {
      'status is 201 or 409': (r) => r.status === 201 || r.status === 409,
    });
  });

  sleep(0.5);
}
