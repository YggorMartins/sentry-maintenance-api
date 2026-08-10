"""create pecas and movimentacoes_estoque tables

Revision ID: 69d8beb05be6
Revises: 5e98e33ae5e5
Create Date: 2026-08-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "69d8beb05be6"
down_revision: Union[str, None] = "5e98e33ae5e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_movimentacao_enum = postgresql.ENUM("entrada", "saida", name="tipo_movimentacao")


def upgrade() -> None:
    op.create_table(
        "pecas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("fornecedor", sa.String(length=150), nullable=True),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("localizacao", sa.String(length=100), nullable=True),
        sa.Column("lote", sa.String(length=50), nullable=True),
        sa.Column("quantidade_atual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pecas_codigo", "pecas", ["codigo"], unique=True)

    tipo_movimentacao_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "movimentacoes_estoque",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("peca_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordem_servico_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "tipo",
            postgresql.ENUM("entrada", "saida", name="tipo_movimentacao", create_type=False),
            nullable=False,
        ),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("data", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["peca_id"], ["pecas.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ordem_servico_id"], ["ordens_servico.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_movimentacoes_estoque_peca_id", "movimentacoes_estoque", ["peca_id"])


def downgrade() -> None:
    op.drop_index("ix_movimentacoes_estoque_peca_id", table_name="movimentacoes_estoque")
    op.drop_table("movimentacoes_estoque")
    tipo_movimentacao_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_pecas_codigo", table_name="pecas")
    op.drop_table("pecas")
