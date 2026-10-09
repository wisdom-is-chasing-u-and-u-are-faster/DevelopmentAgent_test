import { CryptoService, AuditRecord } from '../../src/services/crypto.service';

describe('CryptoService SHA-256 Audit Verification Tests', () => {
  it('should verify a valid cryptographic audit chain', () => {
    const genesisHash = '0000000000000000000000000000000000000000000000000000000000000000';
    const record1Hash = CryptoService.calculateChecksum(genesisHash, 'tck-1', 'CREATED', { title: 'Test' }, '2026-09-25T10:00:00Z');
    const record2Hash = CryptoService.calculateChecksum(record1Hash, 'tck-1', 'UPDATED', { status: 'TRIAGED' }, '2026-09-25T10:05:00Z');

    const chain: AuditRecord[] = [
      {
        auditId: 1,
        ticketId: 'tck-1',
        actionType: 'CREATED',
        diffPayload: { title: 'Test' },
        timestamp: '2026-09-25T10:00:00Z',
        prevChecksum: genesisHash,
        checksum: record1Hash
      },
      {
        auditId: 2,
        ticketId: 'tck-1',
        actionType: 'UPDATED',
        diffPayload: { status: 'TRIAGED' },
        timestamp: '2026-09-25T10:05:00Z',
        prevChecksum: record1Hash,
        checksum: record2Hash
      }
    ];

    const result = CryptoService.verifyAuditChain(chain);
    expect(result.isValid).toBe(true);
  });

  it('should detect tampering when a hash in the chain is modified', () => {
    const genesisHash = '0000000000000000000000000000000000000000000000000000000000000000';
    const record1Hash = 'valid_hash_1';

    const tamperedChain: AuditRecord[] = [
      {
        auditId: 1,
        ticketId: 'tck-1',
        actionType: 'CREATED',
        diffPayload: { title: 'Test' },
        timestamp: '2026-09-25T10:00:00Z',
        prevChecksum: genesisHash,
        checksum: record1Hash
      },
      {
        auditId: 2,
        ticketId: 'tck-1',
        actionType: 'UPDATED',
        diffPayload: { status: 'TRIAGED' },
        timestamp: '2026-09-25T10:05:00Z',
        prevChecksum: 'corrupted_or_altered_hash', // Tampered!
        checksum: 'record2Hash'
      }
    ];

    const result = CryptoService.verifyAuditChain(tamperedChain);
    expect(result.isValid).toBe(false);
    expect(result.brokenAtAuditId).toBe(2);
  });
});
