"""
Transactional Carbon Ledger Service
Provides cryptographically chained, immutable audit trail for all order-level carbon emissions and offsets.
"""
import uuid
import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import TransactionalCarbonLedger
from app.schemas import CreateLedgerEntryRequest, LedgerEntryResponse


class LedgerService:
    @staticmethod
    def calculate_block_hash(
        order_id: str,
        customer_id: str,
        total_order_co2e: float,
        is_offset: bool,
        offset_provider_tx: str,
        previous_hash: str
    ) -> str:
        prev_str = previous_hash or "GENESIS"
        payload = f"{order_id}|{customer_id}|{total_order_co2e:.4f}|{is_offset}|{offset_provider_tx or ''}|{prev_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def get_latest_block_hash(cls, db: Session) -> str:
        latest = db.query(TransactionalCarbonLedger).order_by(
            TransactionalCarbonLedger.created_at.desc()
        ).first()
        return latest.block_hash if latest else "GENESIS_BLOCK_00000000000000000000000000000000"

    @classmethod
    def record_transaction(
        cls,
        req: CreateLedgerEntryRequest,
        db: Session
    ) -> LedgerEntryResponse:
        total_order_co2e = round(req.total_product_co2e + req.total_shipping_co2e, 4)
        prev_hash = cls.get_latest_block_hash(db)

        block_hash = cls.calculate_block_hash(
            order_id=req.order_id,
            customer_id=req.customer_id,
            total_order_co2e=total_order_co2e,
            is_offset=req.is_offset,
            offset_provider_tx=req.offset_provider_transaction_id or "",
            previous_hash=prev_hash
        )

        entry = TransactionalCarbonLedger(
            ledger_id=str(uuid.uuid4()),
            order_id=req.order_id,
            customer_id=req.customer_id,
            total_product_co2e=req.total_product_co2e,
            total_shipping_co2e=req.total_shipping_co2e,
            total_order_co2e=total_order_co2e,
            is_offset=req.is_offset,
            offset_amount_usd=req.offset_amount_usd,
            offset_provider_transaction_id=req.offset_provider_transaction_id,
            offset_certificate_url=req.offset_certificate_url,
            previous_block_hash=prev_hash,
            block_hash=block_hash,
            created_at=datetime.now(timezone.utc)
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return LedgerEntryResponse(
            ledger_id=entry.ledger_id,
            order_id=entry.order_id,
            customer_id=entry.customer_id,
            total_product_co2e=entry.total_product_co2e,
            total_shipping_co2e=entry.total_shipping_co2e,
            total_order_co2e=entry.total_order_co2e,
            is_offset=entry.is_offset,
            offset_amount_usd=entry.offset_amount_usd,
            offset_provider_transaction_id=entry.offset_provider_transaction_id,
            offset_certificate_url=entry.offset_certificate_url,
            block_hash=entry.block_hash,
            previous_block_hash=entry.previous_block_hash,
            created_at=entry.created_at.isoformat()
        )

    @classmethod
    def get_entry_by_order_id_safe(cls, order_id: str, db: Session):
        """
        Retrieves ledger entry using parameterized query preventing SQL injection.
        """
        # Parameterized query to defend against SQL injection
        query = text("SELECT * FROM transactional_carbon_ledger WHERE order_id = :order_id")
        result = db.execute(query, {"order_id": order_id}).mappings().first()
        return result
