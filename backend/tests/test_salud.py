from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.database import engine, get_db
from app.main import app


class SesionQueFalla:
    def execute(self, *_):
        raise OperationalError("SELECT 1", {}, Exception("sin base"))


def test_salud_con_sqlite_real(client):
    respuesta = client.get("/api/v1/salud")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["data"]["baseDatos"] == "conectada"


def test_salud_cuando_falla_la_base(client):
    app.dependency_overrides[get_db] = lambda: SesionQueFalla()
    respuesta = client.get("/api/v1/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["baseDatos"] == "sin conexion"


def test_sqlite_tiene_llaves_foraneas_activas():
    with engine.connect() as conexion:
        assert conexion.execute(text("PRAGMA foreign_keys")).scalar() == 1
        assert conexion.execute(text("PRAGMA journal_mode")).scalar() == "wal"


def test_ruta_inexistente_usa_formato_de_error(client):
    respuesta = client.get("/api/v1/no-existe")

    assert respuesta.status_code == 404
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["error"]["codigo"] == "NO_ENCONTRADO"
