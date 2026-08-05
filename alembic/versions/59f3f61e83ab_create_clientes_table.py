"""create clientes table

Revision ID: 59f3f61e83ab
Revises: 51ec54760953
Create Date: 2026-07-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "59f3f61e83ab"
down_revision: Union[str, None] = "51ec54760953"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_pessoa_enum = postgresql.ENUM("fisica", "juridica", name="tipo_pessoa")


def upgrade() -> None:
    tipo_pessoa_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "clientes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tipo_pessoa",
            postgresql.ENUM("fisica", "juridica", name="tipo_pessoa", create_type=False),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("cpf", sa.String(length=11), nullable=True),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("endereco_logradouro", sa.String(length=200), nullable=True),
        sa.Column("endereco_numero", sa.String(length=20), nullable=True),
        sa.Column("endereco_complemento", sa.String(length=100), nullable=True),
        sa.Column("endereco_bairro", sa.String(length=100), nullable=True),
        sa.Column("endereco_cidade", sa.String(length=100), nullable=True),
        sa.Column("endereco_uf", sa.String(length=2), nullable=True),
        sa.Column("endereco_cep", sa.String(length=8), nullable=True),
        sa.Column("telefone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(tipo_pessoa = 'fisica' AND cpf IS NOT NULL AND cnpj IS NULL) OR "
            "(tipo_pessoa = 'juridica' AND cnpj IS NOT NULL AND cpf IS NULL)",
            name="ck_clientes_documento_por_tipo_pessoa",
        ),
    )
    op.create_index("ix_clientes_cpf", "clientes", ["cpf"], unique=True)
    op.create_index("ix_clientes_cnpj", "clientes", ["cnpj"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_clientes_cnpj", table_name="clientes")
    op.drop_index("ix_clientes_cpf", table_name="clientes")
    op.drop_table("clientes")
    tipo_pessoa_enum.drop(op.get_bind(), checkfirst=True)
