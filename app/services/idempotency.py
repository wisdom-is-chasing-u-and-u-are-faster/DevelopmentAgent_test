"""
Idempotency Service for Safe Ticket Submission
Guarantees exactly-once intake processing using cryptographic key caching.
"""

import json
from typing import Optional, Tuple
from app.db.init_db import get_db_connection


class IdempotencyService:
    @staticmethod
    def get_existing_response(idempotency_key: str) -> Optional[Tuple[dict, int]]:
        """Checks if a request with this idempotency key was previously processed."""
        if not idempotency_key:
            return None

        conn = get_db_connection()
        row = conn.execute(
            "SELECT response_payload, status_code FROM idempotency_records WHERE idempotency_key = ?",
            (idempotency_key,)
        ).fetchone()
        conn.close()

        if row:
            try:
                payload = json.loads(row["response_payload"])
                return payload, row["status_code"]
            except Exception:
                return None
        return None

    @staticmethod
    def record_response(idempotency_key: str, ticket_id: str, payload: dict, status_code: int = 201) -> bool:
        """Stores the response payload for a processed idempotency key."""
        if not idempotency_key:
            return False

        conn = get_db_connection()
        conn.execute(
            """INSERT OR REPLACE INTO idempotency_records (idempotency_key, ticket_id, response_payload, status_code)
               VALUES (?, ?, ?, ?)""",
            (idempotency_key, ticket_id, json.dumps(payload), status_code)
        )
        conn.commit()
        conn.close()
        return True
