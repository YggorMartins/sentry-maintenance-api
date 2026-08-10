"""
Model de Movimentação de Estoque.

É o "livro-razão": cada linha é um evento imutável de entrada ou saída.
O saldo atual da peça (Peca.quantidade_atual) é a soma de todas essas
movimentações, mantida pelo repository no momento da criação — nunca
editada nem removida depois (auditoria).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoMovimentacao
from app.database.session import Base
from app.models.mixins import UUIDMixin


class MovimentacaoEstoque(Base, UUIDMixin):
    __tablename__ = "movimentacoes_estoque"

    peca_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pecas.id", ondelete="RESTRICT"), nullable=False
    )
    ordem_servico_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("ordens_servico.id", ondelete="SET NULL"), nullable=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(TipoMovimentacao, name="tipo_movimentacao", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    peca = relationship("Peca")
    ordem_servico = relationship("OrdemServico")
    usuario = relationship("User")

    def __repr__(self) -> str:
        return f"<MovimentacaoEstoque {self.tipo.value} qtd={self.quantidade}>"
