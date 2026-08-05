"""create motores and aeronaves tables

Revision ID: a692f9af66d6
Revises: 59f3f61e83ab
Create Date: 2026-08-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a692f9af66d6"
down_revision: Union[str, None] = "59f3f61e83ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

categoria_aeronave_enum = postgresql.ENUM(
    "monomotor", "multimotor", "helicoptero", "turboprop", "jato",
    name="categoria_aeronave",
)
status_aeronave_enum = postgresql.ENUM(
    "ativa", "em_manutencao", "inativa", name="status_aeronave"
)


def upgrade() -> None:
    op.create_table(
        "motores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fabricante", sa.String(length=100), nullable=False),
        sa.Column("modelo", sa.String(length=100), nullable=False),
        sa.Column("numero_serie", sa.String(length=50), nullable=False),
        sa.Column("tsn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tso", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tbo", sa.Integer(), nullable=False),
        sa.Column("ultima_inspecao", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_motores_numero_serie", "motores", ["numero_serie"], unique=True)

    categoria_aeronave_enum.create(op.get_bind(), checkfirst=True)
    status_aeronave_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "aeronaves",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("prefixo", sa.String(length=10), nullable=False),
        sa.Column("fabricante", sa.String(length=100), nullable=False),
        sa.Column("modelo", sa.String(length=100), nullable=False),
        sa.Column("numero_serie", sa.String(length=50), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column(
            "categoria",
            postgresql.ENUM(
                "monomotor", "multimotor", "helicoptero", "turboprop", "jato",
                name="categoria_aeronave", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("horas_totais", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ativa", "em_manutencao", "inativa",
                name="status_aeronave", create_type=False,
            ),
            nullable=False,
            server_default="ativa",
        ),
        sa.Column("motor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["motor_id"], ["motores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_aeronaves_prefixo", "aeronaves", ["prefixo"], unique=True)
    op.create_index("ix_aeronaves_numero_serie", "aeronaves", ["numero_serie"], unique=True)
    op.create_index("ix_aeronaves_motor_id", "aeronaves", ["motor_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_aeronaves_motor_id", table_name="aeronaves")
    op.drop_index("ix_aeronaves_numero_serie", table_name="aeronaves")
    op.drop_index("ix_aeronaves_prefixo", table_name="aeronaves")
    op.drop_table("aeronaves")
    status_aeronave_enum.drop(op.get_bind(), checkfirst=True)
    categoria_aeronave_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_motores_numero_serie", table_name="motores")
    op.drop_table("motores")
