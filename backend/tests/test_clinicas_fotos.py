from app.core.config import get_settings

URL = "/api/v1/clinicas"
URL_NEGOCIO = "/api/v1/negocio/clinicas"
BASE_FOTOS = "http://testserver/fotos/"

JPG = b"\xff\xd8\xff\xe0" + b"0" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 200


def subir(client, clinica_id, cabeceras, contenido=JPG, nombre="foto.jpg", campo="foto"):
    return client.post(
        f"{URL_NEGOCIO}/{clinica_id}/fotos",
        files={campo: (nombre, contenido, "image/jpeg")},
        headers=cabeceras,
    )


def archivo_de(url: str):
    return get_settings().fotos_ruta_absoluta / url.removeprefix(BASE_FOTOS)


def test_subir_foto(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    respuesta = subir(client, clinica["id"], cabeceras)

    assert respuesta.status_code == 201, respuesta.text
    foto = respuesta.json()["data"]
    assert set(foto) == {"id", "url", "orden"}
    assert foto["orden"] == 1
    assert foto["url"].startswith(BASE_FOTOS + "clinicas/")
    assert foto["url"].endswith(".jpg")
    assert archivo_de(foto["url"]).read_bytes() == JPG


def test_la_foto_subida_se_puede_descargar(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    foto = subir(client, clinica["id"], cabeceras, PNG, "local.png").json()["data"]

    respuesta = client.get(foto["url"])

    assert respuesta.status_code == 200
    assert respuesta.content == PNG


def test_la_primera_foto_es_la_principal(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    assert client.get(f"{URL}/{clinica['id']}").json()["data"]["fotoPrincipal"] is None

    primera = subir(client, clinica["id"], cabeceras).json()["data"]
    subir(client, clinica["id"], cabeceras, PNG)

    detalle = client.get(f"{URL}/{clinica['id']}").json()["data"]
    resumen = client.get(URL).json()["data"][0]
    assert detalle["fotoPrincipal"] == primera["url"]
    assert resumen["fotoPrincipal"] == primera["url"]
    assert [f["orden"] for f in detalle["fotos"]] == [1, 2]


def test_el_detalle_trae_cinco_fotos_y_la_galeria_todas(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    for _ in range(7):
        assert subir(client, clinica["id"], cabeceras).status_code == 201

    detalle = client.get(f"{URL}/{clinica['id']}").json()["data"]
    galeria = client.get(f"{URL}/{clinica['id']}/fotos").json()["data"]

    assert len(detalle["fotos"]) == 5
    assert [f["orden"] for f in galeria] == [1, 2, 3, 4, 5, 6, 7]


def test_maximo_diez_fotos(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    for _ in range(10):
        assert subir(client, clinica["id"], cabeceras).status_code == 201

    respuesta = subir(client, clinica["id"], cabeceras)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CONFLICTO"
    assert len(client.get(f"{URL}/{clinica['id']}/fotos").json()["data"]) == 10


def test_rechaza_archivos_que_no_son_fotos(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    respuesta = subir(client, clinica["id"], cabeceras, b"<script>alert(1)</script>", "foto.jpg")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "ARCHIVO_INVALIDO"
    assert client.get(f"{URL}/{clinica['id']}/fotos").json()["data"] == []


def test_sin_el_campo_foto_da_400(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    respuesta = subir(client, clinica["id"], cabeceras, campo="archivo")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_reordenar_cambia_la_principal(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    a, b, c = (subir(client, clinica["id"], cabeceras).json()["data"] for _ in range(3))

    respuesta = client.put(
        f"{URL_NEGOCIO}/{clinica['id']}/fotos/orden",
        json={"ids": [c["id"], a["id"], b["id"]]},
        headers=cabeceras,
    )

    assert respuesta.status_code == 200, respuesta.text
    assert [f["id"] for f in respuesta.json()["data"]] == [c["id"], a["id"], b["id"]]
    assert [f["orden"] for f in respuesta.json()["data"]] == [1, 2, 3]
    assert client.get(f"{URL}/{clinica['id']}").json()["data"]["fotoPrincipal"] == c["url"]


def test_reordenar_exige_todas_las_fotos_una_vez(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    a, b = (subir(client, clinica["id"], cabeceras).json()["data"] for _ in range(2))
    url = f"{URL_NEGOCIO}/{clinica['id']}/fotos/orden"

    for ids in ([a["id"]], [a["id"], a["id"]], [a["id"], b["id"], 999], []):
        respuesta = client.put(url, json={"ids": ids}, headers=cabeceras)
        assert respuesta.status_code == 400, ids
        assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_borrar_foto_quita_el_archivo_y_renumera(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    a, b, c = (subir(client, clinica["id"], cabeceras).json()["data"] for _ in range(3))

    respuesta = client.delete(f"{URL_NEGOCIO}/{clinica['id']}/fotos/{a['id']}", headers=cabeceras)

    assert respuesta.status_code == 204
    assert not archivo_de(a["url"]).exists()
    assert archivo_de(b["url"]).exists()
    galeria = client.get(f"{URL}/{clinica['id']}/fotos").json()["data"]
    assert [(f["id"], f["orden"]) for f in galeria] == [(b["id"], 1), (c["id"], 2)]


def test_borrar_foto_que_no_existe_da_404(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    respuesta = client.delete(f"{URL_NEGOCIO}/{clinica['id']}/fotos/999", headers=cabeceras)

    assert respuesta.status_code == 404


def test_solo_la_clinica_duena_administra_sus_fotos(
    client, crear_clinica, encabezados_clinica, encabezados
):
    clinica, cabeceras = crear_clinica()
    foto = subir(client, clinica["id"], cabeceras).json()["data"]
    otra_clinica = encabezados_clinica("otra@mail.com")
    dueno = encabezados(email="dueno@mail.com")
    borrar = f"{URL_NEGOCIO}/{clinica['id']}/fotos/{foto['id']}"

    assert subir(client, clinica["id"], otra_clinica).status_code == 403
    assert subir(client, clinica["id"], dueno).status_code == 403
    assert subir(client, clinica["id"], {}).status_code == 401
    assert client.delete(borrar, headers=otra_clinica).status_code == 403
    assert len(client.get(f"{URL}/{clinica['id']}/fotos").json()["data"]) == 1


def test_no_se_borra_la_foto_de_otra_clinica_por_su_id(client, crear_clinica, encabezados_clinica):
    mia, cabeceras = crear_clinica()
    ajena, cabeceras_ajena = crear_clinica(encabezados_clinica("ajena@mail.com"), nombre="Ajena")
    foto_ajena = subir(client, ajena["id"], cabeceras_ajena).json()["data"]

    respuesta = client.delete(
        f"{URL_NEGOCIO}/{mia['id']}/fotos/{foto_ajena['id']}", headers=cabeceras
    )

    assert respuesta.status_code == 404
    assert archivo_de(foto_ajena["url"]).exists()


def test_la_galeria_de_una_clinica_dada_de_baja_no_es_publica(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    subir(client, clinica["id"], cabeceras)
    client.delete(f"{URL_NEGOCIO}/{clinica['id']}", headers=cabeceras)

    assert client.get(f"{URL}/{clinica['id']}/fotos").status_code == 404
