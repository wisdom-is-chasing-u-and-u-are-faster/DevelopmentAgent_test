import { pool } from '../db/client';
import { CreateTicketDTO } from '../api/validators/ticket.validator';
import { UserContext } from '../middleware/auth.middleware';
import { SessionContextService } from '../middleware/session_context.middleware';

export interface Ticket {
  ticket_id: string;
  ticket_number: string;
  requester_id: string;
  assigned_agent_id: string | null;
  department_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  sla_ack_deadline: Date;
  sla_resolve_deadline: Date;
  sla_ack_status: string;
  sla_resolve_status: string;
  version: number;
  created_at: Date;
  updated_at: Date;
}

export class TicketService {
  public static calculateSLADeadlines(priority: string, createdAt: Date = new Date()) {
    let ackMinutes = 120;
    let resolveMinutes = 1440; // 24h

    switch (priority) {
      case 'P1':
        ackMinutes = 15;
        resolveMinutes = 240; // 4h
        break;
      case 'P2':
        ackMinutes = 30;
        resolveMinutes = 480; // 8h
        break;
      case 'P3':
        ackMinutes = 120;
        resolveMinutes = 1440; // 24h
        break;
      case 'P4':
        ackMinutes = 240;
        resolveMinutes = 4320; // 72h
        break;
    }

    const ackDeadline = new Date(createdAt.getTime() + ackMinutes * 60 * 1000);
    const resolveDeadline = new Date(createdAt.getTime() + resolveMinutes * 60 * 1000);

    return { ackDeadline, resolveDeadline };
  }

  public static async createTicket(dto: CreateTicketDTO, user: UserContext): Promise<Ticket> {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      await SessionContextService.applySessionContext(client, user);

      const ticketNumber = `TCK-${Date.now().toString().slice(-6)}-${Math.floor(Math.random() * 900 + 100)}`;
      const now = new Date();
      const { ackDeadline, resolveDeadline } = this.calculateSLADeadlines(dto.priority, now);

      const queryText = `
        INSERT INTO tickets (
          ticket_number, requester_id, department_id, title, description,
          priority, category, sla_ack_deadline, sla_resolve_deadline,
          status, sla_ack_status, sla_resolve_status, version, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'SUBMITTED', 'RUNNING', 'RUNNING', 1, $10, $10)
        RETURNING *;
      `;

      const res = await client.query(queryText, [
        ticketNumber,
        user.userId,
        dto.department_id,
        dto.title,
        dto.description,
        dto.priority,
        dto.category,
        ackDeadline,
        resolveDeadline,
        now
      ]);

      await client.query('COMMIT');
      return res.rows[0];
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    } finally {
      await SessionContextService.resetSessionContext(client);
      client.release();
    }
  }

  public static async getTicketById(ticketId: string, user: UserContext): Promise<Ticket | null> {
    const client = await pool.connect();
    try {
      await SessionContextService.applySessionContext(client, user);
      const res = await client.query('SELECT * FROM tickets WHERE ticket_id = $1', [ticketId]);
      return res.rows[0] || null;
    } finally {
      await SessionContextService.resetSessionContext(client);
      client.release();
    }
  }

  public static async listTickets(user: UserContext, limit = 50, offset = 0): Promise<Ticket[]> {
    const client = await pool.connect();
    try {
      await SessionContextService.applySessionContext(client, user);
      const res = await client.query(
        'SELECT * FROM tickets ORDER BY created_at DESC LIMIT $1 OFFSET $2',
        [limit, offset]
      );
      return res.rows;
    } finally {
      await SessionContextService.resetSessionContext(client);
      client.release();
    }
  }
}
