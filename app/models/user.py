"""
Model de usuário.

Esta tabela cobre autenticação (email/senha) e autorização (role).
Dados de "Cliente" como pessoa física/jurídica NÃO ficam aqui — isso
vai para o model Cliente (Etapa 2), que poderá se relacionar com um
User quando o cliente também precisar logar no sistema.
"""
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.roles import UserRole
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=UserRole.CLIENTE,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"
