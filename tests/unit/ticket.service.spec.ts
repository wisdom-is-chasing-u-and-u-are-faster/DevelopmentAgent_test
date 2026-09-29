import { TicketService } from '../../src/services/ticket.service';

describe('TicketService Unit Tests', () => {
  it('should calculate correct SLA deadlines for P1 critical incident', () => {
    const baseDate = new Date('2026-09-25T10:00:00Z');
    const { ackDeadline, resolveDeadline } = TicketService.calculateSLADeadlines('P1', baseDate);

    // P1: 15 min Ack, 4 hours (240 min) Resolve
    expect(ackDeadline.toISOString()).toBe('2026-09-25T10:15:00.000Z');
    expect(resolveDeadline.toISOString()).toBe('2026-09-25T14:00:00.000Z');
  });

  it('should calculate correct SLA deadlines for P2 high incident', () => {
    const baseDate = new Date('2026-09-25T10:00:00Z');
    const { ackDeadline, resolveDeadline } = TicketService.calculateSLADeadlines('P2', baseDate);

    // P2: 30 min Ack, 8 hours (480 min) Resolve
    expect(ackDeadline.toISOString()).toBe('2026-09-25T10:30:00.000Z');
    expect(resolveDeadline.toISOString()).toBe('2026-09-25T18:00:00.000Z');
  });

  it('should calculate correct SLA deadlines for P3 medium ticket', () => {
    const baseDate = new Date('2026-09-25T10:00:00Z');
    const { ackDeadline, resolveDeadline } = TicketService.calculateSLADeadlines('P3', baseDate);

    // P3: 2 hours Ack, 24 hours Resolve
    expect(ackDeadline.toISOString()).toBe('2026-09-25T12:00:00.000Z');
    expect(resolveDeadline.toISOString()).toBe('2026-09-26T10:00:00.000Z');
  });

  it('should calculate correct SLA deadlines for P4 low ticket', () => {
    const baseDate = new Date('2026-09-25T10:00:00Z');
    const { ackDeadline, resolveDeadline } = TicketService.calculateSLADeadlines('P4', baseDate);

    // P4: 4 hours Ack, 72 hours Resolve
    expect(ackDeadline.toISOString()).toBe('2026-09-25T14:00:00.000Z');
    expect(resolveDeadline.toISOString()).toBe('2026-09-28T10:00:00.000Z');
  });
});
