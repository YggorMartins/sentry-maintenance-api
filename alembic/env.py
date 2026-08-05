"""
env.py do Alembic.

Diferente do template padrão, aqui a URL do banco vem do NOSSO
settings.py (que já lê o .env), e o metadata alvo é a Base declarativa
do projeto — assim `alembic revision --autogenerate` detecta
automaticamente os models conforme forem criados em app/models/.
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config.settings import settings
from app.database.session import Base

# Importar aqui todos os módulos de models para que fiquem registrados
# no Base.metadata antes do autogenerate rodar.
from app.models import aeronave, cliente, inspecao, motor, ordem_servico, refresh_token, user  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Roda as migrations em modo 'offline' (gera SQL sem conectar ao banco)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda as migrations em modo 'online' (conecta de fato ao banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
