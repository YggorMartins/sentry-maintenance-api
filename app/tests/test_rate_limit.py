import pytest

from app.core.exceptions import RateLimitExceededError
from app.core.rate_limit import InMemoryRateLimitBackend, RateLimiter


def test_rate_limiter_bloqueia_apos_o_limite_e_informa_retry_after():
    limiter = RateLimiter(InMemoryRateLimitBackend())

    limiter.enforce("login", "127.0.0.1:pessoa@example.com", 2, 60)
    limiter.enforce("login", "127.0.0.1:pessoa@example.com", 2, 60)

    with pytest.raises(RateLimitExceededError) as exc_info:
        limiter.enforce("login", "127.0.0.1:pessoa@example.com", 2, 60)

    assert 1 <= exc_info.value.retry_after <= 60


def test_chave_de_rate_limit_nao_expoe_identificador():
    key = RateLimiter._opaque_key("login", "Pessoa@Example.com")

    assert key.startswith("login:")
    assert "pessoa@example.com" not in key
