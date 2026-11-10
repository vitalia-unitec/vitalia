URL_NEGOCIO = "/api/v1/negocio/clinicas"


def test_detalle_publico(client, crear_clinica):
    clinica, _ = crear_clinica()

    respuesta = client.get(f"/api/v1/clinicas/{clinica['id']}")

    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert data["nombre"] == "Clínica Veterinaria Patitas"
    assert data["distanciaKm"] is None
    assert "esFavorito" not in data
    assert "activa" not in data


def test_detalle_con_distancia(client, crear_clinica):
    clinica, _ = crear_clinica()

    respuesta = client.get(
        f"/api/v1/clinicas/{clinica['id']}", params={"lat": 19.3855, "lng": -99.1702}
    )

    assert respuesta.json()["data"]["distanciaKm"] == 0.6


def test_detalle_con_solo_latitud(client, crear_clinica):
    clinica, _ = crear_clinica()

    respuesta = client.get(f"/api/v1/clinicas/{clinica['id']}", params={"lat": 19.38})

    assert respuesta.status_code == 400


def test_clinica_24_horas_siempre_abierta(client, crear_clinica):
    clinica, _ = crear_clinica(urgencias24h=True)

    data = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]

    assert data["urgencias24h"] is True
    assert data["abierto"] is True
    assert data["cierraA"] is None


def test_servicios_ordenados_por_categoria_y_destacados(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    base = f"{URL_NEGOCIO}/{clinica['id']}/servicios"
    servicios = [(4, "Cirugía"), (1, "Consulta general"), (3, "Vacuna antirrábica")]
    for categoria, nombre in servicios:
        datos = {"categoriaId": categoria, "nombre": nombre, "precio": 300}
        client.post(base, json=datos, headers=cabeceras)

    servicios = client.get(f"/api/v1/clinicas/{clinica['id']}/servicios").json()["data"]
    detalle = client.get(f"/api/v1/clinicas/{clinica['id']}").json()["data"]

    assert [s["nombre"] for s in servicios] == ["Consulta general", "Vacuna antirrábica", "Cirugía"]
    assert detalle["serviciosDestacados"] == ["Consulta general", "Vacuna antirrábica", "Cirugía"]


def test_clinica_inexistente_publica(client):
    respuesta = client.get("/api/v1/clinicas/999")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "NO_ENCONTRADO"
