"""
SQLAlchemy Database Models for Carbon Footprint Engine & Ledger
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    JSON,
    CheckConstraint
)
from app.database import Base


class EmissionFactor(Base):
    """Emission factors table mapping raw materials to kg CO2e per kg."""
    __tablename__ = "emission_factors"

    factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    material_name = Column(String(100), unique=True, nullable=False, index=True)
    co2e_kg_per_kg = Column(Float, nullable=False)
    source_database = Column(String(100), nullable=False)
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("co2e_kg_per_kg >= 0", name="check_positive_emission_factor"),
    )


class ProductCarbonBaseline(Base):
    """Stores pre-calculated Cradle-to-Gate product baseline carbon footprint."""
    __tablename__ = "product_carbon_baselines"

    baseline_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(String(100), nullable=False)
    cradle_to_gate_co2e = Column(Float, nullable=False)
    calculation_metadata = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("cradle_to_gate_co2e >= 0", name="check_positive_cradle_to_gate"),
    )


class TransactionalCarbonLedger(Base):
    """Immutable, cryptographically chained transactional carbon ledger."""
    __tablename__ = "transactional_carbon_ledger"

    ledger_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    total_product_co2e = Column(Float, nullable=False)
    total_shipping_co2e = Column(Float, nullable=False)
    total_order_co2e = Column(Float, nullable=False)
    is_offset = Column(Boolean, default=False, nullable=False)
    offset_amount_usd = Column(Float, default=0.0, nullable=False)
    offset_provider_transaction_id = Column(String(150), nullable=True)
    offset_certificate_url = Column(String(255), nullable=True)
    previous_block_hash = Column(String(64), nullable=True)
    block_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("total_product_co2e >= 0", name="check_positive_product_co2e"),
        CheckConstraint("total_shipping_co2e >= 0", name="check_positive_shipping_co2e"),
        CheckConstraint("total_order_co2e >= 0", name="check_positive_order_co2e"),
        CheckConstraint("offset_amount_usd >= 0", name="check_positive_offset_amount"),
    )
