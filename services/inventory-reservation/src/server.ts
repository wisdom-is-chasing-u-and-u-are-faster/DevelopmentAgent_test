import fastify from 'fastify';
import { reservationRoutes } from './routes/reservation';
import { startTTLExpiryListener } from './workers/ttl_expiry_listener';

const server = fastify({ logger: true });

server.register(reservationRoutes);

const PORT = parseInt(process.env.PORT || '3000', 10);

export async function start() {
  try {
    await server.listen({ port: PORT, host: '0.0.0.0' });
    console.log(`Inventory Reservation Service listening on ${PORT}`);
    if (process.env.NODE_ENV !== 'test') {
      startTTLExpiryListener().catch(console.error);
    }
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
}

if (require.main === module) {
  start();
}
