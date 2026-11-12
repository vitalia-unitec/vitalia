import secrets
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SECRETO_DE_EJEMPLO = "cambia-esto-por-un-secreto-largo-de-32-caracteres-o-mas"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Aplicación
    app_nombre: str = "Vitalia API"
    app_entorno: str = "produccion"
    app_debug: bool = False
    app_zona_horaria: str = "America/Mexico_City"

    # Base de datos
    db_ruta: str = "data/vitalia.db"

    # Autenticación
    jwt_secret: str = ""
    jwt_expira_horas: int = 8
    jwt_algoritmo: str = "HS256"

    # Fotos
    fotos_ruta: str = "data/fotos"
    fotos_url_base: str = "http://localhost:8000/fotos"

    # CORS
    cors_origenes: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def db_ruta_absoluta(self) -> Path:
        return Path(self.db_ruta).expanduser().resolve()

    @property
    def fotos_ruta_absoluta(self) -> Path:
        return Path(self.fotos_ruta).expanduser().resolve()

        # Fuera de local el secreto es obligatorio; en local se genera uno si falta

    @model_validator(mode="after")
    def revisar_secreto(self) -> "Settings":
        if self.app_entorno == "local":
            if not self.jwt_secret:
                self.jwt_secret = secrets.token_urlsafe(48)
            return self
        if self.jwt_secret == SECRETO_DE_EJEMPLO or len(self.jwt_secret) < 32:
            raise ValueError(
                "JWT_SECRET debe ser propio y tener 32 caracteres o más. "
                "Para desarrollo copia .env.example a .env, que usa APP_ENTORNO=local"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
