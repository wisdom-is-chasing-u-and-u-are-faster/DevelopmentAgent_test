import hashlib
import json
from typing import Dict, Any, Optional
from app.db.init_db import get_connection


def check_idempotency(idempotency_key: Optional[str]) -> Optional[Dict[str, Any]]:
    if not idempotency_key:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE idempotency_key = ?", (idempotency_key,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def generate_payload_checksum(payload: Dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
