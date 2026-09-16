import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RecorrenciaManutencao, StatusAgendamento, TipoManutencao
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class AgendamentoManutencao(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agendamentos_manutencao"

    aeronave_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("aeronaves.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tecnico_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tipo: Mapped[TipoManutencao] = mapped_column(
        Enum(TipoManutencao, name="tipo_manutencao", values_callable=lambda cls: [e.value for e in cls]),
        nullable=False,
    )
    recorrencia: Mapped[RecorrenciaManutencao] = mapped_column(
        Enum(RecorrenciaManutencao, name="recorrencia_manutencao", values_callable=lambda cls: [e.value for e in cls]),
        nullable=False,
        default=RecorrenciaManutencao.NENHUMA,
    )
    recorrencia_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[StatusAgendamento] = mapped_column(
        Enum(StatusAgendamento, name="status_agendamento", values_callable=lambda cls: [e.value for e in cls]),
        nullable=False,
        default=StatusAgendamento.AGENDADO,
    )

    aeronave = relationship("Aeronave")
    tecnico = relationship("User")
