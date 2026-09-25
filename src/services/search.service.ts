import { OpenSearchClient, SearchParams } from '../integrations/opensearch.client';
import { pool } from '../db/client';

export class SearchService {
  private static opensearch = new OpenSearchClient();

  public static async searchTickets(params: SearchParams): Promise<any> {
    try {
      // Primary: OpenSearch query
      const osResults = await this.opensearch.search(params);
      if (osResults.hits.hits.length > 0) {
        return osResults.hits.hits.map((h: any) => h._source);
      }
    } catch (e) {
      // Fallback to PostgreSQL relational full-text search
    }

    // Fallback: PostgreSQL ILIKE / Full-Text Search
    let queryText = 'SELECT * FROM tickets WHERE 1=1';
    const values: any[] = [];
    let idx = 1;

    if (params.query) {
      queryText += ` AND (title ILIKE $${idx} OR description ILIKE $${idx} OR ticket_number ILIKE $${idx})`;
      values.push(`%${params.query}%`);
      idx++;
    }

    if (params.status) {
      queryText += ` AND status = $${idx}`;
      values.push(params.status);
      idx++;
    }

    if (params.priority) {
      queryText += ` AND priority = $${idx}`;
      values.push(params.priority);
      idx++;
    }

    queryText += ` ORDER BY created_at DESC LIMIT $${idx} OFFSET $${idx + 1}`;
    values.push(params.size || 20, params.from || 0);

    const res = await pool.query(queryText, values);
    return res.rows;
  }
}
