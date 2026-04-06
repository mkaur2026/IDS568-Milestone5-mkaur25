import time
import hashlib
from typing import Optional

from src.config import settings


class CacheEntry:
    def __init__(self, value, ttl_seconds: int):
        self.value = value
        self.expiry = time.time() + ttl_seconds


class InMemoryCache:
    def __init__(self):
        self.store = {}
        self.max_entries = settings.cache_max_entries
        self.ttl = settings.cache_ttl_seconds

    def _make_key(self, prompt: str, temperature: float, max_tokens: int):
        key_string = f"{prompt}_{temperature}_{max_tokens}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, prompt: str, temperature: float, max_tokens: int):
        key = self._make_key(prompt, temperature, max_tokens)

        if key not in self.store:
            return None

        entry = self.store[key]

        # Check expiration
        if time.time() > entry.expiry:
            del self.store[key]
            return None

        return entry.value

    def set(self, prompt: str, temperature: float, max_tokens: int, value):
        # Enforce max entries
        if len(self.store) >= self.max_entries:
            # Remove oldest
            oldest_key = min(
                self.store,
                key=lambda k: self.store[k].expiry
            )
            del self.store[oldest_key]

        key = self._make_key(prompt, temperature, max_tokens)

        self.store[key] = CacheEntry(
            value,
            self.ttl
        )


cache = InMemoryCache()
