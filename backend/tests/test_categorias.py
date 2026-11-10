def test_categorias_iniciales(client):
    respuesta = client.get("/api/v1/categorias")

    assert respuesta.status_code == 200
    categorias = respuesta.json()["data"]
    assert len(categorias) == 10
    assert categorias[0] == {
        "id": 1,
        "nombre": "Consulta general",
        "slug": "consulta-general",
        "icono": "stethoscope",
    }
