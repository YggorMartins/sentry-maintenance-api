"""
Configuração da engine e das sessões do SQLAlchemy 2.0.

Este é o ÚNICO lugar onde a engine é criada. Repositórios recebem
a sessão via injeção de dependência (get_db), nunca importam a engine
diretamente.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # evita erros de "conexão morta" em pools longos
    echo=settings.DEBUG,  # loga SQL gerado apenas em modo debug
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Classe base declarativa. Todos os models herdam daqui."""
    pass


def get_db() -> Generator:
    """
    Dependência do FastAPI que fornece uma sessão de banco por requisição
    e garante que ela seja sempre fechada, mesmo em caso de exceção.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
