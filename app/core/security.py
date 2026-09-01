"""
Funções puras de segurança: hash de senha e criação/decodificação de JWT.

Este módulo não conhece banco de dados nem HTTP — só criptografia.
Isso permite testá-lo isoladamente (unit test puro, sem mocks pesados).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config.settings import settings

# Argon2id é usado para novas senhas. Bcrypt permanece apenas como verificador
# de legado; verify_and_update gera um hash Argon2 para migração transparente.
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))


# --- Senhas ---

def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    valid, _ = verify_and_update_password(plain_password, hashed_password)
    return valid


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    """Valida a senha e sugere um hash Argon2 quando o formato é legado."""
    try:
        return password_hash.verify_and_update(plain_password, hashed_password)
    except (PwdlibError, ValueError):
        # Hash ausente/corrompido no banco não deve derrubar o endpoint de login.
        return False, None


# --- JWT ---

def create_access_token(subject: str, role: str) -> str:
    """Access token de vida curta. `subject` é o id (str) do usuário."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, uuid.UUID, datetime]:
    """
    Refresh token de vida longa. Retorna (token, jti, expires_at) para
    que o caller persista o jti em banco (ver RefreshToken model).
    """
    jti = uuid.uuid4()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": str(jti),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict[str, Any]:
    """Valida assinatura, algoritmo, emissor, audiência e claims temporais."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={
                "require": ["sub", "type", "jti", "iss", "aud", "iat", "nbf", "exp"]
            },
        )
    except PyJWTError as exc:
        raise exc
