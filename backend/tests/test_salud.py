from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app


class SesionFalsa:
    def __init__(self, falla: bool = False):
        self.falla = falla

    def execute(self, *_):
        if self.falla:
            raise OperationalError("SELECT 1", {}, Exception("sin servidor"))
        return None


def test_salud_con_bd_conectada(client):
    app.dependency_overrides[get_db] = lambda: SesionFalsa()
    respuesta = client.get("/api/v1/salud")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["data"]["baseDatos"] == "conectada"


def test_salud_sin_bd(client):
    app.dependency_overrides[get_db] = lambda: SesionFalsa(falla=True)
    respuesta = client.get("/api/v1/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["baseDatos"] == "sin conexion"


def test_ruta_inexistente_usa_formato_de_error(client):
    respuesta = client.get("/api/v1/no-existe")

    assert respuesta.status_code == 404
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["error"]["codigo"] == "NO_ENCONTRADO"
