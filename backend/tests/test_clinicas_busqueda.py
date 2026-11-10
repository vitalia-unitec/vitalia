from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.database import SessionLocal
from app.core.geo import distancia_km, rectangulo
from app.modules.clinicas import service
from app.modules.clinicas.models import Clinica
from tests.conftest import DATOS_CLINICA

URL = "/api/v1/clinicas"
URL_NEGOCIO = "/api/v1/negocio/clinicas"

SIN_UBICACION = {"lat": None, "lng": None, "radioKm": None}

CAMPOS_RESUMEN = {
    "id",
    "nombre",
    "tipos",
    "calificacion",
    "totalResenas",
    "distanciaKm",
    "abierto",
    "cierraA",
    "abreA",
    "urgencias24h",
    "verificada",
    "fotoPrincipal",
    "serviciosDestacados",
    "lat",
    "lng",
}


def calificar(clinica_id: int, promedio: float, total: int) -> None:
    with SessionLocal() as db:
        clinica = db.get(Clinica, clinica_id)
        clinica.calificacion_prom = promedio
        clinica.total_resenas = total
        db.commit()


def test_busqueda_sin_clinicas(client):
    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["data"] == []
    assert cuerpo["meta"] == {
        "pagina": 1,
        "porPagina": 10,
        "total": 0,
        "totalPaginas": 0,
        "busqueda": SIN_UBICACION,
    }


def test_busqueda_regresa_resumen(client, crear_clinica):
    crear_clinica()

    data = client.get(URL).json()["data"]

    assert len(data) == 1
    assert set(data[0]) == CAMPOS_RESUMEN
    assert data[0]["nombre"] == "Clínica Veterinaria Patitas"
    assert data[0]["distanciaKm"] is None


def test_busqueda_solo_muestra_activas(client, crear_clinica):
    activa, cabeceras = crear_clinica()
    baja, _ = crear_clinica(cabeceras, nombre="Clínica dada de baja")
    client.delete(f"{URL_NEGOCIO}/{baja['id']}", headers=cabeceras)

    cuerpo = client.get(URL).json()

    assert [c["id"] for c in cuerpo["data"]] == [activa["id"]]
    assert cuerpo["meta"]["total"] == 1


def test_busqueda_pagina(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Segunda")
    crear_clinica(cabeceras, nombre="Tercera")

    primera = client.get(URL, params={"porPagina": 2}).json()
    segunda = client.get(URL, params={"porPagina": 2, "pagina": 2}).json()

    assert len(primera["data"]) == 2
    assert len(segunda["data"]) == 1
    assert primera["meta"]["total"] == 3
    assert primera["meta"]["totalPaginas"] == 2
    ids = [c["id"] for c in primera["data"] + segunda["data"]]
    assert len(set(ids)) == 3


def test_busqueda_ordena_por_calificacion(client, crear_clinica):
    sin_resenas, cabeceras = crear_clinica()
    buena, _ = crear_clinica(cabeceras, nombre="Buena")
    mejor, _ = crear_clinica(cabeceras, nombre="Mejor")
    calificar(buena["id"], 4.2, 10)
    calificar(mejor["id"], 4.8, 3)

    data = client.get(URL).json()["data"]

    assert [c["id"] for c in data] == [mejor["id"], buena["id"], sin_resenas["id"]]
    assert data[0]["calificacion"] == 4.8
    assert data[2]["calificacion"] is None


# Filtros
def nombres(client, **params) -> list[str]:
    respuesta = client.get(URL, params=params)
    assert respuesta.status_code == 200, respuesta.text
    return sorted(c["nombre"] for c in respuesta.json()["data"])


def test_q_busca_en_nombre_sin_importar_acentos_ni_mayusculas(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Hospital Animal Sur")

    assert nombres(client, q="clinica") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, q="PATITAS") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, q="gatos") == []


def test_q_busca_en_colonia(client, crear_clinica):
    _, cabeceras = crear_clinica()
    otra_direccion = {**DATOS_CLINICA["direccion"], "colonia": "Nápoles"}
    crear_clinica(cabeceras, nombre="Vet Nápoles", direccion=otra_direccion)

    assert nombres(client, q="del valle") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, q="napoles") == ["Vet Nápoles"]


def test_q_trata_los_comodines_como_texto(client, crear_clinica):
    crear_clinica()

    assert nombres(client, q="%%") == []
    assert nombres(client, q="__") == []


def test_q_de_una_letra_da_400(client):
    respuesta = client.get(URL, params={"q": "a"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["detalles"][0]["campo"] == "q"


def test_filtro_por_tipo(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Estética Pelos", tipos=["estetica", "hospedaje"])

    assert nombres(client, tipo="estetica") == ["Estética Pelos"]
    assert nombres(client, tipo="hospedaje") == ["Estética Pelos"]
    assert nombres(client, tipo="adiestramiento") == []


def test_tipo_desconocido_da_400(client):
    respuesta = client.get(URL, params={"tipo": "zoologico"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_filtro_por_categoria(client, crear_clinica):
    con_vacunas, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Sin servicios")
    servicios = f"{URL_NEGOCIO}/{con_vacunas['id']}/servicios"
    for nombre in ("Vacuna antirrábica", "Vacuna múltiple"):
        respuesta = client.post(
            servicios, json={"categoriaId": 3, "nombre": nombre}, headers=cabeceras
        )
        assert respuesta.status_code == 201, respuesta.text

    assert nombres(client, categoria="vacunas") == ["Clínica Veterinaria Patitas"]
    assert nombres(client, categoria="cirugia") == []
    assert nombres(client, categoria="no-existe") == []


def test_filtro_urgencias(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Hospital 24 horas", urgencias24h=True)

    assert nombres(client, urgencias="true") == ["Hospital 24 horas"]
    assert len(nombres(client, urgencias="false")) == 2


def test_filtros_combinados(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Hospital Patitas", tipos=["hospital"], urgencias24h=True)
    crear_clinica(cabeceras, nombre="Hospital Central", tipos=["hospital"])

    assert nombres(client, q="patitas", tipo="hospital", urgencias="true") == ["Hospital Patitas"]
    cuerpo = client.get(URL, params={"tipo": "hospital"}).json()
    assert cuerpo["meta"]["total"] == 2


# Ubicación
CENTRO = {"lat": 19.3801, "lng": -99.1702}


def test_rectangulo_contiene_al_circulo():
    lat_min, lat_max, lng_min, lng_max = rectangulo(19.3801, -99.1702, 5)

    assert distancia_km(19.3801, -99.1702, lat_max, -99.1702) >= 5
    assert distancia_km(19.3801, -99.1702, lat_min, -99.1702) >= 5
    assert distancia_km(19.3801, -99.1702, 19.3801, lng_max) >= 5
    assert distancia_km(19.3801, -99.1702, 19.3801, lng_min) >= 5
    assert distancia_km(19.3801, -99.1702, lat_max, -99.1702) < 5.2


def test_busqueda_por_radio_ordena_por_distancia(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="A tres km", lat=19.4071)
    crear_clinica(cabeceras, nombre="A veinte km", lat=19.5601)

    cerca = client.get(URL, params=CENTRO).json()
    lejos = client.get(URL, params={**CENTRO, "radioKm": 30}).json()

    assert [c["nombre"] for c in cerca["data"]] == ["Clínica Veterinaria Patitas", "A tres km"]
    assert [c["distanciaKm"] for c in cerca["data"]] == [0.0, 3.0]
    assert cerca["meta"]["total"] == 2
    assert [c["nombre"] for c in lejos["data"]][-1] == "A veinte km"
    assert lejos["meta"]["total"] == 3


def test_busqueda_descarta_la_esquina_del_rectangulo(client, crear_clinica):
    _, cabeceras = crear_clinica(lat=19.4161, lng=-99.1322)
    lat_min, lat_max, lng_min, lng_max = rectangulo(CENTRO["lat"], CENTRO["lng"], 5)

    assert lat_min <= 19.4161 <= lat_max
    assert lng_min <= -99.1322 <= lng_max
    assert nombres(client, **CENTRO) == []
    assert nombres(client, **CENTRO, radioKm=6) == ["Clínica Veterinaria Patitas"]


def test_ubicacion_se_combina_con_los_filtros(client, crear_clinica):
    _, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Hospital cercano", tipos=["hospital"], lat=19.3901)
    crear_clinica(cabeceras, nombre="Hospital lejano", tipos=["hospital"], lat=19.9001)

    assert nombres(client, **CENTRO, tipo="hospital") == ["Hospital cercano"]


def test_radio_sin_ubicacion_se_ignora(client, crear_clinica):
    crear_clinica()

    data = client.get(URL, params={"radioKm": 1}).json()["data"]

    assert len(data) == 1
    assert data[0]["distanciaKm"] is None


def test_lat_sin_lng_da_400(client):
    respuesta = client.get(URL, params={"lat": 19.38})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["mensaje"] == "lat y lng deben enviarse juntos"


def test_radio_fuera_de_rango_da_400(client):
    for radio in (0, 51):
        respuesta = client.get(URL, params={**CENTRO, "radioKm": radio})

        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["detalles"][0]["campo"] == "radioKm"


# Abierto ahora
ZONA = ZoneInfo("America/Mexico_City")
LUNES_10_AM = datetime(2026, 11, 9, 10, 0, tzinfo=ZONA)
LUNES_8_PM = datetime(2026, 11, 9, 20, 0, tzinfo=ZONA)


def fijar_hora(monkeypatch, momento: datetime) -> None:
    monkeypatch.setattr(service, "ahora_local", lambda: momento)


def test_filtro_abierto_ahora(client, crear_clinica, monkeypatch):
    con_horario, cabeceras = crear_clinica()
    crear_clinica(cabeceras, nombre="Sin horarios")
    crear_clinica(cabeceras, nombre="Hospital 24 horas", urgencias24h=True)
    lunes = {"horarios": [{"diaSemana": 1, "abre": "09:00", "cierra": "18:00"}]}
    respuesta = client.put(
        f"{URL_NEGOCIO}/{con_horario['id']}/horarios", json=lunes, headers=cabeceras
    )
    assert respuesta.status_code == 200, respuesta.text

    fijar_hora(monkeypatch, LUNES_10_AM)
    abiertas = ["Clínica Veterinaria Patitas", "Hospital 24 horas"]
    assert nombres(client, abiertoAhora="true") == abiertas
    assert len(nombres(client)) == 3

    fijar_hora(monkeypatch, LUNES_8_PM)
    assert nombres(client, abiertoAhora="true") == ["Hospital 24 horas"]


# Orden
def test_orden_por_resenas(client, crear_clinica):
    pocas, cabeceras = crear_clinica()
    muchas, _ = crear_clinica(cabeceras, nombre="Muchas reseñas")
    calificar(pocas["id"], 4.9, 3)
    calificar(muchas["id"], 4.1, 80)

    por_resenas = client.get(URL, params={"orden": "resenas"}).json()["data"]
    por_calificacion = client.get(URL, params={"orden": "calificacion"}).json()["data"]

    assert [c["id"] for c in por_resenas] == [muchas["id"], pocas["id"]]
    assert [c["id"] for c in por_calificacion] == [pocas["id"], muchas["id"]]


def test_orden_por_calificacion_con_ubicacion(client, crear_clinica):
    cerca, cabeceras = crear_clinica()
    lejos, _ = crear_clinica(cabeceras, nombre="Lejos pero mejor", lat=19.4071)
    calificar(cerca["id"], 3.5, 10)
    calificar(lejos["id"], 4.9, 10)

    por_defecto = client.get(URL, params=CENTRO).json()["data"]
    por_calificacion = client.get(URL, params={**CENTRO, "orden": "calificacion"}).json()["data"]

    assert [c["id"] for c in por_defecto] == [cerca["id"], lejos["id"]]
    assert [c["id"] for c in por_calificacion] == [lejos["id"], cerca["id"]]
    assert por_calificacion[0]["distanciaKm"] == 3.0


def test_orden_por_distancia_sin_ubicacion_da_400(client):
    respuesta = client.get(URL, params={"orden": "distancia"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_orden_desconocido_da_400(client):
    respuesta = client.get(URL, params={"orden": "precio"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["detalles"][0]["campo"] == "orden"


# Meta de la búsqueda
def test_meta_incluye_la_busqueda_usada(client, crear_clinica):
    crear_clinica()

    con_radio = client.get(URL, params={**CENTRO, "radioKm": 8}).json()["meta"]
    por_defecto = client.get(URL, params=CENTRO).json()["meta"]
    sin_ubicacion = client.get(URL, params={"radioKm": 8}).json()["meta"]

    assert con_radio["busqueda"] == {"lat": 19.3801, "lng": -99.1702, "radioKm": 8}
    assert por_defecto["busqueda"]["radioKm"] == 5
    assert sin_ubicacion["busqueda"] == SIN_UBICACION
    assert con_radio["total"] == 1
