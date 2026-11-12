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


# Parte 3: listar, editar y borrar
def dejar_resenas(client, clinica_id: int, encabezados, calificaciones: list[int]) -> list[dict]:
    creadas = []
    for numero, calificacion in enumerate(calificaciones):
        cabeceras = encabezados(email=f"dueno{numero}@mail.com", nombre=f"Persona {numero}")
        respuesta = client.post(
            url_resenas(clinica_id), json={"calificacion": calificacion}, headers=cabeceras
        )
        creadas.append({**respuesta.json()["data"], "cabeceras": cabeceras})
    return creadas


def test_listar_resenas_recientes_con_resumen(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    dejar_resenas(client, clinica["id"], encabezados, [5, 3, 5])

    respuesta = client.get(url_resenas(clinica["id"])).json()

    assert [r["calificacion"] for r in respuesta["data"]] == [5, 3, 5]
    assert respuesta["data"][0]["esMia"] is None
    assert respuesta["meta"]["total"] == 3
    assert respuesta["meta"]["resumen"] == {
        "promedio": 4.3,
        "total": 3,
        "distribucion": {"5": 2, "4": 0, "3": 1, "2": 0, "1": 0},
    }


def test_listar_por_mejores_y_peores(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    dejar_resenas(client, clinica["id"], encabezados, [3, 5, 1])
    url = url_resenas(clinica["id"])

    mejores = client.get(url, params={"orden": "mejores"}).json()["data"]
    peores = client.get(url, params={"orden": "peores"}).json()["data"]

    assert [r["calificacion"] for r in mejores] == [5, 3, 1]
    assert [r["calificacion"] for r in peores] == [1, 3, 5]


def test_orden_invalido_da_400(client, crear_clinica):
    clinica, _ = crear_clinica()

    respuesta = client.get(url_resenas(clinica["id"]), params={"orden": "chistosas"})

    assert respuesta.status_code == 400


def test_clinica_sin_resenas(client, crear_clinica):
    clinica, _ = crear_clinica()

    respuesta = client.get(url_resenas(clinica["id"])).json()

    assert respuesta["data"] == []
    assert respuesta["meta"]["resumen"]["promedio"] is None
    assert respuesta["meta"]["resumen"]["total"] == 0


def test_editar_mi_resena_recalcula(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    resena = dejar_resenas(client, clinica["id"], encabezados, [5])[0]

    respuesta = client.put(
        f"/api/v1/resenas/{resena['id']}",
        json={"calificacion": 2, "comentario": "Cambié de opinión"},
        headers=resena["cabeceras"],
    )

    data = respuesta.json()["data"]
    assert data["calificacion"] == 2
    assert data["editadoEn"] is not None
    detalle = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]
    assert detalle["calificacion"] == 2.0


def test_borrar_mi_resena_recalcula(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    primera, segunda = dejar_resenas(client, clinica["id"], encabezados, [5, 1])

    respuesta = client.delete(f"/api/v1/resenas/{segunda['id']}", headers=segunda["cabeceras"])

    assert respuesta.status_code == 204
    detalle = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]
    assert detalle["calificacion"] == 5.0
    assert detalle["totalResenas"] == 1


def test_no_puedo_editar_ni_borrar_resenas_ajenas(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    resena = dejar_resenas(client, clinica["id"], encabezados, [5])[0]
    intruso = encabezados(email="intruso@mail.com")
    url = f"/api/v1/resenas/{resena['id']}"

    editar = client.put(url, json={"calificacion": 1}, headers=intruso)
    borrar = client.delete(url, headers=intruso)

    assert editar.status_code == 403
    assert borrar.status_code == 403


def test_resena_inexistente(client, encabezados):
    respuesta = client.delete("/api/v1/resenas/999", headers=encabezados())

    assert respuesta.status_code == 404


# Parte 4: moderación y cuentas borradas
def test_admin_borra_una_resena_ofensiva(client, crear_clinica, encabezados, encabezados_admin):
    clinica, _ = crear_clinica()
    buena, ofensiva = dejar_resenas(client, clinica["id"], encabezados, [5, 1])

    respuesta = client.delete(
        f"/api/v1/admin/resenas/{ofensiva['id']}", headers=encabezados_admin()
    )

    assert respuesta.status_code == 204
    detalle = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]
    assert detalle["calificacion"] == 5.0
    assert detalle["totalResenas"] == 1


def test_solo_un_admin_modera(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    resena = dejar_resenas(client, clinica["id"], encabezados, [1])[0]

    respuesta = client.delete(f"/api/v1/admin/resenas/{resena['id']}", headers=resena["cabeceras"])

    assert respuesta.status_code == 403


def test_el_admin_no_puede_editar_resenas_ajenas(
    client, crear_clinica, encabezados, encabezados_admin
):
    clinica, _ = crear_clinica()
    resena = dejar_resenas(client, clinica["id"], encabezados, [1])[0]

    respuesta = client.put(
        f"/api/v1/resenas/{resena['id']}", json={"calificacion": 5}, headers=encabezados_admin()
    )

    assert respuesta.status_code == 403


def test_resena_de_cuenta_borrada_sale_como_usuario_eliminado(client, crear_clinica, encabezados):
    clinica, _ = crear_clinica()
    resena = dejar_resenas(client, clinica["id"], encabezados, [4])[0]

    client.delete("/api/v1/me", headers=resena["cabeceras"])

    listado = client.get(url_resenas(clinica["id"])).json()
    assert listado["data"][0]["autor"] == {"id": None, "nombre": "Usuario eliminado"}
    assert listado["meta"]["resumen"]["total"] == 1
