"""
Funções puras de segurança: hash de senha e criação/decodificação de JWT.

Este módulo não conhece banco de dados nem HTTP — só criptografia.
Isso permite testá-lo isoladamente (unit test puro, sem mocks pesados).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Senhas ---

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT ---

def create_access_token(subject: str, role: str) -> str:
    """Access token de vida curta. `subject` é o id (str) do usuário."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, uuid.UUID, datetime]:
    """
    Refresh token de vida longa. Retorna (token, jti, expires_at) para
    que o caller persista o jti em banco (ver RefreshToken model).
    """
    jti = uuid.uuid4()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": str(jti),
        "exp": expire,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict[str, Any]:
    """Levanta jose.JWTError se o token for inválido ou estiver expirado."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise exc
