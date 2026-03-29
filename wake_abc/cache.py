"""In-memory cache with TTL support.

NOTE: This cache is per-process and does not persist across Vercel cold starts.
Inventory data is re-fetched after TTL expires or on a new function instance.
"""

import time

# TTL defaults in seconds
INVENTORY_TTL = 3600        # 1 hour
STORE_LOCATIONS_TTL = 86400  # 24 hours

_store: dict[str, tuple] = {}  # key -> (data, timestamp)


def get(key: str, ttl: float = INVENTORY_TTL):
    """Return cached data if it exists and hasn't expired, else None."""
    entry = _store.get(key)
    if entry and (time.time() - entry[1]) < ttl:
        return entry[0]
    return None


def set(key: str, data) -> None:
    """Store data in the cache."""
    _store[key] = (data, time.time())


def clear() -> None:
    """Clear all cached data."""
    _store.clear()
