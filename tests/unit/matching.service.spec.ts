import { AgentMatchingService } from '../../src/services/matching.service';

describe('AgentMatchingService Unit Tests', () => {
  it('should calculate matching scores balancing proficiency and current workload', () => {
    // Proficiency 5, 0 active tickets -> 5*10 - 0 = 50
    const scoreA = AgentMatchingService.calculateScore(5, 0);
    expect(scoreA).toBe(50);

    // Proficiency 5, 5 active tickets -> 5*10 - 10 = 40
    const scoreB = AgentMatchingService.calculateScore(5, 5);
    expect(scoreB).toBe(40);

    // Proficiency 3, 1 active ticket -> 3*10 - 2 = 28
    const scoreC = AgentMatchingService.calculateScore(3, 1);
    expect(scoreC).toBe(28);

    // Lower loaded agent with same proficiency gets higher score
    expect(scoreA).toBeGreaterThan(scoreB);
  });
});
