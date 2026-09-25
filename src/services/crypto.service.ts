import crypto from 'crypto';

export interface AuditRecord {
  auditId: number;
  ticketId: string;
  actionType: string;
  diffPayload: any;
  timestamp: string;
  prevChecksum: string;
  checksum: string;
}

export class CryptoService {
  /**
   * Generates a SHA-256 hash for an audit ledger entry.
   */
  public static calculateChecksum(prevChecksum: string, ticketId: string, actionType: string, diffPayload: any, timestamp: string): string {
    const payloadStr = typeof diffPayload === 'string' ? diffPayload : JSON.stringify(diffPayload);
    const raw = `${prevChecksum}${ticketId}${actionType}${payloadStr}${timestamp}`;
    return crypto.createHash('sha256').update(raw).digest('hex');
  }

  /**
   * Verifies an entire chain of audit records for tamper resistance.
   */
  public static verifyAuditChain(records: AuditRecord[]): { isValid: boolean; brokenAtAuditId?: number } {
    let expectedPrev = '0000000000000000000000000000000000000000000000000000000000000000';

    for (const record of records) {
      if (record.prevChecksum !== expectedPrev) {
        return { isValid: false, brokenAtAuditId: record.auditId };
      }
      // Chain moves forward to the current record's checksum
      expectedPrev = record.checksum;
    }

    return { isValid: true };
  }
}
