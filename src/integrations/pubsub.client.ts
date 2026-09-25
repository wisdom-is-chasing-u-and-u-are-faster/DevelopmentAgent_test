export interface PubSubMessage {
  messageId: string;
  topic: string;
  data: any;
  attributes: Record<string, string>;
  publishTime: string;
}

export class PubSubClient {
  private topic: string;

  constructor(topic?: string) {
    this.topic = topic || process.env.PUBSUB_TOPIC || 'projects/mock/topics/ticket-events';
  }

  public async publish(eventType: string, data: any, partitionKey: string): Promise<string> {
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
    if (process.env.NODE_ENV === 'development') {
      console.log(`[PubSub] Published ${eventType} with key ${partitionKey} to ${this.topic}`);
    }
    return messageId;
  }
}
