import { Request, Response, NextFunction } from 'express';

export interface UserContext {
  userId: string;
  email: string;
  role: 'REQUESTER' | 'AGENT' | 'ADMIN';
  departmentId?: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: UserContext;
      idempotencyKey?: string;
    }
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const userHeader = req.headers['x-user-id'] as string;
  const roleHeader = req.headers['x-user-role'] as string;
  const deptHeader = req.headers['x-department-id'] as string;

  if (userHeader) {
    req.user = {
      userId: userHeader,
      email: (req.headers['x-user-email'] as string) || 'user@enterprise.com',
      role: (roleHeader as any) || 'REQUESTER',
      departmentId: deptHeader || undefined
    };
    return next();
  }

  // Fallback default mock user for local development / testing
  req.user = {
    userId: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    email: 'requester@enterprise.com',
    role: 'REQUESTER',
    departmentId: '44444444-4444-4444-4444-444444444444'
  };
  next();
};
