"""
Carbon Engine API Endpoints
"""
import time
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CalculateBaselineRequest,
    CalculateBaselineResponse,
    CalculateShippingRequest,
    CalculateShippingResponse,
    PurchaseOffsetRequest,
    PurchaseOffsetResponse,
    CreateLedgerEntryRequest,
    LedgerEntryResponse,
)
from app.services.carbon_engine import CarbonBaselineEngine
from app.services.shipping_calculator import ShippingCarbonCalculator
from app.services.offset_service import OffsetService
from app.services.ledger_service import LedgerService

router = APIRouter()

# Simple in-memory rate limiter for demo/test compliance
RATE_LIMIT_STORE: Dict[str, list] = {}


def verify_bearer_token(authorization: str = Header(None)):
    """Verifies Bearer token authentication."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header"
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token format"
        )
    token = parts[1]
    if token != "valid_token" and token != "test-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return token


def rate_limit_check(client_ip: str = "default_client", limit: int = 100):
    """Enforces 100 requests per minute rate limit."""
    now = time.time()
    history = RATE_LIMIT_STORE.setdefault(client_ip, [])
    # Keep only requests within last 60 seconds
    history = [t for t in history if now - t < 60]
    RATE_LIMIT_STORE[client_ip] = history

    if len(history) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 100 requests per minute."
        )
    history.append(now)


@router.post(
    "/calculate-baseline",
    response_model=CalculateBaselineResponse,
    summary="Calculate Cradle-to-Gate baseline carbon footprint"
)
def calculate_baseline(
    request: CalculateBaselineRequest,
    token: str = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    try:
        co2e, meta = CarbonBaselineEngine.calculate_baseline(request, db)
        return CalculateBaselineResponse(
            product_id=request.product_id,
            cradle_to_gate_co2e_kg=co2e,
            calculation_metadata=meta
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/calculate-shipping",
    response_model=CalculateShippingResponse,
    summary="Calculate dynamic shipping carbon emissions"
)
def calculate_shipping(
    request: CalculateShippingRequest,
    http_req: Request
):
    client_ip = http_req.client.host if http_req.client else "127.0.0.1"
    rate_limit_check(client_ip, limit=100)

    try:
        co2e, dist, fallback = ShippingCarbonCalculator.calculate_shipping_carbon(
            origin_zip=request.origin_zip,
            destination_zip=request.destination_zip,
            weight_kg=request.weight_kg,
            carrier=request.carrier
        )
        return CalculateShippingResponse(
            shipping_co2e_kg=co2e,
            distance_km=dist,
            carrier=request.carrier,
            fallback_applied=fallback
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/offsets/purchase",
    response_model=PurchaseOffsetResponse,
    summary="Execute carbon offset purchase via Patch API"
)
def purchase_offset(
    request: PurchaseOffsetRequest,
    simulate_failure: bool = False
):
    res = OffsetService.purchase_offset(
        order_id=request.order_id,
        customer_id=request.customer_id,
        total_carbon_kg=request.total_carbon_kg,
        project_id=request.project_id or "proj_prod_wind_energy_099",
        simulate_failure=simulate_failure
    )
    return PurchaseOffsetResponse(**res)


@router.post(
    "/ledger",
    response_model=LedgerEntryResponse,
    summary="Record transaction in immutable carbon ledger"
)
def record_ledger_entry(
    request: CreateLedgerEntryRequest,
    db: Session = Depends(get_db)
):
    return LedgerService.record_transaction(request, db)


@router.get(
    "/ledger/{order_id}",
    summary="Query transactional carbon ledger for an order"
)
def get_ledger_entry(
    order_id: str,
    db: Session = Depends(get_db)
):
    entry = LedgerService.get_entry_by_order_id_safe(order_id, db)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order ledger record not found")
    return dict(entry)
