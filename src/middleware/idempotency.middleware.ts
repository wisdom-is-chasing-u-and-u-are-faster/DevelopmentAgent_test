import { Request, Response, NextFunction } from 'express';

const idempotencyCache = new Map<string, { status: number; body: any; expiresAt: number }>();

export const idempotencyMiddleware = (req: Request, res: Response, next: NextFunction) => {
  if (req.method !== 'POST') {
    return next();
  }

  const idempotencyKey = req.headers['x-idempotency-key'] as string;
  if (!idempotencyKey) {
    return res.status(400).json({
      type: 'https://tools.ietf.org/html/rfc7807',
      title: 'Missing Required Header',
      status: 400,
      detail: 'X-Idempotency-Key header is required for ticket ingestion'
    });
  }

  req.idempotencyKey = idempotencyKey;

  const cached = idempotencyCache.get(idempotencyKey);
  if (cached) {
    if (Date.now() < cached.expiresAt) {
      return res.status(cached.status).json(cached.body);
    } else {
      idempotencyCache.delete(idempotencyKey);
    }
  }

  // Intercept json sending to cache the response
  const originalJson = res.json.bind(res);
  res.json = (body: any) => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      idempotencyCache.set(idempotencyKey, {
        status: res.statusCode,
        body,
        expiresAt: Date.now() + 24 * 60 * 60 * 1000 // 24-hour TTL
      });
    }
    return originalJson(body);
  };

  next();
};
