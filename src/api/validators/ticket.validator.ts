import { z } from 'zod';

export const createTicketSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(255),
  description: z.string().min(5, 'Description must be at least 5 characters'),
  priority: z.enum(['P1', 'P2', 'P3', 'P4']).default('P3'),
  category: z.string().min(2, 'Category is required'),
  department_id: z.string().uuid('department_id must be a valid UUID')
});

export type CreateTicketDTO = z.infer<typeof createTicketSchema>;

export const formatRFC7807Error = (status: number, title: string, detail: string, invalidParams?: any[]) => {
  return {
    type: 'https://tools.ietf.org/html/rfc7807',
    title,
    status,
    detail,
    invalid_params: invalidParams
  };
};
