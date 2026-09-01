"""
Configurações centralizadas da aplicação.

Todas as variáveis de ambiente são lidas UMA ÚNICA VEZ aqui e validadas
por tipo através do Pydantic Settings. Nenhuma outra parte do sistema
deve chamar os.getenv() diretamente — sempre importar `settings` daqui.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    # --- Aplicação ---
    APP_NAME: str = "Sentry Maintenance API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = True

    # --- Banco de dados ---
    DATABASE_URL: str
    # Opcional: se não definido, os testes de integração usam SQLite
    # em memória. Informe uma URL para validá-los também no PostgreSQL.
    TEST_DATABASE_URL: str | None = None

    # --- Segurança / JWT ---
    SECRET_KEY: str
    ALGORITHM: Literal["HS256"] = "HS256"
    JWT_ISSUER: str = "sentry-maintenance-api"
    JWT_AUDIENCE: str = "sentry-maintenance-clients"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, le=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0, le=90)

    # --- CORS ---
    CORS_ORIGINS: str = "*"
    ALLOWED_HOSTS: str = "*"

    # --- Upload de arquivos ---
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, gt=0, le=100)

    # --- Proteção contra abuso ---
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REDIS_URL: str | None = None
    LOGIN_RATE_LIMIT: int = Field(default=10, gt=0)
    LOGIN_RATE_WINDOW_SECONDS: int = Field(default=900, gt=0)
    REGISTER_RATE_LIMIT: int = Field(default=5, gt=0)
    REGISTER_RATE_WINDOW_SECONDS: int = Field(default=3600, gt=0)
    REFRESH_RATE_LIMIT: int = Field(default=60, gt=0)
    REFRESH_RATE_WINDOW_SECONDS: int = Field(default=900, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_hosts(self) -> list[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.APP_ENV != "production":
            return self

        insecure_secrets = {"troque-esta-chave-em-producao", "change-me", "secret"}
        if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.lower() in insecure_secrets:
            raise ValueError("SECRET_KEY deve ter ao menos 32 caracteres aleatórios em produção.")
        if self.DEBUG:
            raise ValueError("DEBUG deve ser False em produção.")
        if not self.cors_origins or "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS deve listar origens explícitas em produção.")
        if not self.allowed_hosts or "*" in self.allowed_hosts:
            raise ValueError("ALLOWED_HOSTS deve listar hosts explícitos em produção.")
        if self.RATE_LIMIT_ENABLED and not self.RATE_LIMIT_REDIS_URL:
            raise ValueError(
                "RATE_LIMIT_REDIS_URL é obrigatório em produção quando o rate limiting está ativo."
            )
        try:
            database_password = make_url(self.DATABASE_URL).password
        except Exception as exc:
            raise ValueError("DATABASE_URL inválida.") from exc
        if not database_password or database_password.lower() in {
            "sentry",
            "password",
            "postgres",
            "change-me",
        }:
            raise ValueError("DATABASE_URL deve usar uma senha forte em produção.")
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Cache das configurações (lru_cache garante que o .env só é lido
    uma vez durante o ciclo de vida da aplicação).
    """
    return Settings()


settings = get_settings()
