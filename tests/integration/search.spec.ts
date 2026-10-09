import { OpenSearchClient } from '../../src/integrations/opensearch.client';

describe('Search Integration Tests', () => {
  it('should construct valid faceted OpenSearch query from parameters', () => {
    const client = new OpenSearchClient();
    const query = client.buildQuery({
      query: 'database latency',
      status: 'IN_PROGRESS',
      priority: 'P1',
      departmentId: '11111111-1111-1111-1111-111111111111',
      from: 0,
      size: 10
    });

    expect(query.from).toBe(0);
    expect(query.size).toBe(10);
    expect(query.query.bool.must[0].multi_match.query).toBe('database latency');
    expect(query.query.bool.filter).toEqual(
      expect.arrayContaining([
        { term: { status: 'IN_PROGRESS' } },
        { term: { priority: 'P1' } },
        { term: { department_id: '11111111-1111-1111-1111-111111111111' } }
      ])
    );
  });
});
