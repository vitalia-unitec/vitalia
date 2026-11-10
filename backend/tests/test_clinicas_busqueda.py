from app.core.database import SessionLocal
from app.modules.clinicas.models import Clinica
from tests.conftest import DATOS_CLINICA

URL = "/api/v1/clinicas"
URL_NEGOCIO = "/api/v1/negocio/clinicas"

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
    assert cuerpo["meta"] == {"pagina": 1, "porPagina": 10, "total": 0, "totalPaginas": 0}


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
    assert primera["meta"] == {"pagina": 1, "porPagina": 2, "total": 3, "totalPaginas": 2}
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
