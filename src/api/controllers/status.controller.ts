import { Request, Response } from 'express';
import { z } from 'zod';
import { StateMachineService, TicketStatus } from '../../services/state_machine.service';
import { formatRFC7807Error } from '../validators/ticket.validator';

const statusPatchSchema = z.object({
  status: z.enum([
    'SUBMITTED', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 
    'PENDING_CUSTOMER', 'RESOLVED', 'CLOSED', 'CANCELED'
  ]),
  expected_version: z.number().int().positive(),
  comment: z.string().optional()
});

export class StatusController {
  public static async updateStatus(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const parseResult = statusPatchSchema.safeParse(req.body);

      if (!parseResult.success) {
        return res.status(400).json(
          formatRFC7807Error(
            400,
            'Validation Error',
            'Invalid status transition request payload',
            parseResult.error.errors.map(e => ({ field: e.path.join('.'), message: e.message }))
          )
        );
      }

      if (!req.user) {
        return res.status(401).json(formatRFC7807Error(401, 'Unauthorized', 'User identity required'));
      }

      const { status, expected_version, comment } = parseResult.data;
      const updatedTicket = await StateMachineService.transitionStatus(
        id,
        status as TicketStatus,
        expected_version,
        req.user,
        comment
      );

      return res.status(200).json({
        status: 'SUCCESS',
        data: updatedTicket
      });
    } catch (error: any) {
      if (error.code === 'CONCURRENCY_CONFLICT') {
        return res.status(409).json({
          type: 'https://tools.ietf.org/html/rfc7807',
          title: 'Concurrency Conflict',
          status: 409,
          detail: error.detail,
          conflict: error.conflict
        });
      }
      if (error.code === 'INVALID_TRANSITION') {
        return res.status(400).json(formatRFC7807Error(400, 'Invalid Transition', error.detail));
      }
      if (error.code === 'NOT_FOUND') {
        return res.status(404).json(formatRFC7807Error(404, 'Not Found', error.message));
      }
      return res.status(500).json(formatRFC7807Error(500, 'Internal Server Error', error.message || 'Status update failed'));
    }
  }
}
