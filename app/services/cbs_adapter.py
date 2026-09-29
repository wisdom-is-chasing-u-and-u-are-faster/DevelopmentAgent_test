"""
app/services/cbs_adapter.py — Core Banking System (CBS) Adapter
"""
import uuid
from typing import Dict, Any
from app.db.init_db import get_db_connection


class CBSAdapter:
    @classmethod
    def provision_account(
        cls,
        application_id: str,
        account_product_code: str = "SAVINGS_STANDARD",
        initial_deposit: float = 100.00,
        currency: str = "USD",
    ) -> Dict[str, Any]:
        """Provisions CIF and creates savings account in Core Banking System."""
        cif_number = f"CIF-{uuid.uuid4().int % 10000000:07d}"
        account_number = f"ACCT-48{uuid.uuid4().int % 100000000:08d}"
        account_id = f"acc_{uuid.uuid4().hex[:10]}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO accounts (account_id, application_id, cif_number, account_number, account_type, currency, balance, status, cbs_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (account_id, application_id, cif_number, account_number,
             "SAVINGS", currency, initial_deposit, "ACTIVE", "ACTIVE"),
        )
        conn.commit()
        conn.close()

        return {
            "application_id": application_id,
            "cif_number": cif_number,
            "account_number": account_number,
            "account_type": "SAVINGS",
            "currency": currency,
            "balance": initial_deposit,
            "cbs_status": "ACTIVE",
        }
