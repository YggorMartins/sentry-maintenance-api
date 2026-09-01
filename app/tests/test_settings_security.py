import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def _production_settings(**overrides):
    values = {
        "APP_ENV": "production",
        "DEBUG": False,
        "DATABASE_URL": "postgresql+psycopg2://sentry:uma-senha-forte-aleatoria@db/app",
        "SECRET_KEY": "uma-chave-aleatoria-com-mais-de-trinta-e-dois-bytes",
        "CORS_ORIGINS": "https://app.example.com",
        "ALLOWED_HOSTS": "api.example.com",
        "RATE_LIMIT_ENABLED": True,
        "RATE_LIMIT_REDIS_URL": "redis://redis:6379/0",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_configuracao_segura_de_producao_e_aceita():
    settings = _production_settings()

    assert settings.APP_ENV == "production"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("DEBUG", True),
        ("SECRET_KEY", "secret"),
        ("CORS_ORIGINS", "*"),
        ("ALLOWED_HOSTS", "*"),
        ("RATE_LIMIT_REDIS_URL", None),
        ("DATABASE_URL", "postgresql+psycopg2://sentry:sentry@db/app"),
    ],
)
def test_configuracao_insegura_de_producao_e_rejeitada(field, value):
    with pytest.raises(ValidationError):
        _production_settings(**{field: value})
