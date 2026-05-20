"""TTL in-memory cache for scraped content."""

import time
import threading


class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: object, ttl: int):
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def clear(self):
        with self._lock:
            self._store.clear()


cache = TTLCache()
