import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import dotenv from 'dotenv';
import { authMiddleware } from './middleware/auth.middleware';
import { idempotencyMiddleware } from './middleware/idempotency.middleware';
import { TicketController } from './api/controllers/ticket.controller';
import { StatusController } from './api/controllers/status.controller';
import { SearchController } from './api/controllers/search.controller';
import { pool } from './db/client';
import { CryptoService } from './services/crypto.service';

dotenv.config();

export const app = express();
const port = process.env.PORT || 8080;

app.use(helmet({
  contentSecurityPolicy: false // Allow inline scripts for dashboard demos
}));
app.use(cors());
app.use(express.json());

// 1. Static frontend assets mount (Required by full-stack verification)
app.use(express.static(path.join(__dirname, '../public')));

// 2. Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'enterprise-ticketing-platform',
    timestamp: new Date().toISOString()
  });
});

// 3. Departments list
app.get('/api/v1/departments', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM departments WHERE is_active = TRUE ORDER BY department_name');
    res.status(200).json({ status: 'SUCCESS', data: result.rows });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Core Ticket APIs
app.post('/api/v1/tickets', authMiddleware, idempotencyMiddleware, TicketController.createTicket);
app.get('/api/v1/tickets', authMiddleware, TicketController.listTickets);
app.get('/api/v1/tickets/:id', authMiddleware, TicketController.getTicketById);
app.patch('/api/v1/tickets/:id/status', authMiddleware, StatusController.updateStatus);

// 5. Search APIs
app.get('/api/v1/search', authMiddleware, SearchController.search);
app.get('/api/v1/tickets/search', authMiddleware, SearchController.search);

// 6. Audit Ledger & SHA-256 Checksum Inspector API
app.get('/api/v1/audit/:ticketId', authMiddleware, async (req, res) => {
  try {
    const { ticketId } = req.params;
    const result = await pool.query(
      `SELECT audit_id as "auditId", ticket_id as "ticketId", action_type as "actionType",
              diff_payload as "diffPayload", timestamp, prev_checksum as "prevChecksum", checksum
       FROM ticket_audit_ledger 
       WHERE ticket_id = $1 
       ORDER BY audit_id ASC`,
      [ticketId]
    );

    const verification = CryptoService.verifyAuditChain(result.rows);

    res.status(200).json({
      status: 'SUCCESS',
      ticketId,
      isChainValid: verification.isValid,
      brokenAtAuditId: verification.brokenAtAuditId || null,
      records: result.rows
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`Enterprise Ticketing Platform listening on port ${port}`);
  });
}
