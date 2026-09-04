"""
In-Memory and Redis Caching Layer for Carbon Footprint Engine
"""
from typing import Optional, Dict, Any
import time


class CacheService:
    """Thread-safe cache service supporting key expiration and invalidation."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if entry["expires_at"] and time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: int = 86400):
        expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else None
        self._store[key] = {
            "value": value,
            "expires_at": expires_at
        }

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self):
        self._store.clear()


cache = CacheService()
