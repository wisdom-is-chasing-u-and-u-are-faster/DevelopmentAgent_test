# Enterprise Ticketing Management System (ETMS)

## Overview
The Enterprise Ticketing Management System (ETMS) delivers a resilient, high-throughput, serverless event-driven architecture designed to manage mission-critical enterprise incidents, outages, and internal service requests at scale. Operating on Google Cloud Run, Cloud Pub/Sub, Cloud Tasks, and Cloud SQL PostgreSQL HA (with SQLite local fallback), ETMS achieves sub-200ms latency, optimistic concurrency state control, automated skill-based dispatching, and immutable SHA-256 cryptographic audit chaining.

---

## Architecture & Technology Stack
- **Backend:** FastAPI, Python 3.11+, Pydantic v2, Uvicorn, SQLite / PostgreSQL
- **Frontend:** Modern Responsive Portal (`public/index.html`, `public/css/style.css`, `public/js/api.js`, `public/js/app.js`)
- **Event & Async Processing:** Google Cloud Pub/Sub, Cloud Tasks SLA Escalation Callbacks
- **Security & Governance:** PostgreSQL Row-Level Security (RLS), SHA-256 Cryptographic Hash Chaining, STRIDE Threat Neutralization

---

## Quickstart & Local Setup

### 1. Environment Configuration
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seeds
```bash
python3 app/db/init_db.py
```

### 4. Run Application Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to `http://localhost:8000` to access the interactive Command Center and Requester Intake portal.

---

## API Reference & Endpoint Catalog

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Container health and database readiness probe |
| `GET` | `/api/v1/categories` | Dynamic category taxonomy and SLA target lookup |
| `POST` | `/api/v1/tickets` | Idempotent ticket intake endpoint (`X-Idempotency-Key`) |
| `GET` | `/api/v1/tickets` | Queue listing with dynamic status and priority filters |
| `GET` | `/api/v1/tickets/{id}` | Detailed ticket profile |
| `PATCH` | `/api/v1/tickets/{id}` | 7-State lifecycle transition with optimistic locking |
| `POST` | `/api/v1/tickets/{id}/route` | Skill-based agent auto-dispatch |
| `GET` | `/api/v1/tickets/{id}/sla` | Real-time SLA elapsed time and milestone metrics |
| `GET` | `/api/v1/tickets/{id}/audit-trail` | Cryptographic SHA-256 tamper-evident audit history |
| `POST` | `/api/v1/notifications/dispatch` | Omnichannel notification dispatcher (Slack/Teams/Email) |
| `GET` | `/api/v1/search` | Faceted full-text incident discovery engine |
| `GET` | `/api/v1/agents` | Agent skills taxonomy and workload queue capacity |

---

## Running Verification Tests
Execute the comprehensive automated test suite with pytest:
```bash
pytest -v
```
