export interface SLAMilestones {
  ack50: Date;
  ack75: Date;
  ack100: Date;
  resolve50: Date;
  resolve75: Date;
  resolve100: Date;
}

export class SLACalculationEngine {
  /**
   * Calculates the exact timestamps for 50%, 75%, and 100% escalation milestones.
   */
  public static calculateMilestones(createdAt: Date, ackDeadline: Date, resolveDeadline: Date): SLAMilestones {
    const createdMs = createdAt.getTime();
    const ackTotalMs = ackDeadline.getTime() - createdMs;
    const resolveTotalMs = resolveDeadline.getTime() - createdMs;

    return {
      ack50: new Date(createdMs + ackTotalMs * 0.5),
      ack75: new Date(createdMs + ackTotalMs * 0.75),
      ack100: ackDeadline,
      resolve50: new Date(createdMs + resolveTotalMs * 0.5),
      resolve75: new Date(createdMs + resolveTotalMs * 0.75),
      resolve100: resolveDeadline
    };
  }

  /**
   * Evaluates current time against deadlines to determine SLA status.
   */
  public static evaluateStatus(deadline: Date, completedAt?: Date, now: Date = new Date()): 'RUNNING' | 'WARNING_50' | 'WARNING_75' | 'BREACHED' | 'MET' {
    if (completedAt) {
      return completedAt.getTime() <= deadline.getTime() ? 'MET' : 'BREACHED';
    }

    if (now.getTime() > deadline.getTime()) {
      return 'BREACHED';
    }

    return 'RUNNING';
  }
}
