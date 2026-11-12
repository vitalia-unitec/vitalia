from tests.conftest import DATOS_CLINICA

URL = "/api/v1/admin/clinicas"
URL_PUBLICA = "/api/v1/clinicas"
URL_NEGOCIO = "/api/v1/negocio/clinicas"


def nombres(client, admin, **params) -> list[str]:
    respuesta = client.get(URL, params=params, headers=admin)
    assert respuesta.status_code == 200, respuesta.text
    return [c["nombre"] for c in respuesta.json()["data"]]


def test_el_admin_lista_todas_las_clinicas(client, crear_clinica, encabezados_admin):
    _, cabeceras = crear_clinica()
    baja, _ = crear_clinica(cabeceras, nombre="Dada de baja")
    client.delete(f"{URL_NEGOCIO}/{baja['id']}", headers=cabeceras)

    respuesta = client.get(URL, headers=encabezados_admin())

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert [c["nombre"] for c in cuerpo["data"]] == ["Dada de baja", "Clínica Veterinaria Patitas"]
    assert [c["activa"] for c in cuerpo["data"]] == [False, True]
    assert cuerpo["data"][0]["verificada"] is False
    assert cuerpo["meta"] == {"pagina": 1, "porPagina": 10, "total": 2, "totalPaginas": 1}


def test_filtros_del_listado(client, crear_clinica, encabezados_admin):
    patitas, cabeceras = crear_clinica()
    baja, _ = crear_clinica(cabeceras, nombre="Hospital Sur")
    client.delete(f"{URL_NEGOCIO}/{baja['id']}", headers=cabeceras)
    admin = encabezados_admin()
    client.patch(f"{URL}/{patitas['id']}/verificacion", json={"verificada": True}, headers=admin)

    assert nombres(client, admin, verificada="true") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, admin, verificada="false") == ["Hospital Sur"]
    assert nombres(client, admin, activa="false") == ["Hospital Sur"]
    assert nombres(client, admin, q="clinica") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, admin, verificada="true", activa="false") == []


def test_el_listado_pagina(client, crear_clinica, encabezados_admin):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Segunda")
    crear_clinica(cabeceras, nombre="Tercera")

    cuerpo = client.get(URL, params={"porPagina": 2}, headers=encabezados_admin()).json()

    assert [c["nombre"] for c in cuerpo["data"]] == ["Tercera", "Segunda"]
    assert cuerpo["meta"]["total"] == 3
    assert cuerpo["meta"]["totalPaginas"] == 2


def test_verificar_y_quitar_la_verificacion(client, crear_clinica, encabezados_admin):
    clinica, _ = crear_clinica()
    admin = encabezados_admin()
    url = f"{URL}/{clinica['id']}/verificacion"

    marcada = client.patch(url, json={"verificada": True}, headers=admin)

    assert marcada.status_code == 200, marcada.text
    assert marcada.json()["data"]["verificada"] is True
    assert client.get(f"{URL_PUBLICA}/{clinica['id']}").json()["data"]["verificada"] is True
    assert client.get(URL_PUBLICA).json()["data"][0]["verificada"] is True

    quitada = client.patch(url, json={"verificada": False}, headers=admin)
    assert quitada.json()["data"]["verificada"] is False


def test_suspender_saca_la_clinica_de_lo_publico(client, crear_clinica, encabezados_admin):
    clinica, _ = crear_clinica()
    admin = encabezados_admin()
    url = f"{URL}/{clinica['id']}/estado"

    suspendida = client.patch(url, json={"activa": False}, headers=admin)

    assert suspendida.status_code == 200, suspendida.text
    assert suspendida.json()["data"]["activa"] is False
    assert client.get(f"{URL_PUBLICA}/{clinica['id']}").status_code == 404
    assert client.get(URL_PUBLICA).json()["data"] == []

    reactivada = client.patch(url, json={"activa": True}, headers=admin)
    assert reactivada.json()["data"]["activa"] is True
    assert client.get(f"{URL_PUBLICA}/{clinica['id']}").status_code == 200


def test_el_admin_puede_reactivar_una_baja(client, crear_clinica, encabezados_admin):
    clinica, cabeceras = crear_clinica()
    client.delete(f"{URL_NEGOCIO}/{clinica['id']}", headers=cabeceras)

    respuesta = client.patch(
        f"{URL}/{clinica['id']}/estado", json={"activa": True}, headers=encabezados_admin()
    )

    assert respuesta.status_code == 200
    assert client.get(f"{URL_PUBLICA}/{clinica['id']}").status_code == 200


def test_solo_el_admin_entra(client, crear_clinica, encabezados):
    clinica, clinica_duena = crear_clinica()
    dueno = encabezados(email="dueno@mail.com")
    verificar = f"{URL}/{clinica['id']}/verificacion"
    estado = f"{URL}/{clinica['id']}/estado"

    for cabeceras, esperado in ((clinica_duena, 403), (dueno, 403), ({}, 401)):
        assert client.get(URL, headers=cabeceras).status_code == esperado
        respuesta = client.patch(verificar, json={"verificada": True}, headers=cabeceras)
        assert respuesta.status_code == esperado
        respuesta = client.patch(estado, json={"activa": False}, headers=cabeceras)
        assert respuesta.status_code == esperado

    detalle = client.get(f"{URL_PUBLICA}/{clinica['id']}").json()["data"]
    assert detalle["verificada"] is False


def test_una_clinica_no_puede_verificarse_sola(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    editada = client.put(
        f"{URL_NEGOCIO}/{clinica['id']}",
        json={**DATOS_CLINICA, "verificada": True},
        headers=cabeceras,
    )

    assert editada.status_code == 200, editada.text
    assert editada.json()["data"]["verificada"] is False


def test_validaciones_y_clinica_inexistente(client, crear_clinica, encabezados_admin):
    clinica, _ = crear_clinica()
    admin = encabezados_admin()
    url = f"{URL}/{clinica['id']}/verificacion"

    assert client.patch(url, json={}, headers=admin).status_code == 400
    assert client.patch(url, json={"verificada": "quizás"}, headers=admin).status_code == 400
    faltante = client.patch(f"{URL}/999/verificacion", json={"verificada": True}, headers=admin)
    assert faltante.status_code == 404
    assert (
        client.patch(f"{URL}/999/estado", json={"activa": True}, headers=admin).status_code == 404
    )
