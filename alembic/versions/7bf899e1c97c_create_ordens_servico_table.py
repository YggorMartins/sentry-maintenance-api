"""create ordens_servico table and os_numero_seq sequence

Revision ID: 7bf899e1c97c
Revises: a692f9af66d6
Create Date: 2026-08-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7bf899e1c97c"
down_revision: Union[str, None] = "a692f9af66d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

status_os_enum = postgresql.ENUM(
    "aberta", "em_andamento", "aguardando_pecas", "concluida", "cancelada",
    name="status_os",
)


def upgrade() -> None:
    # SEQUENCE dedicada para gerar o número da OS de forma atômica
    # (ver explicação na conversa da Etapa 4).
    op.execute("CREATE SEQUENCE IF NOT EXISTS os_numero_seq START WITH 1 INCREMENT BY 1")

    status_os_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "ordens_servico",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(length=20), nullable=False),
        sa.Column("aeronave_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("motor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mecanico_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("inspetor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "aberta", "em_andamento", "aguardando_pecas", "concluida", "cancelada",
                name="status_os", create_type=False,
            ),
            nullable=False,
            server_default="aberta",
        ),
        sa.Column("data_abertura", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_fechamento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("horas_trabalhadas", sa.Numeric(6, 1), nullable=False, server_default="0"),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["aeronave_id"], ["aeronaves.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["motor_id"], ["motores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mecanico_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inspetor_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ordens_servico_numero", "ordens_servico", ["numero"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_ordens_servico_numero", table_name="ordens_servico")
    op.drop_table("ordens_servico")
    status_os_enum.drop(op.get_bind(), checkfirst=True)
    op.execute("DROP SEQUENCE IF EXISTS os_numero_seq")
