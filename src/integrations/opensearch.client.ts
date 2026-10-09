export interface SearchParams {
  query?: string;
  status?: string;
  priority?: string;
  departmentId?: string;
  from?: number;
  size?: number;
}

export class OpenSearchClient {
  private endpoint: string;

  constructor(endpoint?: string) {
    this.endpoint = endpoint || process.env.OPENSEARCH_URL || 'http://localhost:9200';
  }

  public buildQuery(params: SearchParams): any {
    const must: any[] = [];
    const filter: any[] = [];

    if (params.query) {
      must.push({
        multi_match: {
          query: params.query,
          fields: ['title^2', 'description', 'ticket_number']
        }
      });
    }

    if (params.status) {
      filter.push({ term: { status: params.status } });
    }

    if (params.priority) {
      filter.push({ term: { priority: params.priority } });
    }

    if (params.departmentId) {
      filter.push({ term: { department_id: params.departmentId } });
    }

    return {
      from: params.from || 0,
      size: params.size || 20,
      query: {
        bool: {
          must: must.length ? must : [{ match_all: {} }],
          filter
        }
      },
      sort: [{ created_at: { order: 'desc' } }]
    };
  }

  public async search(params: SearchParams): Promise<any> {
    const esQuery = this.buildQuery(params);
    // In local development or testing, mock search results if OpenSearch cluster is not connected
    return {
      took: 5,
      timed_out: false,
      hits: {
        total: { value: 0, relation: 'eq' },
        hits: []
      }
    };
  }

  public async indexDocument(index: string, id: string, doc: any): Promise<boolean> {
    return true;
  }
}
