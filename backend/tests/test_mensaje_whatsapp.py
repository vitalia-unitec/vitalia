from urllib.parse import unquote

from app.modules.mascotas.mensaje import armar_texto, armar_url, describir_edad
from tests.test_mascotas import LUNA, URL


# La lógica pura, sin base de datos
def test_describir_edad():
    assert describir_edad(3, 0) == "3 años"
    assert describir_edad(1, None) == "1 año"
    assert describir_edad(0, 4) == "4 meses"
    assert describir_edad(1, 1) == "1 año y 1 mes"
    assert describir_edad(None, None) is None


def test_texto_completo():
    texto = armar_texto(
        "Clínica Patitas", "Luna", "perro", "hembra", "Golden Retriever", 3, 0, "Dorado"
    )

    assert texto == (
        "Hola, Clínica Patitas. Los encontré en Vitalia. "
        "Quiero información para mi mascota: Luna, perro hembra, Golden Retriever, "
        "3 años, color dorado."
    )


def test_texto_sin_datos_opcionales():
    texto = armar_texto("Clínica Patitas", "Michi", "gato", "macho")

    assert texto.endswith("mi mascota: Michi, gato macho.")


def test_url_agrega_lada_y_codifica_el_texto():
    url = armar_url("5598765432", "Hola, ¿qué tal?")

    assert url.startswith("https://wa.me/525598765432?text=")
    assert " " not in url
    assert unquote(url.split("text=")[1]) == "Hola, ¿qué tal?"


def test_url_respeta_numero_con_lada():
    assert armar_url("5215598765432", "Hola").startswith("https://wa.me/5215598765432?")


# La ruta completa
def test_mensaje_de_whatsapp(client, encabezados, crear_clinica):
    clinica, _ = crear_clinica()
    cabeceras = encabezados()
    mascota = client.post(URL, json=LUNA, headers=cabeceras).json()["data"]

    respuesta = client.get(
        f"{URL}/{mascota['id']}/mensaje-whatsapp",
        params={"clinicaId": clinica["id"]},
        headers=cabeceras,
    )

    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert "Clínica Veterinaria Patitas" in data["texto"]
    assert "Luna, perro hembra" in data["texto"]
    assert data["url"].startswith("https://wa.me/5215598765432?text=")
    assert unquote(data["url"].split("text=")[1]) == data["texto"]


def test_clinica_sin_whatsapp_da_400(client, encabezados, crear_clinica):
    clinica, _ = crear_clinica(whatsapp=None)
    cabeceras = encabezados()
    mascota = client.post(URL, json=LUNA, headers=cabeceras).json()["data"]

    respuesta = client.get(
        f"{URL}/{mascota['id']}/mensaje-whatsapp",
        params={"clinicaId": clinica["id"]},
        headers=cabeceras,
    )

    assert respuesta.status_code == 400


def test_falta_clinica_o_no_existe(client, encabezados):
    cabeceras = encabezados()
    mascota = client.post(URL, json=LUNA, headers=cabeceras).json()["data"]
    url = f"{URL}/{mascota['id']}/mensaje-whatsapp"

    assert client.get(url, headers=cabeceras).status_code == 400
    assert client.get(url, params={"clinicaId": 999}, headers=cabeceras).status_code == 404


def test_no_se_arma_mensaje_con_mascota_ajena(client, encabezados, crear_clinica):
    clinica, _ = crear_clinica()
    mascota = client.post(URL, json=LUNA, headers=encabezados()).json()["data"]
    intruso = encabezados(email="intruso@mail.com")

    respuesta = client.get(
        f"{URL}/{mascota['id']}/mensaje-whatsapp",
        params={"clinicaId": clinica["id"]},
        headers=intruso,
    )

    assert respuesta.status_code == 404
