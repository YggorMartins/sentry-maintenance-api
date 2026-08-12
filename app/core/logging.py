"""
Configuração de logging da aplicação.

Chamado uma vez no startup (main.py). Em DEBUG=True, nível DEBUG e
formato mais verboso; em produção (DEBUG=False), nível INFO.
"""
import logging
import sys

from app.config.settings import settings


def setup_logging() -> None:
    nivel = logging.DEBUG if settings.DEBUG else logging.INFO

    formato = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.basicConfig(
        level=nivel,
        format=formato,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # SQLAlchemy é muito verboso em INFO/DEBUG (loga toda query) — deixamos
    # em WARNING por padrão, mesmo com DEBUG=True. Ativa `echo=True` na
    # engine (já configurado por settings.DEBUG) quando quiser ver o SQL.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
