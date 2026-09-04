"""
Product Carbon Baseline Calculation Engine
Implements Cradle-to-Gate Life Cycle Assessment (LCA) according to ISO 14067 / GHG Protocol.
"""
import logging
from typing import Dict, Tuple
from sqlalchemy.orm import Session

from app.models import EmissionFactor, ProductCarbonBaseline
from app.schemas import CalculateBaselineRequest, BaselineCalculationMetadata
from app.services.cache_service import cache

logger = logging.getLogger("carbon_engine")


class CarbonBaselineEngine:
    DEFAULT_FALLBACK_MATERIAL = "Organic Cotton"
    DEFAULT_FALLBACK_FACTOR = 3.5

    @classmethod
    def get_cache_key(cls, product_id: str) -> str:
        return f"carbon:product:{product_id}"

    @classmethod
    def calculate_baseline(
        cls,
        req: CalculateBaselineRequest,
        db: Session,
        use_cache: bool = True
    ) -> Tuple[float, BaselineCalculationMetadata]:
        cache_key = cls.get_cache_key(req.product_id)

        # 1. Check Cache
        if use_cache:
            cached_val = cache.get(cache_key)
            if cached_val is not None:
                meta = BaselineCalculationMetadata(
                    formula=cached_val["metadata"]["formula"],
                    material_breakdown=cached_val["metadata"]["material_breakdown"],
                    fallback_applied=cached_val["metadata"].get("fallback_applied", False),
                    warning=cached_val["metadata"].get("warning"),
                    cached=True
                )
                return cached_val["cradle_to_gate_co2e_kg"], meta

        # 2. Query Emission Factors
        factors_query = db.query(EmissionFactor).all()
        factor_map: Dict[str, float] = {f.material_name.lower(): f.co2e_kg_per_kg for f in factors_query}

        total_co2e = 0.0
        material_breakdown = []
        fallback_applied = False
        fallback_warning = None

        for mat in req.materials:
            name_clean = mat.material_name.strip()
            name_lower = name_clean.lower()
            fraction = mat.percentage / 100.0
            mat_weight_kg = req.weight_kg * fraction

            if name_lower in factor_map:
                ef = factor_map[name_lower]
                source = "emission_factors"
            else:
                # Fallback mechanism for rare/missing materials
                fallback_applied = True
                ef = factor_map.get(
                    cls.DEFAULT_FALLBACK_MATERIAL.lower(),
                    cls.DEFAULT_FALLBACK_FACTOR
                )
                source = f"fallback ({cls.DEFAULT_FALLBACK_MATERIAL})"
                fallback_warning = f"Calculated with fallback: material '{name_clean}' mapped to default"
                logger.warning(
                    "Missing emission factor for '%s'. Fallback to '%s' (factor: %s).",
                    name_clean,
                    cls.DEFAULT_FALLBACK_MATERIAL,
                    ef
                )

            mat_co2e = mat_weight_kg * ef
            total_co2e += mat_co2e
            material_breakdown.append({
                "material_name": name_clean,
                "percentage": mat.percentage,
                "weight_kg": round(mat_weight_kg, 4),
                "emission_factor_kg_co2e_per_kg": ef,
                "source": source,
                "subtotal_co2e_kg": round(mat_co2e, 4)
            })

        total_co2e_rounded = round(total_co2e, 4)

        meta = BaselineCalculationMetadata(
            formula="SUM(weight_kg * (percentage / 100) * emission_factor_co2e_per_kg)",
            material_breakdown=material_breakdown,
            fallback_applied=fallback_applied,
            warning=fallback_warning,
            cached=False
        )

        # 3. Persist / Update Baseline in DB
        baseline_record = db.query(ProductCarbonBaseline).filter(
            ProductCarbonBaseline.product_id == req.product_id
        ).first()

        if baseline_record:
            baseline_record.cradle_to_gate_co2e = total_co2e_rounded
            baseline_record.calculation_metadata = meta.model_dump()
            baseline_record.vendor_id = req.vendor_id or baseline_record.vendor_id
        else:
            baseline_record = ProductCarbonBaseline(
                product_id=req.product_id,
                vendor_id=req.vendor_id or "default_vendor",
                cradle_to_gate_co2e=total_co2e_rounded,
                calculation_metadata=meta.model_dump()
            )
            db.add(baseline_record)

        db.commit()

        # 4. Save to Cache
        cache.set(
            cache_key,
            {
                "cradle_to_gate_co2e_kg": total_co2e_rounded,
                "metadata": meta.model_dump()
            },
            ttl_seconds=86400
        )

        return total_co2e_rounded, meta

    @classmethod
    def invalidate_cache(cls, product_id: str) -> bool:
        """Invalidates the Redis / in-memory cache on product update."""
        return cache.delete(cls.get_cache_key(product_id))
