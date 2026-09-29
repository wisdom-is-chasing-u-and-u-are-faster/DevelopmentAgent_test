import { Request, Response } from 'express';
import { createTicketSchema, formatRFC7807Error } from '../validators/ticket.validator';
import { TicketService } from '../../services/ticket.service';

export class TicketController {
  public static async createTicket(req: Request, res: Response) {
    try {
      const parseResult = createTicketSchema.safeParse(req.body);
      if (!parseResult.success) {
        return res.status(400).json(
          formatRFC7807Error(
            400,
            'Validation Error',
            'Invalid payload provided for ticket creation',
            parseResult.error.errors.map(e => ({ field: e.path.join('.'), message: e.message }))
          )
        );
      }

      if (!req.user) {
        return res.status(401).json(formatRFC7807Error(401, 'Unauthorized', 'User identity required'));
      }

      const ticket = await TicketService.createTicket(parseResult.data, req.user);
      return res.status(201).json({
        status: 'SUCCESS',
        data: ticket
      });
    } catch (error: any) {
      console.error('Error in createTicket:', error);
      return res.status(500).json(
        formatRFC7807Error(500, 'Internal Server Error', error.message || 'Failed to create ticket')
      );
    }
  }

  public static async getTicketById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      if (!req.user) {
        return res.status(401).json(formatRFC7807Error(401, 'Unauthorized', 'User identity required'));
      }

      const ticket = await TicketService.getTicketById(id, req.user);
      if (!ticket) {
        return res.status(404).json(formatRFC7807Error(404, 'Not Found', `Ticket with ID ${id} not found`));
      }

      return res.status(200).json({ status: 'SUCCESS', data: ticket });
    } catch (error: any) {
      console.error('Error in getTicketById:', error);
      return res.status(500).json(
        formatRFC7807Error(500, 'Internal Server Error', error.message || 'Failed to fetch ticket')
      );
    }
  }

  public static async listTickets(req: Request, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json(formatRFC7807Error(401, 'Unauthorized', 'User identity required'));
      }

      const limit = parseInt(req.query.limit as string) || 50;
      const offset = parseInt(req.query.offset as string) || 0;

      const tickets = await TicketService.listTickets(req.user, limit, offset);
      return res.status(200).json({ status: 'SUCCESS', data: tickets });
    } catch (error: any) {
      console.error('Error in listTickets:', error);
      return res.status(500).json(
        formatRFC7807Error(500, 'Internal Server Error', error.message || 'Failed to list tickets')
      );
    }
  }
}
