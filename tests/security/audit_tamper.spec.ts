import { CryptoService, AuditRecord } from '../../src/services/crypto.service';

describe('STRIDE Security - Audit Ledger Tamper Proofing Tests', () => {
  it('should detect when an attacker replaces a record in the audit ledger', () => {
    const genesis = '0000000000000000000000000000000000000000000000000000000000000000';
    const rec1Hash = CryptoService.calculateChecksum(genesis, 'tck-1', 'CREATED', { title: 'Security Event' }, '2026-09-25T12:00:00Z');
    const rec2Hash = CryptoService.calculateChecksum(rec1Hash, 'tck-1', 'STATUS_CHANGED', { old_status: 'SUBMITTED', new_status: 'RESOLVED' }, '2026-09-25T12:30:00Z');

    const ledger: AuditRecord[] = [
      {
        auditId: 101,
        ticketId: 'tck-1',
        actionType: 'CREATED',
        diffPayload: { title: 'Security Event' },
        timestamp: '2026-09-25T12:00:00Z',
        prevChecksum: genesis,
        checksum: rec1Hash
      },
      {
        auditId: 102,
        ticketId: 'tck-1',
        actionType: 'STATUS_CHANGED',
        diffPayload: { old_status: 'SUBMITTED', new_status: 'RESOLVED' },
        timestamp: '2026-09-25T12:30:00Z',
        prevChecksum: rec1Hash,
        checksum: rec2Hash
      }
    ];

    expect(CryptoService.verifyAuditChain(ledger).isValid).toBe(true);

    // Attacker modifies record 1's checksum or content
    ledger[1].prevChecksum = 'tampered_previous_hash_value';
    const tamperedResult = CryptoService.verifyAuditChain(ledger);
    expect(tamperedResult.isValid).toBe(false);
    expect(tamperedResult.brokenAtAuditId).toBe(102);
  });
});
