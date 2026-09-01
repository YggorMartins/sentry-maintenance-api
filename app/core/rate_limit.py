"""Rate limiting com Redis em produção e fallback local em desenvolvimento."""

import hashlib
import threading
import time
from functools import lru_cache
from typing import Protocol

from redis import Redis
from redis.exceptions import RedisError

from app.config.settings import settings
from app.core.exceptions import (
    RateLimitBackendUnavailableError,
    RateLimitExceededError,
)


class RateLimitBackend(Protocol):
    def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        """Retorna segundos para nova tentativa, ou None quando permitido."""


class InMemoryRateLimitBackend:
    """Fallback thread-safe para desenvolvimento e testes de uma instância."""

    def __init__(self) -> None:
        self._entries: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        now = time.monotonic()
        with self._lock:
            count, expires_at = self._entries.get(key, (0, now + window_seconds))
            if now >= expires_at:
                count, expires_at = 0, now + window_seconds

            count += 1
            self._entries[key] = (count, expires_at)

            if len(self._entries) > 10_000:
                self._entries = {
                    entry_key: value
                    for entry_key, value in self._entries.items()
                    if value[1] > now
                }

            if count > limit:
                return max(1, int(expires_at - now))
            return None


class RedisRateLimitBackend:
    """Contador atômico compartilhado por todas as réplicas da API."""

    _CONSUME_SCRIPT = """
    local current = redis.call('INCR', KEYS[1])
    if current == 1 then
        redis.call('EXPIRE', KEYS[1], ARGV[1])
    end
    local ttl = redis.call('TTL', KEYS[1])
    if ttl < 0 then
        redis.call('EXPIRE', KEYS[1], ARGV[1])
        ttl = tonumber(ARGV[1])
    end
    if current > tonumber(ARGV[2]) then
        return ttl
    end
    return -1
    """

    def __init__(self, url: str) -> None:
        self._redis = Redis.from_url(url, decode_responses=True)

    def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        try:
            ttl = int(
                self._redis.eval(
                    self._CONSUME_SCRIPT,
                    1,
                    f"sentry:rate-limit:{key}",
                    window_seconds,
                    limit,
                )
            )
        except RedisError as exc:
            raise RateLimitBackendUnavailableError() from exc
        return max(1, ttl) if ttl >= 0 else None


class NoopRateLimitBackend:
    def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        return None


class RateLimiter:
    def __init__(self, backend: RateLimitBackend) -> None:
        self.backend = backend

    @staticmethod
    def _opaque_key(scope: str, identifier: str) -> str:
        digest = hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()
        return f"{scope}:{digest}"

    def enforce(self, scope: str, identifier: str, limit: int, window_seconds: int) -> None:
        retry_after = self.backend.consume(
            self._opaque_key(scope, identifier), limit, window_seconds
        )
        if retry_after is not None:
            raise RateLimitExceededError(retry_after)


@lru_cache
def get_rate_limiter() -> RateLimiter:
    if not settings.RATE_LIMIT_ENABLED:
        return RateLimiter(NoopRateLimitBackend())
    if settings.RATE_LIMIT_REDIS_URL:
        return RateLimiter(RedisRateLimitBackend(settings.RATE_LIMIT_REDIS_URL))
    return RateLimiter(InMemoryRateLimitBackend())
