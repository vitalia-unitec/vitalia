from app.core.database import SessionLocal
from app.modules.clinicas.models import Clinica

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
