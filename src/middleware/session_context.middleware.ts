import { PoolClient } from 'pg';
import { UserContext } from './auth.middleware';

export class SessionContextService {
  /**
   * Sets PostgreSQL session variables for Row-Level Security within the current client transaction.
   */
  public static async applySessionContext(client: PoolClient, user: UserContext): Promise<void> {
    await client.query("SELECT set_config('app.current_user_id', $1, true)", [user.userId]);
    await client.query("SELECT set_config('app.current_user_role', $1, true)", [user.role]);
    if (user.departmentId) {
      await client.query("SELECT set_config('app.current_department_id', $1, true)", [user.departmentId]);
    } else {
      await client.query("SELECT set_config('app.current_department_id', '', true)");
    }
  }

  /**
   * Resets session context to prevent connection pool contamination.
   */
  public static async resetSessionContext(client: PoolClient): Promise<void> {
    await client.query("SELECT set_config('app.current_user_id', '', true)");
    await client.query("SELECT set_config('app.current_user_role', '', true)");
    await client.query("SELECT set_config('app.current_department_id', '', true)");
  }
}
