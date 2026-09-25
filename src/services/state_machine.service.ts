import { pool } from '../db/client';
import { UserContext } from '../middleware/auth.middleware';
import { SessionContextService } from '../middleware/session_context.middleware';

export type TicketStatus = 
  | 'SUBMITTED' 
  | 'TRIAGED' 
  | 'ASSIGNED' 
  | 'IN_PROGRESS' 
  | 'PENDING_CUSTOMER' 
  | 'RESOLVED' 
  | 'CLOSED' 
  | 'CANCELED';

export class StateMachineService {
  private static validTransitions: Record<TicketStatus, TicketStatus[]> = {
    SUBMITTED: ['TRIAGED', 'CANCELED'],
    TRIAGED: ['ASSIGNED', 'CANCELED'],
    ASSIGNED: ['IN_PROGRESS', 'TRIAGED', 'CANCELED'],
    IN_PROGRESS: ['PENDING_CUSTOMER', 'RESOLVED', 'CANCELED'],
    PENDING_CUSTOMER: ['IN_PROGRESS', 'RESOLVED', 'CANCELED'],
    RESOLVED: ['CLOSED', 'IN_PROGRESS'],
    CLOSED: [],
    CANCELED: []
  };

  public static isValidTransition(fromStatus: TicketStatus, toStatus: TicketStatus): boolean {
    const allowed = this.validTransitions[fromStatus] || [];
    return allowed.includes(toStatus);
  }

  public static async transitionStatus(
    ticketId: string,
    targetStatus: TicketStatus,
    expectedVersion: number,
    user: UserContext,
    comment?: string
  ) {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      await SessionContextService.applySessionContext(client, user);

      // Select row for update
      const checkRes = await client.query(
        'SELECT * FROM tickets WHERE ticket_id = $1 FOR UPDATE',
        [ticketId]
      );

      if (checkRes.rowCount === 0) {
        throw { code: 'NOT_FOUND', message: `Ticket ${ticketId} not found` };
      }

      const currentTicket = checkRes.rows[0];

      // Optimistic Locking Check
      if (currentTicket.version !== expectedVersion) {
        throw {
          code: 'CONCURRENCY_CONFLICT',
          status: 409,
          detail: 'Optimistic locking conflict: ticket was modified by another agent or transaction',
          conflict: {
            current_version: currentTicket.version,
            expected_version: expectedVersion,
            current_status: currentTicket.status,
            updated_at: currentTicket.updated_at
          }
        };
      }

      // State machine validation
      if (!this.isValidTransition(currentTicket.status, targetStatus)) {
        throw {
          code: 'INVALID_TRANSITION',
          status: 400,
          detail: `Cannot transition status from ${currentTicket.status} to ${targetStatus}`
        };
      }

      // Update ticket
      const updateRes = await client.query(
        `UPDATE tickets 
         SET status = $1, version = version + 1, updated_at = CURRENT_TIMESTAMP
         WHERE ticket_id = $2
         RETURNING *;`,
        [targetStatus, ticketId]
      );

      // Add comment if provided
      if (comment) {
        await client.query(
          `INSERT INTO ticket_comments (ticket_id, author_id, body, is_internal)
           VALUES ($1, $2, $3, $4)`,
          [ticketId, user.userId, comment, false]
        );
      }

      await client.query('COMMIT');
      return updateRes.rows[0];
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    } finally {
      await SessionContextService.resetSessionContext(client);
      client.release();
    }
  }
}
