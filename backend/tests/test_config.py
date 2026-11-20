import pytest
from pydantic import ValidationError

from app.core.config import SECRETO_DE_EJEMPLO, Settings

SECRETO_BUENO = "un-secreto-propio-y-largo-para-las-pruebas-0123456789"


def crear(**valores) -> Settings:
    return Settings(_env_file=None, **valores)


def test_sin_configurar_nada_no_arranca(monkeypatch):
    monkeypatch.delenv("APP_ENTORNO", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError, match="JWT_SECRET"):
        crear()


@pytest.mark.parametrize(
    "secreto", ["", "corto", SECRETO_DE_EJEMPLO], ids=["vacio", "corto", "de-ejemplo"]
)
def test_fuera_de_local_rechaza_secretos_inseguros(secreto):
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        crear(app_entorno="produccion", jwt_secret=secreto)


def test_fuera_de_local_acepta_un_secreto_propio():
    settings = crear(app_entorno="produccion", jwt_secret=SECRETO_BUENO, app_debug=False)

    assert settings.jwt_secret == SECRETO_BUENO


def test_el_modo_debug_viene_apagado(monkeypatch):
    monkeypatch.delenv("APP_DEBUG", raising=False)

    assert crear(app_entorno="local").app_debug is False


def test_en_local_sin_secreto_genera_uno_al_azar(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)

    primero = crear(app_entorno="local")
    segundo = crear(app_entorno="local")

    assert len(primero.jwt_secret) >= 32
    assert primero.jwt_secret != segundo.jwt_secret
    assert primero.jwt_secret != SECRETO_DE_EJEMPLO


def test_en_local_respeta_el_secreto_configurado():
    settings = crear(app_entorno="local", jwt_secret=SECRETO_DE_EJEMPLO)

    assert settings.jwt_secret == SECRETO_DE_EJEMPLO
