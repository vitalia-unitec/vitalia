from app.core.database import SessionLocal
from app.modules.mascotas.models import Mascota

URL = "/api/v1/me/mascotas"

LUNA = {
    "nombre": "Luna",
    "especie": "perro",
    "raza": "Golden Retriever",
    "sexo": "hembra",
    "edadAnios": 3,
    "edadMeses": 0,
    "color": "Dorado",
}


def test_crear_y_listar_mis_mascotas(client, encabezados):
    cabeceras = encabezados()

    creada = client.post(URL, json=LUNA, headers=cabeceras)

    assert creada.status_code == 201
    mascota = creada.json()["data"]
    assert mascota["nombre"] == "Luna"
    assert mascota["edadAnios"] == 3
    assert mascota["fotoUrl"] is None
    lista = client.get(URL, headers=cabeceras).json()["data"]
    assert [m["nombre"] for m in lista] == ["Luna"]


def test_solo_nombre_especie_y_sexo_son_obligatorios(client, encabezados):
    minima = {"nombre": "Michi", "especie": "gato", "sexo": "macho"}

    respuesta = client.post(URL, json=minima, headers=encabezados())

    assert respuesta.status_code == 201
    assert respuesta.json()["data"]["raza"] is None


def test_valores_invalidos_dan_400(client, encabezados):
    cabeceras = encabezados()
    invalidos = [
        {**LUNA, "especie": "dragon"},
        {**LUNA, "sexo": "otro"},
        {**LUNA, "edadMeses": 12},
        {**LUNA, "edadAnios": -1},
        {**LUNA, "nombre": ""},
    ]

    for datos in invalidos:
        assert client.post(URL, json=datos, headers=cabeceras).status_code == 400


def test_editar_mi_mascota(client, encabezados):
    cabeceras = encabezados()
    mascota = client.post(URL, json=LUNA, headers=cabeceras).json()["data"]

    respuesta = client.put(
        f"{URL}/{mascota['id']}", json={**LUNA, "edadAnios": 4}, headers=cabeceras
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["edadAnios"] == 4


def test_borrar_mi_mascota(client, encabezados):
    cabeceras = encabezados()
    mascota = client.post(URL, json=LUNA, headers=cabeceras).json()["data"]

    assert client.delete(f"{URL}/{mascota['id']}", headers=cabeceras).status_code == 204
    assert client.get(f"{URL}/{mascota['id']}", headers=cabeceras).status_code == 404


def test_mascota_ajena_responde_404(client, encabezados):
    mascota = client.post(URL, json=LUNA, headers=encabezados()).json()["data"]
    intruso = encabezados(email="intruso@mail.com")
    url = f"{URL}/{mascota['id']}"

    assert client.get(url, headers=intruso).status_code == 404
    assert client.put(url, json=LUNA, headers=intruso).status_code == 404
    assert client.delete(url, headers=intruso).status_code == 404


def test_maximo_diez_mascotas(client, encabezados):
    cabeceras = encabezados()
    for numero in range(10):
        client.post(URL, json={**LUNA, "nombre": f"Mascota {numero}"}, headers=cabeceras)

    respuesta = client.post(URL, json=LUNA, headers=cabeceras)

    assert respuesta.status_code == 409


def test_solo_duenos_tienen_mascotas(client, encabezados_clinica):
    assert client.get(URL, headers=encabezados_clinica()).status_code == 403
    assert client.get(URL).status_code == 401


def test_al_borrar_la_cuenta_se_borran_sus_mascotas(client, encabezados):
    cabeceras = encabezados()
    client.post(URL, json=LUNA, headers=cabeceras)

    client.delete("/api/v1/me", headers=cabeceras)

    with SessionLocal() as db:
        assert db.query(Mascota).count() == 0
