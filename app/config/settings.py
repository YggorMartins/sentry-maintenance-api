"""
Configurações centralizadas da aplicação.

Todas as variáveis de ambiente são lidas UMA ÚNICA VEZ aqui e validadas
por tipo através do Pydantic Settings. Nenhuma outra parte do sistema
deve chamar os.getenv() diretamente — sempre importar `settings` daqui.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Aplicação ---
    APP_NAME: str = "Sentry Maintenance API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # --- Banco de dados ---
    DATABASE_URL: str
    # Opcional: se não definido, os testes derivam automaticamente um
    # banco "<DATABASE_URL>_test" a partir do banco de desenvolvimento
    # (ver app/tests/conftest.py).
    TEST_DATABASE_URL: str | None = None

    # --- Segurança / JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: str = "*"

    # --- Upload de arquivos ---
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cache das configurações (lru_cache garante que o .env só é lido
    uma vez durante o ciclo de vida da aplicação).
    """
    return Settings()


settings = get_settings()
