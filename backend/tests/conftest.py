import os
import tempfile
from pathlib import Path

os.environ["DB_RUTA"] = str(Path(tempfile.mkdtemp()) / "vitalia_test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.modelos import crear_tablas  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.auth.limitador import limitador_login  # noqa: E402
from app.modules.usuarios.models import Usuario  # noqa: E402

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
    crear_tablas()
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


DATOS_CLINICA = {
    "nombre": "Clínica Veterinaria Patitas",
    "descripcion": "Atención integral para perros y gatos",
    "tipos": ["veterinaria"],
    "direccion": {
        "calle": "Av. Insurgentes 123",
        "colonia": "Del Valle",
        "alcaldiaMunicipio": "Benito Juárez",
        "ciudad": "Ciudad de México",
        "estado": "CDMX",
        "codigoPostal": "03100",
    },
    "lat": 19.3801,
    "lng": -99.1702,
    "telefono": "5598765432",
    "whatsapp": "5215598765432",
    "sitioWeb": None,
    "urgencias24h": False,
}


@pytest.fixture
def encabezados_admin(encabezados):
    def _encabezados_admin(email: str = "admin@mail.com") -> dict:
        cabeceras = encabezados(email=email, nombre="Admin Vitalia")
        with SessionLocal() as db:
            admin = db.scalar(select(Usuario).where(Usuario.email == email))
            admin.rol = "admin"
            db.commit()
        return cabeceras

    return _encabezados_admin


@pytest.fixture
def encabezados_clinica(encabezados):
    def _encabezados_clinica(email: str = "vet@mail.com") -> dict:
        return encabezados(email=email, rol="clinica")

    return _encabezados_clinica


@pytest.fixture
def crear_clinica(client, encabezados_clinica):
    def _crear_clinica(cabeceras: dict | None = None, **cambios) -> tuple[dict, dict]:
        cabeceras = cabeceras or encabezados_clinica()
        datos = {**DATOS_CLINICA, **cambios}
        respuesta = client.post("/api/v1/negocio/clinicas", json=datos, headers=cabeceras)
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()["data"], cabeceras

    return _crear_clinica
