from time import perf_counter

from app.core.database import SessionLocal
from scripts.sembrar_demo import sembrar

URL = "/api/v1/clinicas"
LIMITE_SEGUNDOS = 0.5

BUSQUEDAS = [
    {},
    {"q": "demo", "orden": "resenas"},
    {"lat": 19.4326, "lng": -99.1332, "radioKm": 5},
    {"lat": 19.4326, "lng": -99.1332, "radioKm": 50, "porPagina": 50},
    {"lat": 19.4326, "lng": -99.1332, "radioKm": 50, "abiertoAhora": "true", "tipo": "hospital"},
    {"categoria": "vacunas", "abiertoAhora": "true"},
]


def mejor_tiempo(client, params: dict) -> float:
    tiempos = []
    for _ in range(3):
        inicio = perf_counter()
        respuesta = client.get(URL, params=params)
        tiempos.append(perf_counter() - inicio)
        assert respuesta.status_code == 200, respuesta.text
    return min(tiempos)


def test_busqueda_con_mil_clinicas_responde_rapido(client):
    with SessionLocal() as db:
        assert sembrar(db, 1000) == 1000

    assert client.get(URL).json()["meta"]["total"] == 1000
    for params in BUSQUEDAS:
        segundos = mejor_tiempo(client, params)
        assert segundos < LIMITE_SEGUNDOS, f"{params} tardó {segundos:.3f} s"


def test_sembrar_reemplaza_los_datos_de_demostracion(client):
    with SessionLocal() as db:
        sembrar(db, 30)
        sembrar(db, 12)

    cuerpo = client.get(URL, params={"porPagina": 50}).json()

    assert cuerpo["meta"]["total"] == 12
    assert all("Demo" in c["nombre"] for c in cuerpo["data"])
    assert not any(c["verificada"] for c in cuerpo["data"])
