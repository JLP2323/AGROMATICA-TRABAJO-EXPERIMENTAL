"""
config/settings.py
------------------
Centralización y validación de toda la configuración de la aplicación.
Lee variables de entorno desde el archivo .env usando python-dotenv.
Usa Pydantic BaseSettings para validación y tipado estricto.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Carga el archivo .env desde la raíz del proyecto (un nivel arriba de agromatica/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class DatabaseSettings(BaseSettings):
    """Configuración de conexión a PostgreSQL."""

    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5433, alias="DB_PORT")
    name: str = Field(default="agrobio_db", alias="DB_NAME")
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")
    pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    pool_max_overflow: int = Field(default=10, alias="DB_POOL_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=1800, alias="DB_POOL_RECYCLE")

    model_config = {"populate_by_name": True, "env_prefix": "DB_"}

    @property
    def dsn(self) -> str:
        """DSN completo para psycopg2."""
        return (
            f"host={self.host} port={self.port} dbname={self.name} "
            f"user={self.user} password={self.password}"
        )

    @property
    def sqlalchemy_url(self) -> str:
        """URL de conexión para SQLAlchemy."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class AppSettings(BaseSettings):
    """Configuración general de la aplicación."""

    env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="APP_DEBUG")
    cache_ttl: int = Field(default=600, alias="APP_CACHE_TTL")

    model_config = {"populate_by_name": True, "env_prefix": "APP_"}

    @field_validator("env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "production", "testing"}
        if v not in allowed:
            raise ValueError(f"APP_ENV debe ser uno de: {allowed}")
        return v


class Settings(BaseSettings):
    """Configuración raíz que agrupa todos los subsistemas."""

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    app: AppSettings = Field(default_factory=AppSettings)

    model_config = {"populate_by_name": True}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retorna la instancia singleton de configuración.
    Cacheada para evitar re-lectura del entorno en cada llamada.
    """
    return Settings()
