"""
Router de autenticação.

Responsabilidade única: traduzir HTTP <-> Service. Nenhuma regra de
negócio mora aqui — só validação de schema (feita pelo FastAPI/Pydantic
automaticamente), chamada ao service e tradução de exceção de domínio
para status HTTP.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    RateLimitBackendUnavailableError,
    RateLimitExceededError,
    UserAlreadyExistsError,
)
from app.config.settings import settings
from app.core.rate_limit import get_rate_limiter
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserOut, UserRegistration
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _enforce_rate_limit(
    request: Request,
    scope: str,
    identifier: str,
    limit: int,
    window_seconds: int,
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    try:
        get_rate_limiter().enforce(
            scope=scope,
            identifier=f"{client_ip}:{identifier}",
            limit=limit,
            window_seconds=window_seconds,
        )
    except RateLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Aguarde antes de tentar novamente.",
            headers={"Retry-After": str(exc.retry_after)},
        )
    except RateLimitBackendUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível.",
            headers={"Retry-After": "30"},
        )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegistration, request: Request, db: Session = Depends(get_db)):
    _enforce_rate_limit(
        request,
        "register",
        "public",
        settings.REGISTER_RATE_LIMIT,
        settings.REGISTER_RATE_WINDOW_SECONDS,
    )
    service = AuthService(db)
    try:
        return service.register(data)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este email.",
        )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    _enforce_rate_limit(
        request,
        "login",
        str(data.email),
        settings.LOGIN_RATE_LIMIT,
        settings.LOGIN_RATE_WINDOW_SECONDS,
    )
    service = AuthService(db)
    try:
        return service.login(data.email, data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
        )
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado. Contate um administrador.",
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    _enforce_rate_limit(
        request,
        "refresh",
        "token",
        settings.REFRESH_RATE_LIMIT,
        settings.REFRESH_RATE_WINDOW_SECONDS,
    )
    service = AuthService(db)
    try:
        return service.refresh(data.refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido, expirado ou revogado.",
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        service.logout(data.refresh_token)
    except InvalidTokenError:
        # Logout é idempotente do ponto de vista do cliente: mesmo que o
        # token já esteja inválido, o resultado desejado (sessão encerrada)
        # já foi alcançado, então não é necessário retornar erro aqui.
        pass


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
