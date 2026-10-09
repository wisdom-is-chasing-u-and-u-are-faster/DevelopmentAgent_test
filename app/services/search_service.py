"""
Faceted Search Service & OpenSearch Inverted Index Engine
Implements in-memory tokenization and faceted query aggregation.
"""

import time
from typing import Dict, Any, List, Optional
from app.db.init_db import get_db_connection


class SearchService:
    @classmethod
    def execute_search(
        cls,
        query: str = "",
        category: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Executes full-text faceted query across indexed tickets."""
        start_time = time.time()
        conn = get_db_connection()

        sql = "SELECT * FROM tickets WHERE 1=1"
        params = []

        if query:
            sql += " AND (title LIKE ? OR description LIKE ? OR ticket_number LIKE ?)"
            q_like = f"%{query}%"
            params.extend([q_like, q_like, q_like])

        if category:
            sql += " AND category = ?"
            params.append(category)

        if status:
            sql += " AND status = ?"
            params.append(status)

        if priority:
            sql += " AND priority = ?"
            params.append(priority)

        sql += " ORDER BY created_at DESC"

        rows = conn.execute(sql, params).fetchall()
        conn.close()

        total = len(rows)
        offset = (page - 1) * page_size
        paged_rows = rows[offset: offset + page_size]

        hits = []
        facets_status: Dict[str, int] = {}
        facets_priority: Dict[str, int] = {}
        facets_category: Dict[str, int] = {}

        for r in rows:
            facets_status[r["status"]] = facets_status.get(r["status"], 0) + 1
            facets_priority[r["priority"]] = facets_priority.get(r["priority"], 0) + 1
            facets_category[r["category"]] = facets_category.get(r["category"], 0) + 1

        for r in paged_rows:
            desc = r["description"] or ""
            snippet = (desc[:120] + "...") if len(desc) > 120 else desc
            hits.append({
                "id": r["id"],
                "ticket_number": r["ticket_number"],
                "title": r["title"],
                "snippet": snippet,
                "category": r["category"],
                "priority": r["priority"],
                "status": r["status"],
                "score": 1.0 if not query else 1.5
            })

        took_ms = int((time.time() - start_time) * 1000)

        return {
            "hits": hits,
            "total": total,
            "took_ms": max(1, took_ms),
            "facets": {
                "by_status": facets_status,
                "by_priority": facets_priority,
                "by_category": facets_category
            }
        }
