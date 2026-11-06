import os
import tempfile
from pathlib import Path

os.environ["DB_RUTA"] = str(Path(tempfile.mkdtemp()) / "vitalia_test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.auth.limitador import limitador_login  # noqa: E402

DATOS_DUENO = {
    "nombre": "Rosa Martínez",
    "email": "rosa@mail.com",
    "password": "Perrito2026",
    "telefono": "5512345678",
    "rol": "dueno",
}


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    limitador_login.reiniciar()
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture
def registrar(client):
    def _registrar(**cambios) -> dict:
        datos = {**DATOS_DUENO, **cambios}
        respuesta = client.post("/api/v1/auth/registro", json=datos)
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()["data"]

    return _registrar


@pytest.fixture
def encabezados(registrar):
    def _encabezados(**cambios) -> dict:
        sesion = registrar(**cambios)
        return {"Authorization": f"Bearer {sesion['token']}"}

    return _encabezados
