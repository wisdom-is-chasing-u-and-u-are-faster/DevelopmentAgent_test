"""
app/services/audit_service.py — Cryptographic Immutable Audit Ledger
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.db.init_db import get_db_connection


class AuditService:
    @staticmethod
    def get_latest_hash(conn) -> str:
        cursor = conn.cursor()
        cursor.execute("SELECT entry_hash FROM audit_ledger ORDER BY timestamp DESC, rowid DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row["entry_hash"]:
            return row["entry_hash"]
        return "0" * 64

    @classmethod
    def record_event(
        cls,
        action: str,
        entity_id: str,
        actor: str = "system",
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """Appends an event to the audit ledger with SHA-256 hash chaining."""
        if payload is None:
            payload = {}

        conn = get_db_connection()
        cursor = conn.cursor()

        prev_hash = cls.get_latest_hash(conn)
        entry_id = f"aud_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload, sort_keys=True)

        raw_data = f"{entry_id}|{now_iso}|{action}|{entity_id}|{actor}|{prev_hash}|{payload_str}"
        entry_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        cursor.execute(
            """
            INSERT INTO audit_ledger (entry_id, timestamp, action, entity_id, actor, prev_hash, entry_hash, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (entry_id, now_iso, action, entity_id, actor, prev_hash, entry_hash, payload_str),
        )
        conn.commit()
        conn.close()
        return entry_hash

    @classmethod
    def get_ledger(cls, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
