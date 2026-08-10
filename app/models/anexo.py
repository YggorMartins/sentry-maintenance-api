"""
Model de Anexo.

`entidade_tipo` + `entidade_id` formam uma associação polimórfica: não
há FOREIGN KEY nativa (o Postgres não valida automaticamente que o
UUID existe na tabela certa) — a validação de existência é feita no
service. Ver explicação completa na conversa da Etapa 7.
"""
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoEntidadeAnexo
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Anexo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "anexos"

    entidade_tipo: Mapped[TipoEntidadeAnexo] = mapped_column(
        Enum(
            TipoEntidadeAnexo,
            name="tipo_entidade_anexo",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        index=True,
    )
    entidade_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)

    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    usuario = relationship("User")

    def __repr__(self) -> str:
        return f"<Anexo {self.nome_original} ({self.entidade_tipo.value}/{self.entidade_id})>"
