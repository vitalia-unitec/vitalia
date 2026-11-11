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


# Parte 2: crear reseñas
def url_resenas(clinica_id: int) -> str:
    return f"/api/v1/clinicas/{clinica_id}/resenas"


def test_crear_resena(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    datos = {"calificacion": 5, "comentario": "Atendieron rápido a mi perrita"}

    respuesta = client.post(url_resenas(clinica["id"]), json=datos, headers=encabezados())

    assert respuesta.status_code == 201
    resena = respuesta.json()["data"]
    assert resena["calificacion"] == 5
    assert resena["autor"]["nombre"] == "Rosa M."
    assert resena["esMia"] is True
    assert resena["editadoEn"] is None


def test_crear_resenas_recalcula_la_calificacion(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    client.post(url_resenas(clinica["id"]), json={"calificacion": 5}, headers=encabezados())
    otro = encabezados(email="luis@mail.com")
    client.post(url_resenas(clinica["id"]), json={"calificacion": 4}, headers=otro)

    detalle = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]

    assert detalle["calificacion"] == 4.5
    assert detalle["totalResenas"] == 2


def test_segunda_resena_del_mismo_usuario_da_conflicto(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    cabeceras = encabezados()
    client.post(url_resenas(clinica["id"]), json={"calificacion": 5}, headers=cabeceras)

    respuesta = client.post(url_resenas(clinica["id"]), json={"calificacion": 1}, headers=cabeceras)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CONFLICTO"


def test_comentario_vacio_se_guarda_como_nulo(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    datos = {"calificacion": 4, "comentario": "   "}

    respuesta = client.post(url_resenas(clinica["id"]), json=datos, headers=encabezados())

    assert respuesta.json()["data"]["comentario"] is None


def test_calificacion_fuera_de_rango_da_400(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()

    for calificacion in (0, 6):
        datos = {"calificacion": calificacion}
        respuesta = client.post(
            url_resenas(clinica["id"]),
            json=datos,
            headers=encabezados(email=f"u{calificacion}@mail.com"),
        )
        assert respuesta.status_code == 400


def test_solo_un_dueno_puede_resenar(client, crear_clinica, encabezados_clinica):
    clinica, _ = crear_clinica()
    otra_clinica = encabezados_clinica("otra@mail.com")

    con_clinica = client.post(
        url_resenas(clinica["id"]), json={"calificacion": 5}, headers=otra_clinica
    )
    sin_sesion = client.post(url_resenas(clinica["id"]), json={"calificacion": 5})

    assert con_clinica.status_code == 403
    assert sin_sesion.status_code == 401


def test_no_se_resena_una_clinica_inexistente_o_dada_de_baja(client, crear_clinica, encabezados):
    clinica, cabeceras_clinica = crear_clinica()
    client.delete(f"/api/v1/negocio/clinicas/{clinica['id']}", headers=cabeceras_clinica)
    cabeceras = encabezados()

    de_baja = client.post(url_resenas(clinica["id"]), json={"calificacion": 5}, headers=cabeceras)
    inexistente = client.post(url_resenas(999), json={"calificacion": 5}, headers=cabeceras)

    assert de_baja.status_code == 404
    assert inexistente.status_code == 404
