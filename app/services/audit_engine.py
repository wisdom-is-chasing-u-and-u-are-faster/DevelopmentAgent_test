"""
Cryptographic Audit Ledger Engine
Maintains tamper-evident SHA-256 hash chaining across all ticket mutations.
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.db.init_db import get_db_connection
from app.models.audit import AuditEntry, AuditTrailResponse


class AuditEngine:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    @classmethod
    def compute_sha256(cls, previous_hash: str, payload_str: str, timestamp_str: str) -> str:
        """Calculates deterministic SHA-256 hash chaining string."""
        raw_string = f"{previous_hash}|{payload_str}|{timestamp_str}"
        return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    @classmethod
    def record_mutation(
        cls,
        ticket_id: str,
        actor_id: str,
        actor_role: str,
        action: str,
        prev_state: Dict[str, Any],
        new_state: Dict[str, Any]
    ) -> AuditEntry:
        """Appends an immutable cryptographic record to the audit trail."""
        conn = get_db_connection()

        # Fetch last hash for ticket
        last_entry = conn.execute(
            "SELECT checksum_sha256 FROM audit_ledger WHERE ticket_id = ? ORDER BY timestamp DESC LIMIT 1",
            (ticket_id,)
        ).fetchone()

        prev_hash = last_entry["checksum_sha256"] if last_entry else cls.GENESIS_HASH
        timestamp = datetime.utcnow().isoformat()
        audit_id = f"aud-{uuid.uuid4().hex[:12]}"

        prev_json = json.dumps(prev_state, sort_keys=True)
        new_json = json.dumps(new_state, sort_keys=True)

        current_hash = cls.compute_sha256(prev_hash, new_json, timestamp)

        conn.execute(
            """INSERT INTO audit_ledger (
                id, ticket_id, actor_id, actor_role, action,
                previous_state, new_state, checksum_sha256, previous_checksum_sha256, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                audit_id, ticket_id, actor_id, actor_role, action,
                prev_json, new_json, current_hash, prev_hash, timestamp
            )
        )
        conn.commit()
        conn.close()

        return AuditEntry(
            id=audit_id,
            ticket_id=ticket_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            previous_state=prev_state,
            new_state=new_state,
            checksum_sha256=current_hash,
            previous_checksum_sha256=prev_hash,
            timestamp=timestamp,
            is_valid=True
        )

    @classmethod
    def verify_audit_trail(cls, ticket_id: str) -> AuditTrailResponse:
        """Verifies full cryptographic chain integrity for a ticket's audit history."""
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM audit_ledger WHERE ticket_id = ? ORDER BY timestamp ASC",
            (ticket_id,)
        ).fetchall()
        conn.close()

        entries: List[AuditEntry] = []
        expected_prev_hash = cls.GENESIS_HASH
        chain_valid = True

        for r in rows:
            prev_dict = json.loads(r["previous_state"]) if r["previous_state"] else {}
            new_dict = json.loads(r["new_state"]) if r["new_state"] else {}

            # Recalculate hash
            recalc_hash = cls.compute_sha256(
                r["previous_checksum_sha256"],
                json.dumps(new_dict, sort_keys=True),
                r["timestamp"]
            )

            is_entry_valid = (
                r["checksum_sha256"] == recalc_hash
                and (r["previous_checksum_sha256"] == expected_prev_hash or expected_prev_hash == cls.GENESIS_HASH)
            )

            if not is_entry_valid:
                chain_valid = False

            expected_prev_hash = r["checksum_sha256"]

            entries.append(AuditEntry(
                id=r["id"],
                ticket_id=r["ticket_id"],
                actor_id=r["actor_id"],
                actor_role=r["actor_role"],
                action=r["action"],
                previous_state=prev_dict,
                new_state=new_dict,
                checksum_sha256=r["checksum_sha256"],
                previous_checksum_sha256=r["previous_checksum_sha256"],
                timestamp=r["timestamp"],
                is_valid=is_entry_valid
            ))

        return AuditTrailResponse(
            ticket_id=ticket_id,
            entries=entries,
            chain_valid=chain_valid
        )
