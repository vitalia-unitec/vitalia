import pytest

ID_GIGANTE = "99999999999999999999999"


@pytest.mark.parametrize(
    "ruta",
    [
        f"/api/v1/clinicas/{ID_GIGANTE}",
        f"/api/v1/clinicas/{ID_GIGANTE}/servicios",
        f"/api/v1/comunidad/{ID_GIGANTE}",
        f"/api/v1/comunidad/{ID_GIGANTE}/comentarios",
        "/api/v1/clinicas/0",
        "/api/v1/clinicas/-5",
    ],
)
def test_id_fuera_de_rango_da_400(client, ruta):
    respuesta = client.get(ruta)

    assert respuesta.status_code == 400
    error = respuesta.json()["error"]
    assert error["codigo"] == "VALIDACION"
    assert error["detalles"][0]["campo"].endswith("_id")


def test_id_fuera_de_rango_en_panel_de_negocio(client, encabezados_clinica):
    respuesta = client.get(f"/api/v1/negocio/clinicas/{ID_GIGANTE}", headers=encabezados_clinica())

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_id_valido_que_no_existe_sigue_dando_404(client):
    respuesta = client.get("/api/v1/clinicas/999")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "NO_ENCONTRADO"
