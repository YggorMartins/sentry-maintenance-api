"""create anexos table

Revision ID: 2790914816f0
Revises: 69d8beb05be6
Create Date: 2026-08-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2790914816f0"
down_revision: Union[str, None] = "69d8beb05be6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_entidade_anexo_enum = postgresql.ENUM(
    "aeronave", "ordem_servico", "cliente", "inspecao", name="tipo_entidade_anexo"
)


def upgrade() -> None:
    tipo_entidade_anexo_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "anexos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "entidade_tipo",
            postgresql.ENUM(
                "aeronave", "ordem_servico", "cliente", "inspecao",
                name="tipo_entidade_anexo", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("entidade_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome_original", sa.String(length=255), nullable=False),
        sa.Column("caminho_arquivo", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("tamanho_bytes", sa.BigInteger(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_anexos_entidade_tipo", "anexos", ["entidade_tipo"])
    op.create_index("ix_anexos_entidade_id", "anexos", ["entidade_id"])


def downgrade() -> None:
    op.drop_index("ix_anexos_entidade_id", table_name="anexos")
    op.drop_index("ix_anexos_entidade_tipo", table_name="anexos")
    op.drop_table("anexos")
    tipo_entidade_anexo_enum.drop(op.get_bind(), checkfirst=True)
