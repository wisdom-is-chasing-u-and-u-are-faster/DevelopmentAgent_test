import { SessionContextService } from '../../src/middleware/session_context.middleware';
import { UserContext } from '../../src/middleware/auth.middleware';

describe('Security & RLS Isolation Tests', () => {
  it('should correctly format PostgreSQL session configuration commands', async () => {
    const mockClient = {
      query: jest.fn().mockResolvedValue({ rowCount: 1 })
    } as any;

    const user: UserContext = {
      userId: '11111111-2222-3333-4444-555555555555',
      email: 'requester@enterprise.com',
      role: 'REQUESTER',
      departmentId: 'dept-123'
    };

    await SessionContextService.applySessionContext(mockClient, user);

    expect(mockClient.query).toHaveBeenCalledWith(
      "SELECT set_config('app.current_user_id', $1, true)",
      ['11111111-2222-3333-4444-555555555555']
    );
    expect(mockClient.query).toHaveBeenCalledWith(
      "SELECT set_config('app.current_user_role', $1, true)",
      ['REQUESTER']
    );
    expect(mockClient.query).toHaveBeenCalledWith(
      "SELECT set_config('app.current_department_id', $1, true)",
      ['dept-123']
    );
  });

  it('should reset session variables to prevent connection pool leakage', async () => {
    const mockClient = {
      query: jest.fn().mockResolvedValue({ rowCount: 1 })
    } as any;

    await SessionContextService.resetSessionContext(mockClient);

    expect(mockClient.query).toHaveBeenCalledWith("SELECT set_config('app.current_user_id', '', true)");
    expect(mockClient.query).toHaveBeenCalledWith("SELECT set_config('app.current_user_role', '', true)");
    expect(mockClient.query).toHaveBeenCalledWith("SELECT set_config('app.current_department_id', '', true)");
  });
});
