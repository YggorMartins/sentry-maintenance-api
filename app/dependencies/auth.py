"""
Dependencies de autenticação e autorização.

`get_current_user` decodifica o access token do header Authorization e
carrega o usuário do banco. `RoleChecker` é uma dependency
parametrizável para restringir endpoints por papel — uso:

    @router.delete("/clientes/{id}")
    def delete_cliente(
        ...,
        current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
    ):
        ...
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# HTTPBearer (não OAuth2PasswordBearer) porque nosso /auth/login usa um
# contrato JSON próprio ({"email", "password"}), não o fluxo OAuth2
# "password" padrão (form-urlencoded com "username"). HTTPBearer faz o
# Swagger mostrar um campo simples de "colar o token", sem tentar
# executar um login automático que não corresponde ao nosso endpoint.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
    except PyJWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_uuid)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


class RoleChecker:
    """Dependency parametrizável: restringe o endpoint a papéis específicos."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta ação.",
            )
        return current_user
