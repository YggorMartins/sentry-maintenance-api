"""
Model de Cliente.

Unifica Pessoa Física e Pessoa Jurídica numa única tabela (ver
explicação de arquitetura na conversa da Etapa 2). A CheckConstraint
garante, a nível de banco, que o documento certo está preenchido para
o tipo de pessoa — essa é a nossa última linha de defesa mesmo que
alguém insira dados direto no banco, ignorando a API.
"""
from sqlalchemy import CheckConstraint, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import TipoPessoa
from app.database.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Cliente(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clientes"
    __table_args__ = (
        CheckConstraint(
            "(tipo_pessoa = 'fisica' AND cpf IS NOT NULL AND cnpj IS NULL) OR "
            "(tipo_pessoa = 'juridica' AND cnpj IS NOT NULL AND cpf IS NULL)",
            name="ck_clientes_documento_por_tipo_pessoa",
        ),
    )

    tipo_pessoa: Mapped[TipoPessoa] = mapped_column(
        Enum(TipoPessoa, name="tipo_pessoa", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(11), unique=True, index=True, nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(14), unique=True, index=True, nullable=True)

    # Endereço (colunas simples: cobre a necessidade atual sem introduzir
    # uma tabela separada; se no futuro clientes puderem ter múltiplos
    # endereços, isso vira uma tabela própria).
    endereco_logradouro: Mapped[str | None] = mapped_column(String(200), nullable=True)
    endereco_numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    endereco_complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endereco_bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endereco_cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endereco_uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    endereco_cep: Mapped[str | None] = mapped_column(String(8), nullable=True)

    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Cliente {self.nome} ({self.tipo_pessoa.value})>"
