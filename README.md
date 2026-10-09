# Enterprise Ticketing Management System (ETMS)

A modern, resilient, serverless event-driven architecture designed to manage mission-critical enterprise incidents, outages, and internal service requests at scale.

---

## 🏛️ System Architecture

* **Backend**: FastAPI (Python 3.11+) with asynchronous routing and RFC-7807 problem details.
* **Database**: PostgreSQL 15+ / SQLite with relational schema (`db/schema.sql`) and initial seed data (`db/seed.sql`).
* **Frontend**: Responsive modern UI views mounted at root `/` and `/pages/` with client API layer (`public/js/api.js`).
* **Lifecycle State Machine**: Strict 7-state lifecycle transition DAG (`NEW` ➔ `TRIAGED` ➔ `ASSIGNED` ➔ `IN_PROGRESS` ➔ `PENDING_CUSTOMER` ➔ `RESOLVED` ➔ `CLOSED`) with optimistic concurrency locking (`expected_version`).
* **Audit Ledger**: Cryptographic SHA-256 chained immutable audit trail ensuring SOC 2 Type II, ISO 27001, and HIPAA compliance.
* **SLA Monitoring**: Multi-stage calculation engine evaluating elapsed time against priority targets (P1: 2h, P2: 4h, P3: 8h, P4: 24h) with 50%, 75%, and 100% threshold notifications across Slack, MS Teams, and Email.

---

## 🚀 Quick Start & Local Execution

### 1. Environment Configuration
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python3 app/db/init_db.py
```

### 4. Run Application Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing & Verification

Run the full automated test suite:
```bash
pytest -v
```

Run linter:
```bash
flake8 app tests --max-line-length=120
```
