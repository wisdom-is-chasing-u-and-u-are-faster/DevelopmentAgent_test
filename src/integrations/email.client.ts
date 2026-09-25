export class EmailClient {
  public async sendEmail(to: string, subject: string, htmlBody: string): Promise<boolean> {
    // In production, invokes SendGrid or Amazon SES
    return true;
  }
}
