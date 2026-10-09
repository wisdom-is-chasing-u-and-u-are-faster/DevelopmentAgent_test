import { SlackClient } from '../integrations/slack.client';
import { TeamsClient } from '../integrations/teams.client';
import { EmailClient } from '../integrations/email.client';

export interface NotificationPayload {
  ticketId: string;
  ticketNumber: string;
  title: string;
  priority: string;
  recipientEmail?: string;
  channels: ('SLACK' | 'TEAMS' | 'EMAIL')[];
  event: 'TICKET_CREATED' | 'SLA_WARNING' | 'SLA_BREACH' | 'STATUS_CHANGED';
}

export class NotificationDispatcher {
  private slackClient: SlackClient;
  private teamsClient: TeamsClient;
  private emailClient: EmailClient;

  constructor() {
    this.slackClient = new SlackClient();
    this.teamsClient = new TeamsClient();
    this.emailClient = new EmailClient();
  }

  public async dispatch(payload: NotificationPayload): Promise<{ success: boolean; dispatchedChannels: string[] }> {
    const dispatched: string[] = [];

    const msg = `[${payload.priority}] Ticket ${payload.ticketNumber}: ${payload.title} (${payload.event})`;

    for (const channel of payload.channels) {
      if (channel === 'SLACK') {
        await this.slackClient.sendAlert('#incident-alerts', msg, payload.priority);
        dispatched.push('SLACK');
      } else if (channel === 'TEAMS') {
        await this.teamsClient.sendNotification(`Ticket Event: ${payload.event}`, msg);
        dispatched.push('TEAMS');
      } else if (channel === 'EMAIL' && payload.recipientEmail) {
        await this.emailClient.sendEmail(payload.recipientEmail, `Notification: ${payload.ticketNumber}`, `<p>${msg}</p>`);
        dispatched.push('EMAIL');
      }
    }

    return { success: true, dispatchedChannels: dispatched };
  }
}
