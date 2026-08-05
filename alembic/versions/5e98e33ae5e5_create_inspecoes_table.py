"""create inspecoes table

Revision ID: 5e98e33ae5e5
Revises: 7bf899e1c97c
Create Date: 2026-08-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5e98e33ae5e5"
down_revision: Union[str, None] = "7bf899e1c97c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_inspecao_enum = postgresql.ENUM(
    "50_horas", "100_horas", "anual", "especial", "progressiva",
    name="tipo_inspecao",
)


def upgrade() -> None:
    tipo_inspecao_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "inspecoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ordem_servico_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("responsavel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "50_horas", "100_horas", "anual", "especial", "progressiva",
                name="tipo_inspecao", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("horas_aeronave", sa.Integer(), nullable=False),
        sa.Column("itens_executados", sa.Text(), nullable=False),
        sa.Column("pendencias", sa.Text(), nullable=True),
        sa.Column("proxima_inspecao", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ordem_servico_id"], ["ordens_servico.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["responsavel_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_inspecoes_ordem_servico_id", "inspecoes", ["ordem_servico_id"])


def downgrade() -> None:
    op.drop_index("ix_inspecoes_ordem_servico_id", table_name="inspecoes")
    op.drop_table("inspecoes")
    tipo_inspecao_enum.drop(op.get_bind(), checkfirst=True)
