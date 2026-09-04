"""
Pydantic Schemas for Carbon Footprint Engine Requests and Responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class MaterialComposition(BaseModel):
    material_name: str = Field(..., description="Name of the raw material (e.g. Organic Cotton)")
    percentage: float = Field(..., ge=0, le=100, description="Percentage share in product (0-100)")
    source: Optional[str] = Field(default=None, description="Optional origin / source database note")


class CalculateBaselineRequest(BaseModel):
    product_id: str = Field(..., description="Unique product SKU or identifier")
    vendor_id: Optional[str] = Field(default="default_vendor", description="Vendor UUID or identifier")
    weight_kg: float = Field(..., gt=0, description="Weight of the product in kilograms")
    materials: List[MaterialComposition] = Field(..., min_length=1, description="List of materials")

    @model_validator(mode="after")
    def validate_material_sum(self):
        total_pct = sum(m.percentage for m in self.materials)
        if round(total_pct, 2) != 100.0:
            raise ValueError("Material composition percentages must equal exactly 100%")
        return self


class BaselineCalculationMetadata(BaseModel):
    formula: str
    material_breakdown: List[Dict[str, Any]]
    fallback_applied: bool = False
    warning: Optional[str] = None
    cached: bool = False


class CalculateBaselineResponse(BaseModel):
    product_id: str
    cradle_to_gate_co2e_kg: float
    calculation_metadata: BaselineCalculationMetadata


class CalculateShippingRequest(BaseModel):
    origin_zip: str = Field(..., description="Origin postal code")
    destination_zip: str = Field(..., description="Destination postal code")
    weight_kg: float = Field(..., description="Weight in kilograms")
    carrier: str = Field(default="UPS", description="Carrier code (USPS, UPS, FedEx, DHL)")


class CalculateShippingResponse(BaseModel):
    shipping_co2e_kg: float
    distance_km: float
    carrier: str
    fallback_applied: bool = False


class PurchaseOffsetRequest(BaseModel):
    order_id: str
    customer_id: str
    total_carbon_kg: float = Field(..., gt=0)
    project_id: Optional[str] = "proj_prod_wind_energy_099"


class PurchaseOffsetResponse(BaseModel):
    transaction_id: str
    amount_kg: float
    price_usd: float
    status: str
    certificate_url: Optional[str] = None
    retry_queued: bool = False


class CreateLedgerEntryRequest(BaseModel):
    order_id: str
    customer_id: str
    total_product_co2e: float = Field(..., ge=0)
    total_shipping_co2e: float = Field(..., ge=0)
    is_offset: bool = False
    offset_amount_usd: float = Field(default=0.0, ge=0)
    offset_provider_transaction_id: Optional[str] = None
    offset_certificate_url: Optional[str] = None


class LedgerEntryResponse(BaseModel):
    ledger_id: str
    order_id: str
    customer_id: str
    total_product_co2e: float
    total_shipping_co2e: float
    total_order_co2e: float
    is_offset: bool
    offset_amount_usd: float
    offset_provider_transaction_id: Optional[str]
    offset_certificate_url: Optional[str]
    block_hash: str
    previous_block_hash: Optional[str]
    created_at: str
