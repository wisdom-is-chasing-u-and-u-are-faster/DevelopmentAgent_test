import { SLACalculationEngine } from '../../src/services/sla.service';

describe('SLACalculationEngine Unit Tests', () => {
  it('should compute exact 50%, 75%, and 100% milestone triggers', () => {
    const created = new Date('2026-09-25T10:00:00Z');
    const ackDeadline = new Date('2026-09-25T12:00:00Z'); // 2 hours = 120 min
    const resolveDeadline = new Date('2026-09-26T10:00:00Z'); // 24 hours = 1440 min

    const milestones = SLACalculationEngine.calculateMilestones(created, ackDeadline, resolveDeadline);

    // 50% Ack = 1 hour = 11:00
    expect(milestones.ack50.toISOString()).toBe('2026-09-25T11:00:00.000Z');
    // 75% Ack = 1.5 hours = 11:30
    expect(milestones.ack75.toISOString()).toBe('2026-09-25T11:30:00.000Z');
    // 100% Ack = 2 hours = 12:00
    expect(milestones.ack100.toISOString()).toBe('2026-09-25T12:00:00.000Z');

    // 50% Resolve = 12 hours = 22:00
    expect(milestones.resolve50.toISOString()).toBe('2026-09-25T22:00:00.000Z');
  });

  it('should evaluate status as MET when completed before deadline', () => {
    const deadline = new Date('2026-09-25T12:00:00Z');
    const completed = new Date('2026-09-25T11:45:00Z');
    expect(SLACalculationEngine.evaluateStatus(deadline, completed)).toBe('MET');
  });

  it('should evaluate status as BREACHED when completed after deadline', () => {
    const deadline = new Date('2026-09-25T12:00:00Z');
    const completed = new Date('2026-09-25T12:15:00Z');
    expect(SLACalculationEngine.evaluateStatus(deadline, completed)).toBe('BREACHED');
  });

  it('should evaluate status as BREACHED if deadline has passed without completion', () => {
    const deadline = new Date('2026-09-25T12:00:00Z');
    const now = new Date('2026-09-25T12:01:00Z');
    expect(SLACalculationEngine.evaluateStatus(deadline, undefined, now)).toBe('BREACHED');
  });
});
