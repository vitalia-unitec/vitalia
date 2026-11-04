from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Aplicación
    app_nombre: str = "Vitalia API"
    app_entorno: str = "local"
    app_debug: bool = True
    app_zona_horaria: str = "America/Mexico_City"

    # Base de datos
    db_host: str = "localhost"
    db_port: int = 3307
    db_user: str = "vitalia"
    db_password: str = "vitalia123"
    db_name: str = "vitalia"

    # CORS
    cors_origenes: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
