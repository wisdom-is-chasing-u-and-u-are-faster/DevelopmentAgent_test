import { pool } from '../db/client';

export interface AgentCandidate {
  agentId: string;
  departmentId: string;
  activeTicketCount: number;
  maxCapacity: number;
  proficiencyLevel: number;
  score: number;
}

export class AgentMatchingService {
  /**
   * Calculates score for candidate:
   * Higher proficiency gives bonus, higher active workload incurs penalty.
   */
  public static calculateScore(proficiency: number, activeCount: number): number {
    return (proficiency * 10) - (activeCount * 2);
  }

  /**
   * Discovers eligible agents and selects the highest scoring agent for a ticket.
   */
  public static async matchAgent(departmentId: string, requiredSkillCode?: string): Promise<string | null> {
    const query = `
      SELECT 
        u.user_id as "agentId",
        u.department_id as "departmentId",
        COALESCE(w.active_ticket_count, 0) as "activeTicketCount",
        COALESCE(w.max_capacity, 10) as "maxCapacity",
        COALESCE(ask.proficiency_level, 3) as "proficiencyLevel"
      FROM users u
      LEFT JOIN agent_workload w ON u.user_id = w.agent_id
      LEFT JOIN agent_skills ask ON u.user_id = ask.agent_id
      LEFT JOIN skills s ON ask.skill_id = s.skill_id AND ($2::text IS NULL OR s.skill_code = $2)
      WHERE u.role = 'AGENT' 
        AND u.is_active = TRUE
        AND u.department_id = $1
        AND COALESCE(w.status, 'AVAILABLE') = 'AVAILABLE'
        AND COALESCE(w.active_ticket_count, 0) < COALESCE(w.max_capacity, 10)
    `;

    const res = await pool.query(query, [departmentId, requiredSkillCode || null]);
    if (res.rows.length === 0) {
      return null;
    }

    const candidates: AgentCandidate[] = res.rows.map(r => ({
      agentId: r.agentId,
      departmentId: r.departmentId,
      activeTicketCount: Number(r.activeTicketCount),
      maxCapacity: Number(r.maxCapacity),
      proficiencyLevel: Number(r.proficiencyLevel),
      score: this.calculateScore(Number(r.proficiencyLevel), Number(r.activeTicketCount))
    }));

    candidates.sort((a, b) => b.score - a.score);
    return candidates[0].agentId;
  }
}
