"""
Model de Refresh Token.

Persistimos o `jti` (JWT ID) de cada refresh token emitido, não o token
inteiro — assim, mesmo que o banco vaze, não expomos tokens válidos,
apenas identificadores que já precisam ser combinados com uma
assinatura JWT válida para servir de algo.

Isso é o que viabiliza um "logout" de verdade (ver explicação na
Etapa 1 da conversa): revogar = marcar revoked=True para aquele jti.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class RefreshToken(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    jti: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<RefreshToken jti={self.jti} user_id={self.user_id} revoked={self.revoked}>"
