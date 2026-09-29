import { OpenSearchClient } from '../integrations/opensearch.client';

export class SearchSyncWorker {
  private static opensearch = new OpenSearchClient();

  public static async processEvent(event: { eventType: string; ticket: any }): Promise<boolean> {
    const { ticket } = event;
    if (!ticket || !ticket.ticket_id) {
      return false;
    }

    const doc = {
      ticket_id: ticket.ticket_id,
      ticket_number: ticket.ticket_number,
      title: ticket.title,
      description: ticket.description,
      status: ticket.status,
      priority: ticket.priority,
      category: ticket.category,
      department_id: ticket.department_id,
      created_at: ticket.created_at,
      updated_at: ticket.updated_at
    };

    return await this.opensearch.indexDocument('tickets', ticket.ticket_id, doc);
  }
}
