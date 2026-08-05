"""
Testes unitários da camada de segurança.

Como app.core.security não depende de banco nem de FastAPI, estes
testes rodam isolados e rápidos — não precisam do docker-compose de pé.
"""
import time

import pytest
from jose import jwt

from app.config.settings import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_gera_hash_diferente_da_senha_original():
    plain = "minhaSenhaForte123"
    hashed = hash_password(plain)
    assert hashed != plain


def test_verify_password_aceita_senha_correta():
    plain = "minhaSenhaForte123"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_rejeita_senha_incorreta():
    hashed = hash_password("minhaSenhaForte123")
    assert verify_password("senhaErrada", hashed) is False


def test_hash_password_gera_salts_diferentes_para_mesma_senha():
    plain = "minhaSenhaForte123"
    assert hash_password(plain) != hash_password(plain)


def test_create_access_token_contem_claims_esperadas():
    token = create_access_token(subject="user-123", role="admin")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_create_refresh_token_contem_jti_unico():
    token1, jti1, _ = create_refresh_token(subject="user-123")
    token2, jti2, _ = create_refresh_token(subject="user-123")
    assert jti1 != jti2
    assert token1 != token2


def test_decode_token_levanta_erro_para_token_invalido():
    from jose import JWTError

    with pytest.raises(JWTError):
        decode_token("token.invalido.aqui")
