"""
Model de Aeronave.

`motor_id` é nullable (uma aeronave pode estar temporariamente sem
motor instalado, ex: em manutenção pesada) mas UNIQUE — garante que um
mesmo motor nunca fique instalado em duas aeronaves ao mesmo tempo.
`cliente_id` é o proprietário, obrigatório.
"""
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CategoriaAeronave, StatusAeronave
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Aeronave(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "aeronaves"

    prefixo: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    fabricante: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    numero_serie: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    categoria: Mapped[CategoriaAeronave] = mapped_column(
        Enum(
            CategoriaAeronave,
            name="categoria_aeronave",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    horas_totais: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[StatusAeronave] = mapped_column(
        Enum(
            StatusAeronave,
            name="status_aeronave",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=StatusAeronave.ATIVA,
    )

    motor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("motores.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    motor = relationship("Motor")
    cliente = relationship("Cliente")

    def __repr__(self) -> str:
        return f"<Aeronave {self.prefixo} {self.fabricante} {self.modelo}>"
