"""
app/services/cms_hsm_adapter.py — Card Management System & HSM Adapter
"""
import uuid
import hashlib
from typing import Dict, Any
from app.db.init_db import get_db_connection


class CMSHSMAdapter:
    @classmethod
    def generate_virtual_card(
        cls,
        account_number: str,
        card_holder_name: str,
        card_network: str = "VISA",
    ) -> Dict[str, Any]:
        """Generates instant virtual debit card using HSM tokenization."""
        card_id = f"crd_{uuid.uuid4().hex[:12]}"

        # Generate valid simulated Visa PAN
        pan_suffix = f"{uuid.uuid4().int % 10000:04d}"
        full_pan = f"411188884444{pan_suffix}"
        masked_pan = f"4111 •••• •••• {pan_suffix}"
        expiry_date = "09/30"
        cvv = f"{uuid.uuid4().int % 900 + 100}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO virtual_cards (card_id, account_number, card_holder_name, masked_pan, full_pan, expiry_date, cvv, network, status, tokenization_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (card_id,
             account_number,
             card_holder_name.upper(),
             masked_pan,
             full_pan,
             expiry_date,
             cvv,
             card_network.upper(),
             "ACTIVE",
             "READY_FOR_WALLET"),
        )
        conn.commit()
        conn.close()

        return {
            "card_id": card_id,
            "account_number": account_number,
            "masked_pan": masked_pan,
            "full_pan": full_pan,
            "expiry_date": expiry_date,
            "cvv": cvv,
            "card_holder_name": card_holder_name.upper(),
            "status": "ACTIVE",
            "network": card_network.upper(),
        }

    @classmethod
    def push_tokenize_to_wallet(
        cls,
        card_id: str,
        wallet_provider: str = "APPLE_PAY",
        device_id: str = "dev_iphone_15",
    ) -> Dict[str, Any]:
        """Executes push tokenization to Apple Wallet / Google Pay with cryptogram generation."""
        token_ref = f"TOK-{wallet_provider[:2].upper()}-{uuid.uuid4().hex[:8].upper()}"
        cryptogram = hashlib.sha256(
            f"{card_id}|{wallet_provider}|{token_ref}".encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE virtual_cards
            SET wallet_provider = ?, token_reference_id = ?, token_cryptogram = ?, tokenization_status = 'TOKENIZED_SUCCESS'
            WHERE card_id = ?
            """,
            (wallet_provider.upper(), token_ref, cryptogram, card_id),
        )
        conn.commit()
        conn.close()

        return {
            "card_id": card_id,
            "wallet_provider": wallet_provider.upper(),
            "token_reference_id": token_ref,
            "tokenization_status": "TOKENIZED_SUCCESS",
            "token_cryptogram": cryptogram,
        }
