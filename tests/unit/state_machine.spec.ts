import { StateMachineService } from '../../src/services/state_machine.service';

describe('StateMachineService Unit Tests', () => {
  it('should allow valid transitions', () => {
    expect(StateMachineService.isValidTransition('SUBMITTED', 'TRIAGED')).toBe(true);
    expect(StateMachineService.isValidTransition('TRIAGED', 'ASSIGNED')).toBe(true);
    expect(StateMachineService.isValidTransition('ASSIGNED', 'IN_PROGRESS')).toBe(true);
    expect(StateMachineService.isValidTransition('IN_PROGRESS', 'RESOLVED')).toBe(true);
    expect(StateMachineService.isValidTransition('RESOLVED', 'CLOSED')).toBe(true);
  });

  it('should reject invalid transitions', () => {
    expect(StateMachineService.isValidTransition('SUBMITTED', 'RESOLVED')).toBe(false);
    expect(StateMachineService.isValidTransition('SUBMITTED', 'CLOSED')).toBe(false);
    expect(StateMachineService.isValidTransition('CLOSED', 'IN_PROGRESS')).toBe(false);
    expect(StateMachineService.isValidTransition('CANCELED', 'ASSIGNED')).toBe(false);
  });

  it('should allow cancellation from early stages', () => {
    expect(StateMachineService.isValidTransition('SUBMITTED', 'CANCELED')).toBe(true);
    expect(StateMachineService.isValidTransition('TRIAGED', 'CANCELED')).toBe(true);
    expect(StateMachineService.isValidTransition('ASSIGNED', 'CANCELED')).toBe(true);
  });
});
