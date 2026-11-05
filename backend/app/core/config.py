from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Aplicación
    app_nombre: str = "Vitalia API"
    app_entorno: str = "local"
    app_debug: bool = True
    app_zona_horaria: str = "America/Mexico_City"

    # Base de datos
    db_ruta: str = "data/vitalia.db"

    # CORS
    cors_origenes: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def db_ruta_absoluta(self) -> Path:
        return Path(self.db_ruta).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
