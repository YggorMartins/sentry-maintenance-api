"""Fixtures dos testes de integração.

Por padrão, os fluxos HTTP usam SQLite em memória: a suíte completa
roda localmente sem Docker e o banco só é criado quando um teste pede
o fixture ``client``. Definir ``TEST_DATABASE_URL`` troca o backend por
um PostgreSQL dedicado, sem nunca reutilizar o banco de desenvolvimento.

O isolamento é por teste: SQLite tem suas tabelas limpas ao final; no
PostgreSQL cada sessão participa de uma transação externa revertida no
teardown, mesmo que os repositories chamem ``commit()``.
"""
import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "False")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-with-at-least-32-bytes")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.settings import settings
from app.database.session import Base, get_db
from app.main import app


def _database_teste_url_e_nome() -> tuple[str, str | None]:
    if settings.TEST_DATABASE_URL:
        url = settings.TEST_DATABASE_URL
        nome = make_url(url).database if make_url(url).get_backend_name() == "postgresql" else None
        return url, nome

    # O banco em memória torna a suíte executável em qualquer máquina,
    # inclusive sem Docker. Para validar especificamente contra PostgreSQL,
    # basta definir TEST_DATABASE_URL.
    return "sqlite+pysqlite:///:memory:", None


def _garantir_banco_de_teste_existe(nome_banco: str) -> None:
    """Cria o banco de teste se ele ainda não existir.

    A conexão administrativa usa `settings.DATABASE_URL` SEM
    MODIFICAÇÃO (a mesma string que o resto da aplicação já usa com
    sucesso o tempo todo). CREATE DATABASE não precisa ser emitido a
    partir do banco "postgres" — pode ser emitido de qualquer banco
    existente no mesmo servidor, então conectamos no banco de
    desenvolvimento mesmo, evitando qualquer reconstrução de URL.
    """
    engine_admin = create_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")
    try:
        with engine_admin.connect() as conn:
            existe = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :nome"), {"nome": nome_banco}
            ).scalar()
            if not existe:
                conn.execute(text(f'CREATE DATABASE "{nome_banco}"'))
    finally:
        engine_admin.dispose()


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    """Cria o banco somente quando um teste de integração o solicita."""
    test_database_url, nome_banco_teste = _database_teste_url_e_nome()
    url = make_url(test_database_url)

    if url.get_backend_name() == "postgresql":
        assert nome_banco_teste is not None
        _garantir_banco_de_teste_existe(nome_banco_teste)
        engine = create_engine(test_database_url, pool_pre_ping=True)
    else:
        engine = create_engine(
            test_database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    if test_engine.dialect.name == "sqlite":
        TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
            # O driver sqlite3 do Python tem particularidades com SAVEPOINTs.
            # Limpar as tabelas é determinístico e impede vazamento de estado
            # entre testes sem enfraquecer o isolamento usado no PostgreSQL.
            with test_engine.begin() as connection:
                for table in reversed(Base.metadata.sorted_tables):
                    connection.execute(table.delete())
        return

    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        # Apoio exclusivo dos helpers: papéis privilegiados são semeados
        # diretamente no banco, nunca pelo endpoint público de registro.
        test_client._sentry_test_db = db_session
        yield test_client
    app.dependency_overrides.clear()
