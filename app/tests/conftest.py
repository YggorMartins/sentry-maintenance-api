"""
Fixtures de teste de integração.

DUAS camadas de isolamento:

1. Banco de dados DEDICADO para testes (não o banco de desenvolvimento).
   Motivo real, não teórico: numa rodada anterior, um teste que
   assumia "CPF ainda não cadastrado" falhou porque esse CPF já
   existia de verdade no banco de dev (criado manualmente via Swagger
   em uma sessão de teste manual anterior). Testes automatizados nunca
   devem depender do estado de um banco compartilhado com uso manual.

   O banco de teste é derivado de DATABASE_URL (sufixo "_test") usando
   MANIPULAÇÃO DE STRING (`rpartition`), não um objeto `URL` do
   SQLAlchemy reconstruído — de propósito: reconstruir a URL via
   parse -> set() -> str() exigiria re-serializar usuário/senha, o que
   se mostrou não confiável dependendo do ambiente. Cortando a string
   só depois do último "/", a parte com usuário/senha nunca é tocada.

2. Isolamento POR TESTE via transação + SAVEPOINT (padrão "join a
   Session into an external transaction" da documentação do
   SQLAlchemy): mesmo dentro do banco de teste, cada teste roda numa
   transação revertida ao final — mesmo que o código sob teste chame
   `session.commit()` internamente (nossos repositories sempre
   chamam). Isso garante que testes não interferem uns nos outros.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.database.session import Base, get_db
from app.main import app


def _database_teste_url_e_nome() -> tuple[str, str]:
    if settings.TEST_DATABASE_URL:
        url = settings.TEST_DATABASE_URL
        nome = url.rpartition("/")[2]
        return url, nome

    base, _, banco_atual = settings.DATABASE_URL.rpartition("/")
    nome = f"{banco_atual}_test"
    return f"{base}/{nome}", nome


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


_TEST_DATABASE_URL, _NOME_BANCO_TESTE = _database_teste_url_e_nome()
_garantir_banco_de_teste_existe(_NOME_BANCO_TESTE)
_test_engine = create_engine(_TEST_DATABASE_URL, pool_pre_ping=True)


@pytest.fixture(scope="session", autouse=True)
def _criar_tabelas():
    Base.metadata.create_all(bind=_test_engine)
    yield


@pytest.fixture()
def db_session():
    connection = _test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestingSessionLocal()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _reabrir_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
