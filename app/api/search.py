"""
Search API Router for ETMS
Faceted full-text search across enterprise tickets and service catalog.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Query
from app.services.search_service import SearchService

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=Dict[str, Any])
def search_tickets(
    q: str = Query("", description="Full text search keyword"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Faceted search endpoint returning hits, took_ms, and aggregations."""
    return SearchService.execute_search(
        query=q,
        category=category,
        status=status,
        priority=priority,
        page=page,
        page_size=page_size
    )
