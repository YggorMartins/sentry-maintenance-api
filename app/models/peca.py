"""
Model de Peça.

`quantidade_atual` é mantido pelo sistema (repository de movimentação),
nunca editado diretamente via PUT — ver explicação na conversa da
Etapa 6.
"""
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Peca(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pecas"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    fornecedor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    localizacao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lote: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantidade_atual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False, default="componente")

    def __repr__(self) -> str:
        return f"<Peca {self.codigo} qtd={self.quantidade_atual}>"
