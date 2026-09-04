"""
Database Configuration and Initialization
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# For SQLite, enable check_same_thread=False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_emission_factors(db):
    """Seed initial emission factors if empty."""
    from app.models import EmissionFactor

    count = db.query(EmissionFactor).count()
    if count == 0:
        default_factors = [
            {"material_name": "Organic Cotton", "co2e_kg_per_kg": 3.5, "source_database": "Ecoinvent v3.8"},
            {"material_name": "Conventional Cotton", "co2e_kg_per_kg": 8.5, "source_database": "Higg Index"},
            {"material_name": "Recycled Polyester", "co2e_kg_per_kg": 4.2, "source_database": "Ecoinvent v3.8"},
            {"material_name": "Virgin Polyester", "co2e_kg_per_kg": 9.8, "source_database": "Higg Index"},
            {"material_name": "Linen", "co2e_kg_per_kg": 2.8, "source_database": "Ecoinvent v3.8"},
            {"material_name": "Hemp", "co2e_kg_per_kg": 2.1, "source_database": "Ecoinvent v3.8"},
            {"material_name": "Recycled Wool", "co2e_kg_per_kg": 5.0, "source_database": "Higg Index"},
            {"material_name": "Silk", "co2e_kg_per_kg": 15.0, "source_database": "Higg Index"},
            {"material_name": "Bamboo", "co2e_kg_per_kg": 4.0, "source_database": "Ecoinvent v3.8"},
        ]
        for item in default_factors:
            factor = EmissionFactor(
                factor_id=str(uuid.uuid4()),
                material_name=item["material_name"],
                co2e_kg_per_kg=item["co2e_kg_per_kg"],
                source_database=item["source_database"],
                last_updated_at=datetime.now(timezone.utc)
            )
            db.add(factor)
        db.commit()


def init_db():
    """Create all tables and seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_emission_factors(db)
    finally:
        db.close()
