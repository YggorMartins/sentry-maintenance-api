"""
Model de Ordem de Serviço — entidade central do sistema.

`numero` é preenchido pelo repository (via SEQUENCE do Postgres) antes
do insert, nunca pelo cliente da API. `data_fechamento` só é setada
pela transição de status no service — ver AeronaveService/OrdemServicoService.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CategoriaManutencao, StatusOS, TipoManutencao
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class OrdemServico(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ordens_servico"

    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    aeronave_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("aeronaves.id", ondelete="RESTRICT"), nullable=False
    )
    motor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("motores.id", ondelete="SET NULL"), nullable=True
    )
    mecanico_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    inspetor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_manutencao: Mapped[TipoManutencao] = mapped_column(
        Enum(TipoManutencao, name="tipo_manutencao", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=TipoManutencao.CORRETIVA,
    )
    categoria: Mapped[CategoriaManutencao] = mapped_column(
        Enum(CategoriaManutencao, name="categoria_manutencao", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=CategoriaManutencao.MECANICA,
    )
    custo_estimado: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    prazo: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[StatusOS] = mapped_column(
        Enum(StatusOS, name="status_os", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=StatusOS.ABERTA,
    )

    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_fechamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    horas_trabalhadas: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False, default=0)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    aeronave = relationship("Aeronave")
    motor = relationship("Motor")
    mecanico = relationship("User", foreign_keys=[mecanico_id])
    inspetor = relationship("User", foreign_keys=[inspetor_id])

    def __repr__(self) -> str:
        return f"<OrdemServico {self.numero} status={self.status.value}>"
