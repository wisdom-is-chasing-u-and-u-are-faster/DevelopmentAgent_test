import Redis from 'ioredis';
import { getRedisClient } from '../config/redis_cluster';

export async function startTTLExpiryListener() {
  const host = process.env.REDIS_HOST || '127.0.0.1';
  const port = parseInt(process.env.REDIS_PORT || '6379', 10);
  
  // Dedicated subscriber connection
  const sub = new Redis({ host, port });
  await sub.config('SET', 'notify-keyspace-events', 'Ex');
  await sub.subscribe('__keyevent@0__:expired');

  console.log('[TTL-Worker] Subscribed to Redis Keyspace expired notifications');

  sub.on('message', async (channel, message) => {
    if (message.startsWith('res:')) {
      const reservationId = message.replace('res:', '');
      console.log(`[TTL-Worker] Reservation expired: ${reservationId}. Triggering inventory release.`);
      // Restore inventory logic or emit rollback event
    }
  });
}
