from app.core.config import get_settings

URL = "/api/v1/me/mascotas"
BASE_FOTOS = "http://testserver/fotos/"

JPG = b"\xff\xd8\xff\xe0" + b"0" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 200
LUNA = {"nombre": "Luna", "especie": "perro", "sexo": "hembra"}


def crear_mascota(client, cabeceras) -> dict:
    respuesta = client.post(URL, json=LUNA, headers=cabeceras)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["data"]


def subir(client, mascota_id, cabeceras, contenido=JPG):
    return client.post(
        f"{URL}/{mascota_id}/foto",
        files={"foto": ("luna.jpg", contenido, "image/jpeg")},
        headers=cabeceras,
    )


def archivo_de(url: str):
    return get_settings().fotos_ruta_absoluta / url.removeprefix(BASE_FOTOS)


def test_subir_foto_de_mi_mascota(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)

    respuesta = subir(client, mascota["id"], cabeceras)

    assert respuesta.status_code == 200, respuesta.text
    data = respuesta.json()["data"]
    assert data["nombre"] == "Luna"
    assert data["fotoUrl"].startswith(BASE_FOTOS + "mascotas/")
    assert data["fotoUrl"].endswith(".jpg")
    assert archivo_de(data["fotoUrl"]).read_bytes() == JPG
    assert client.get(f"{URL}/{mascota['id']}", headers=cabeceras).json()["data"] == data


def test_cambiar_la_foto_borra_la_anterior(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)
    primera = subir(client, mascota["id"], cabeceras).json()["data"]["fotoUrl"]

    segunda = subir(client, mascota["id"], cabeceras, PNG).json()["data"]["fotoUrl"]

    assert segunda.endswith(".png")
    assert not archivo_de(primera).exists()
    assert archivo_de(segunda).read_bytes() == PNG


def test_editar_el_carnet_conserva_la_foto(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)
    foto = subir(client, mascota["id"], cabeceras).json()["data"]["fotoUrl"]

    editada = client.put(
        f"{URL}/{mascota['id']}", json={**LUNA, "nombre": "Lunita"}, headers=cabeceras
    )

    assert editada.json()["data"]["nombre"] == "Lunita"
    assert editada.json()["data"]["fotoUrl"] == foto


def test_un_archivo_que_no_es_foto_no_cambia_la_actual(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)
    foto = subir(client, mascota["id"], cabeceras).json()["data"]["fotoUrl"]

    respuesta = subir(client, mascota["id"], cabeceras, b"%PDF-1.7 no soy una foto")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "ARCHIVO_INVALIDO"
    assert client.get(f"{URL}/{mascota['id']}", headers=cabeceras).json()["data"]["fotoUrl"] == foto
    assert archivo_de(foto).exists()


def test_la_mascota_de_otro_usuario_da_404(client, encabezados):
    mascota = crear_mascota(client, encabezados())
    otro = encabezados(email="otro@mail.com")

    assert subir(client, mascota["id"], otro).status_code == 404
    assert subir(client, mascota["id"], {}).status_code == 401


def test_borrar_la_mascota_borra_su_foto(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)
    foto = subir(client, mascota["id"], cabeceras).json()["data"]["fotoUrl"]

    assert client.delete(f"{URL}/{mascota['id']}", headers=cabeceras).status_code == 204

    assert not archivo_de(foto).exists()


def test_borrar_la_cuenta_borra_las_fotos_de_sus_mascotas(client, encabezados):
    cabeceras = encabezados()
    mascota = crear_mascota(client, cabeceras)
    foto = subir(client, mascota["id"], cabeceras).json()["data"]["fotoUrl"]

    assert client.delete("/api/v1/me", headers=cabeceras).status_code == 204

    assert not archivo_de(foto).exists()
