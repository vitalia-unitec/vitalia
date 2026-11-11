import pytest
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.modules.resenas.models import Resena


# Parte 1: la tabla y sus reglas
def test_la_base_rechaza_calificacion_fuera_de_rango(crear_clinica, registrar):
    clinica, _ = crear_clinica()
    autor_id = registrar()["usuario"]["id"]

    with SessionLocal() as db:
        db.add(Resena(clinica_id=clinica["id"], autor_id=autor_id, calificacion=6))
        with pytest.raises(IntegrityError):
            db.commit()


def test_la_base_rechaza_dos_resenas_del_mismo_usuario(crear_clinica, registrar):
    clinica, _ = crear_clinica()
    autor_id = registrar()["usuario"]["id"]

    with SessionLocal() as db:
        db.add(Resena(clinica_id=clinica["id"], autor_id=autor_id, calificacion=5))
        db.commit()
        db.add(Resena(clinica_id=clinica["id"], autor_id=autor_id, calificacion=4))
        with pytest.raises(IntegrityError):
            db.commit()


def test_al_borrar_la_cuenta_la_resena_se_queda_sin_autor(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    cabeceras = encabezados()
    autor_id = client.get("/api/v1/auth/me", headers=cabeceras).json()["data"]["id"]
    with SessionLocal() as db:
        db.add(Resena(clinica_id=clinica["id"], autor_id=autor_id, calificacion=5))
        db.commit()

    client.delete("/api/v1/me", headers=cabeceras)

    with SessionLocal() as db:
        resena = db.query(Resena).one()
        assert resena.autor_id is None
