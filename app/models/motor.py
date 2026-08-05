"""
Model de Motor.

É uma entidade independente de Aeronave (não um campo embutido) porque
motores são removidos, trocados e mantidos em estoque separadamente na
manutenção aeronáutica real — ver explicação completa na conversa da
Etapa 3.
"""
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Motor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "motores"

    fabricante: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    numero_serie: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Horas em décimos (ex: 1234 = 123.4h) evitaria ponto flutuante, mas
    # para o escopo deste portfólio usamos Integer representando horas
    # cheias — decisão documentada para eu lembrar do trade-off depois.
    tsn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Time Since New
    tso: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Time Since Overhaul
    tbo: Mapped[int] = mapped_column(Integer, nullable=False)  # Time Between Overhaul (do fabricante)

    ultima_inspecao: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<Motor {self.fabricante} {self.modelo} SN={self.numero_serie}>"
