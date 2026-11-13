import pytest

from app.main import app

# Las únicas rutas que responden sin iniciar sesión; todas las demás deben dar 401
RUTAS_PUBLICAS = {
    ("GET", "/api/v1/salud"),
    ("POST", "/api/v1/auth/registro"),
    ("POST", "/api/v1/auth/login"),
    ("GET", "/api/v1/categorias"),
    ("GET", "/api/v1/clinicas"),
    ("GET", "/api/v1/clinicas/{clinica_id}"),
    ("GET", "/api/v1/clinicas/{clinica_id}/servicios"),
    ("GET", "/api/v1/clinicas/{clinica_id}/fotos"),
    ("GET", "/api/v1/clinicas/{clinica_id}/resenas"),
    ("GET", "/api/v1/comunidad"),
    ("GET", "/api/v1/comunidad/{publicacion_id}"),
    ("GET", "/api/v1/comunidad/{publicacion_id}/comentarios"),
}


def todas_las_rutas() -> list[tuple[str, str, str]]:
    rutas = []
    for plantilla, operaciones in app.openapi()["paths"].items():
        for metodo, operacion in operaciones.items():
            url = plantilla
            for parametro in operacion.get("parameters", []):
                if parametro["in"] == "path":
                    url = url.replace("{" + parametro["name"] + "}", "1")
            rutas.append((metodo.upper(), plantilla, url))
    return rutas


RUTAS = todas_las_rutas()
PROTEGIDAS = [r for r in RUTAS if (r[0], r[1]) not in RUTAS_PUBLICAS]


def nombre(ruta: tuple[str, str, str]) -> str:
    return f"{ruta[0]} {ruta[1]}"


def con_prefijo(prefijo: str) -> list[tuple[str, str, str]]:
    return [r for r in RUTAS if r[1].startswith(prefijo)]


@pytest.mark.parametrize("ruta", PROTEGIDAS, ids=nombre)
def test_sin_token_las_rutas_protegidas_dan_401(client, ruta):
    metodo, _, url = ruta

    respuesta = client.request(metodo, url)

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_la_lista_de_rutas_publicas_esta_al_dia(client):
    existentes = {(metodo, plantilla) for metodo, plantilla, _ in RUTAS}

    assert RUTAS_PUBLICAS <= existentes
    for metodo, plantilla, url in RUTAS:
        if (metodo, plantilla) in RUTAS_PUBLICAS:
            assert client.request(metodo, url).status_code != 401, plantilla


@pytest.mark.parametrize("ruta", con_prefijo("/api/v1/admin/"), ids=nombre)
def test_las_rutas_de_admin_rechazan_otros_roles(client, encabezados, encabezados_clinica, ruta):
    metodo, _, url = ruta

    for cabeceras in (encabezados(), encabezados_clinica()):
        respuesta = client.request(metodo, url, headers=cabeceras)

        assert respuesta.status_code == 403
        assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


@pytest.mark.parametrize("ruta", con_prefijo("/api/v1/negocio/"), ids=nombre)
def test_el_panel_de_negocio_rechaza_a_los_duenos(client, encabezados, ruta):
    metodo, _, url = ruta

    assert client.request(metodo, url, headers=encabezados()).status_code == 403


@pytest.mark.parametrize("ruta", con_prefijo("/api/v1/me/mascotas"), ids=nombre)
def test_el_carnet_rechaza_a_las_clinicas(client, encabezados_clinica, ruta):
    metodo, _, url = ruta

    assert client.request(metodo, url, headers=encabezados_clinica()).status_code == 403
