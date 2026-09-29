import { pool } from '../db/client';
import { AgentMatchingService } from '../services/matching.service';

export class RoutingWorker {
  public static async processUnassignedTickets(): Promise<number> {
    const unassigned = await pool.query(`
      SELECT ticket_id, department_id, category 
      FROM tickets 
      WHERE assigned_agent_id IS NULL AND status = 'SUBMITTED'
      LIMIT 20
    `);

    let assignedCount = 0;

    for (const ticket of unassigned.rows) {
      const matchedAgentId = await AgentMatchingService.matchAgent(ticket.department_id);
      if (matchedAgentId) {
        const client = await pool.connect();
        try {
          await client.query('BEGIN');
          await client.query(
            `UPDATE tickets 
             SET assigned_agent_id = $1, status = 'ASSIGNED', updated_at = CURRENT_TIMESTAMP
             WHERE ticket_id = $2`,
            [matchedAgentId, ticket.ticket_id]
          );

          await client.query(
            `INSERT INTO agent_workload (agent_id, active_ticket_count, max_capacity, status)
             VALUES ($1, 1, 10, 'AVAILABLE')
             ON CONFLICT (agent_id) 
             DO UPDATE SET active_ticket_count = agent_workload.active_ticket_count + 1, updated_at = CURRENT_TIMESTAMP`,
            [matchedAgentId]
          );

          await client.query('COMMIT');
          assignedCount++;
        } catch (err) {
          await client.query('ROLLBACK');
          console.error(`Failed to assign ticket ${ticket.ticket_id}:`, err);
        } finally {
          client.release();
        }
      }
    }

    return assignedCount;
  }
}
