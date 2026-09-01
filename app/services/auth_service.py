"""
Service de autenticação.

Contém a REGRA DE NEGÓCIO de login/refresh/logout. Não sabe nada de
HTTP (nada de HTTPException aqui) — levanta exceções de domínio
(app.core.exceptions), que o router traduz para respostas HTTP.
"""
import uuid
from datetime import datetime, timezone

from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_and_update_password,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.core.roles import UserRole
from app.schemas.user import UserCreate, UserRegistration


_DUMMY_PASSWORD_HASH = hash_password("comparacao-constante-para-usuario-ausente")


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(self, data: UserRegistration) -> User:
        if self.users.get_by_email(data.email) is not None:
            raise UserAlreadyExistsError()
        return self.users.create(
            UserCreate(**data.model_dump(), role=UserRole.CLIENTE)
        )

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id))
        self.refresh_tokens.create(user_id=user.id, jti=jti, expires_at=expires_at)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.users.get_by_email(email)
        if user is None:
            # Mantém custo semelhante ao login de uma conta existente e
            # reduz enumeração de emails por diferença de tempo.
            verify_and_update_password(password, _DUMMY_PASSWORD_HASH)
            raise InvalidCredentialsError()
        valid_password, updated_hash = verify_and_update_password(
            password, user.hashed_password
        )
        if not valid_password:
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()
        if updated_hash is not None:
            self.users.update_password_hash(user, updated_hash)
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except PyJWTError:
            raise InvalidTokenError()

        if payload.get("type") != "refresh":
            raise InvalidTokenError()

        try:
            jti = uuid.UUID(payload["jti"])
        except (KeyError, TypeError, ValueError):
            raise InvalidTokenError()
        stored = self.refresh_tokens.get_by_jti(jti)

        if stored is None or stored.revoked:
            raise InvalidTokenError()
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            # Alguns drivers (notadamente SQLite) descartam o tzinfo ao
            # desserializar DateTime. O valor persistido é sempre UTC.
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise InvalidTokenError()

        user = self.users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError()

        # Rotação: revoga o refresh token usado e emite um par novo.
        self.refresh_tokens.revoke(jti)
        return self._issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except PyJWTError:
            raise InvalidTokenError()

        if payload.get("type") != "refresh":
            raise InvalidTokenError()

        try:
            jti = uuid.UUID(payload["jti"])
        except (KeyError, TypeError, ValueError):
            raise InvalidTokenError()
        self.refresh_tokens.revoke(jti)
