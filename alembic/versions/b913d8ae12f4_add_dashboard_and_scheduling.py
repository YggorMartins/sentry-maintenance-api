"""add dashboard fields and maintenance scheduling

Revision ID: b913d8ae12f4
Revises: 69d8beb05be6
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b913d8ae12f4"
down_revision: Union[str, None] = "69d8beb05be6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_manutencao = postgresql.ENUM("preventiva", "corretiva", "inspecao", "preditiva", name="tipo_manutencao", create_type=False)
categoria_manutencao = postgresql.ENUM("avionicos", "mecanica", "estrutura", "motor", name="categoria_manutencao", create_type=False)
recorrencia_manutencao = postgresql.ENUM("nenhuma", "semanal", "mensal", "trimestral", "anual", name="recorrencia_manutencao", create_type=False)
status_agendamento = postgresql.ENUM("agendado", "confirmado", "concluido", "cancelado", name="status_agendamento", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    tipo_manutencao.create(bind, checkfirst=True)
    categoria_manutencao.create(bind, checkfirst=True)
    recorrencia_manutencao.create(bind, checkfirst=True)
    status_agendamento.create(bind, checkfirst=True)

    op.add_column("ordens_servico", sa.Column("tipo_manutencao", tipo_manutencao, nullable=False, server_default="corretiva"))
    op.add_column("ordens_servico", sa.Column("categoria", categoria_manutencao, nullable=False, server_default="mecanica"))
    op.add_column("ordens_servico", sa.Column("custo_estimado", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("ordens_servico", sa.Column("prazo", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_ordens_servico_prazo", "ordens_servico", ["prazo"])
    op.create_index("ix_ordens_servico_status_data", "ordens_servico", ["status", "data_abertura"])

    op.add_column("pecas", sa.Column("estoque_minimo", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("pecas", sa.Column("categoria", sa.String(length=80), nullable=False, server_default="componente"))
    op.create_index("ix_pecas_estoque_alerta", "pecas", ["quantidade_atual", "estoque_minimo"])

    op.create_table(
        "agendamentos_manutencao",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("aeronave_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tecnico_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("titulo", sa.String(length=160), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fim", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tipo", tipo_manutencao, nullable=False),
        sa.Column("recorrencia", recorrencia_manutencao, nullable=False, server_default="nenhuma"),
        sa.Column("recorrencia_ate", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", status_agendamento, nullable=False, server_default="agendado"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["aeronave_id"], ["aeronaves.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tecnico_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_agendamentos_aeronave_id", "agendamentos_manutencao", ["aeronave_id"])
    op.create_index("ix_agendamentos_tecnico_id", "agendamentos_manutencao", ["tecnico_id"])
    op.create_index("ix_agendamentos_inicio", "agendamentos_manutencao", ["inicio"])


def downgrade() -> None:
    op.drop_table("agendamentos_manutencao")
    op.drop_index("ix_pecas_estoque_alerta", table_name="pecas")
    op.drop_column("pecas", "categoria")
    op.drop_column("pecas", "estoque_minimo")
    op.drop_index("ix_ordens_servico_status_data", table_name="ordens_servico")
    op.drop_index("ix_ordens_servico_prazo", table_name="ordens_servico")
    op.drop_column("ordens_servico", "prazo")
    op.drop_column("ordens_servico", "custo_estimado")
    op.drop_column("ordens_servico", "categoria")
    op.drop_column("ordens_servico", "tipo_manutencao")
    status_agendamento.drop(op.get_bind(), checkfirst=True)
    recorrencia_manutencao.drop(op.get_bind(), checkfirst=True)
    categoria_manutencao.drop(op.get_bind(), checkfirst=True)
    tipo_manutencao.drop(op.get_bind(), checkfirst=True)
