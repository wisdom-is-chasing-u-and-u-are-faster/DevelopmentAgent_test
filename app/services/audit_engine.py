import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.db.init_db import get_connection


def get_latest_audit_hash() -> str:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT current_hash FROM audit_ledger ORDER BY rowid DESC LIMIT 1")
        row = cur.fetchone()
        if row and row["current_hash"]:
            return row["current_hash"]
        return "0" * 64
    finally:
        conn.close()


def append_audit_event(
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    from_status: Optional[str],
    to_status: Optional[str],
    payload_data: Dict[str, Any]
) -> Dict[str, Any]:
    from app.services.idempotency import generate_payload_checksum

    payload_checksum = generate_payload_checksum(payload_data)
    previous_hash = get_latest_audit_hash()
    timestamp = datetime.now(timezone.utc).isoformat()
    audit_id = f"audit-{uuid.uuid4().hex[:12]}"

    raw_chain = (
        f"{previous_hash}|{audit_id}|{entity_id}|{action}|{actor}|{payload_checksum}|{timestamp}"
    )
    current_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO audit_ledger (
                id, entity_type, entity_id, action, actor, from_status, to_status,
                payload_checksum, previous_hash, current_hash, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id, entity_type, entity_id, action, actor, from_status, to_status,
                payload_checksum, previous_hash, current_hash, timestamp
            )
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "id": audit_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "actor": actor,
        "from_status": from_status,
        "to_status": to_status,
        "payload_checksum": payload_checksum,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "timestamp": timestamp,
    }


def fetch_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_ledger ORDER BY rowid DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def verify_audit_chain_integrity() -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_ledger ORDER BY rowid ASC")
        rows = cur.fetchall()
        if not rows:
            return True

        expected_prev = "0" * 64
        for idx, row in enumerate(rows):
            if idx > 0 and row["previous_hash"] != expected_prev:
                return False
            raw_chain = (
                f"{row['previous_hash']}|{row['id']}|{row['entity_id']}|{row['action']}|"
                f"{row['actor']}|{row['payload_checksum']}|{row['timestamp']}"
            )
            computed_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()
            if row["entity_id"] != "GENESIS" and computed_hash != row["current_hash"]:
                return False
            expected_prev = row["current_hash"]
        return True
    finally:
        conn.close()
