import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { getRedisClient, reserveStockLuaSha } from '../config/redis_cluster';

interface ReserveBody {
  reservation_id: string;
  customer_id: string;
  variant_id: string;
  quantity: number;
}

export async function reservationRoutes(fastify: FastifyInstance) {
  fastify.post('/v1/cart/reserve', async (request: FastifyRequest<{ Body: ReserveBody }>, reply: FastifyReply) => {
    const { reservation_id, customer_id, variant_id, quantity } = request.body;
    
    if (!reservation_id || !variant_id || !quantity || quantity <= 0) {
      return reply.status(400).send({ error: 'INVALID_REQUEST', message: 'Missing required reservation fields' });
    }

    const redis = getRedisClient();
    const stockKey = `stock:available:${variant_id}`;
    const resKey = `res:${reservation_id}`;
    const ttlSeconds = 600; // 10-minute hold

    try {
      const sha = await reserveStockLuaSha();
      const result = await redis.evalsha(
        sha,
        2,
        stockKey,
        resKey,
        quantity.toString(),
        ttlSeconds.toString(),
        customer_id || 'guest',
        variant_id
      );

      if (result === 1) {
        return reply.status(201).send({
          status: 'RESERVED',
          reservation_id,
          variant_id,
          quantity,
          expires_in_seconds: ttlSeconds,
          expires_at: new Date(Date.now() + ttlSeconds * 1000).toISOString()
        });
      } else {
        return reply.status(409).send({
          status: 'CONFLICT',
          error: 'OUT_OF_STOCK',
          message: 'Requested quantity exceeds available stock'
        });
      }
    } catch (err: any) {
      fastify.log.error(err);
      return reply.status(500).send({ error: 'INTERNAL_ERROR', message: err.message });
    }
  });
}
