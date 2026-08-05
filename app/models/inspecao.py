"""
Model de Inspeção.

Pertence a uma Ordem de Serviço (não à Aeronave diretamente) — ver
explicação completa na conversa da Etapa 5. A aeronave é acessível via
`inspecao.ordem_servico.aeronave`.
"""
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoInspecao
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Inspecao(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "inspecoes"

    ordem_servico_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False
    )
    responsavel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    tipo: Mapped[TipoInspecao] = mapped_column(
        Enum(TipoInspecao, name="tipo_inspecao", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    horas_aeronave: Mapped[int] = mapped_column(Integer, nullable=False)

    itens_executados: Mapped[str] = mapped_column(Text, nullable=False)
    pendencias: Mapped[str | None] = mapped_column(Text, nullable=True)
    proxima_inspecao: Mapped[date | None] = mapped_column(Date, nullable=True)

    ordem_servico = relationship("OrdemServico")
    responsavel = relationship("User")

    def __repr__(self) -> str:
        return f"<Inspecao {self.tipo.value} data={self.data}>"
