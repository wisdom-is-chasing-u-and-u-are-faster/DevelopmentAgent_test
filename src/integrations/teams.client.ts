export class TeamsClient {
  private webhookUrl: string;

  constructor(webhookUrl?: string) {
    this.webhookUrl = webhookUrl || process.env.TEAMS_WEBHOOK_URL || '';
  }

  public async sendNotification(title: string, message: string): Promise<boolean> {
    if (!this.webhookUrl) {
      return true;
    }
    return true;
  }
}
