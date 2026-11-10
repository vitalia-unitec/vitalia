from app.core.database import SessionLocal
from app.modules.usuarios.models import Usuario

URL = "/api/v1/comunidad"


def publicar(client, cabeceras, texto="Mi perrita ya tiene todas sus vacunas") -> dict:
    respuesta = client.post(URL, json={"texto": texto}, headers=cabeceras)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["data"]


# Publicaciones
def test_publicar_y_leer_sin_sesion(client, encabezados):
    publicacion = publicar(client, encabezados())

    assert publicacion["autor"] == {"id": 1, "nombre": "Rosa M."}
    assert publicacion["esMia"] is True
    assert publicacion["fotos"] == []
    assert publicacion["totalComentarios"] == 0
    assert publicacion["editadoEn"] is None

    publica = client.get(f"{URL}/{publicacion['id']}").json()["data"]
    assert publica["esMia"] is None


def test_sin_sesion_no_se_puede_publicar(client):
    respuesta = client.post(URL, json={"texto": "Hola"})

    assert respuesta.status_code == 401


def test_una_clinica_tambien_puede_publicar(client, encabezados_clinica):
    publicacion = publicar(client, encabezados_clinica(), "Campaña de vacunación este sábado")

    assert publicacion["texto"] == "Campaña de vacunación este sábado"


def test_texto_vacio_o_muy_largo(client, encabezados):
    cabeceras = encabezados()

    assert client.post(URL, json={"texto": "   "}, headers=cabeceras).status_code == 400
    assert client.post(URL, json={"texto": "a" * 2001}, headers=cabeceras).status_code == 400


def test_lista_paginada_mas_reciente_primero(client, encabezados):
    cabeceras = encabezados()
    for numero in range(3):
        publicar(client, cabeceras, f"Publicación {numero}")

    respuesta = client.get(URL, params={"pagina": 1, "porPagina": 2}).json()

    assert [p["texto"] for p in respuesta["data"]] == ["Publicación 2", "Publicación 1"]
    assert respuesta["meta"] == {"pagina": 1, "porPagina": 2, "total": 3, "totalPaginas": 2}


def test_editar_mi_publicacion(client, encabezados):
    cabeceras = encabezados()
    publicacion = publicar(client, cabeceras)

    respuesta = client.put(
        f"{URL}/{publicacion['id']}", json={"texto": "Editado"}, headers=cabeceras
    )

    data = respuesta.json()["data"]
    assert data["texto"] == "Editado"
    assert data["editadoEn"] is not None


def test_no_puedo_editar_ni_borrar_lo_ajeno(client, encabezados):
    publicacion = publicar(client, encabezados())
    otro = encabezados(email="otro@mail.com")

    editar = client.put(f"{URL}/{publicacion['id']}", json={"texto": "Hackeado"}, headers=otro)
    borrar = client.delete(f"{URL}/{publicacion['id']}", headers=otro)

    assert editar.status_code == 403
    assert borrar.status_code == 403


def test_borrar_mi_publicacion_borra_sus_comentarios(client, encabezados):
    cabeceras = encabezados()
    publicacion = publicar(client, cabeceras)
    client.post(
        f"{URL}/{publicacion['id']}/comentarios", json={"texto": "Qué bien"}, headers=cabeceras
    )

    assert client.delete(f"{URL}/{publicacion['id']}", headers=cabeceras).status_code == 204
    assert client.get(f"{URL}/{publicacion['id']}").status_code == 404


# Comentarios
def test_comentar_y_listar(client, encabezados):
    publicacion = publicar(client, encabezados())
    otro = encabezados(email="luis@mail.com", nombre="Luis")
    ruta = f"{URL}/{publicacion['id']}/comentarios"

    creado = client.post(ruta, json={"texto": "¿Dónde la vacunaste?"}, headers=otro)
    assert creado.status_code == 201
    assert creado.json()["data"]["autor"]["nombre"] == "Luis"

    comentarios = client.get(ruta).json()
    assert comentarios["meta"]["total"] == 1
    assert client.get(f"{URL}/{publicacion['id']}").json()["data"]["totalComentarios"] == 1


def test_comentar_publicacion_inexistente(client, encabezados):
    respuesta = client.post(f"{URL}/999/comentarios", json={"texto": "Hola"}, headers=encabezados())

    assert respuesta.status_code == 404


def test_solo_el_autor_borra_su_comentario(client, encabezados):
    publicacion = publicar(client, encabezados())
    autor = encabezados(email="luis@mail.com")
    otro = encabezados(email="ana@mail.com")
    ruta = f"{URL}/{publicacion['id']}/comentarios"
    comentario = client.post(ruta, json={"texto": "Hola"}, headers=autor).json()["data"]

    assert client.delete(f"{ruta}/{comentario['id']}", headers=otro).status_code == 403
    assert client.delete(f"{ruta}/{comentario['id']}", headers=autor).status_code == 204


# Moderación y cuentas borradas
def test_admin_puede_borrar_lo_de_otros(client, encabezados):
    publicacion = publicar(client, encabezados())
    cabeceras_admin = encabezados(email="admin@mail.com")
    with SessionLocal() as db:
        admin = db.query(Usuario).filter_by(email="admin@mail.com").one()
        admin.rol = "admin"
        db.commit()

    respuesta = client.delete(f"{URL}/{publicacion['id']}", headers=cabeceras_admin)

    assert respuesta.status_code == 204


def test_al_borrar_la_cuenta_queda_como_usuario_eliminado(client, encabezados):
    cabeceras = encabezados()
    publicacion = publicar(client, cabeceras)

    client.delete("/api/v1/me", headers=cabeceras)

    autor = client.get(f"{URL}/{publicacion['id']}").json()["data"]["autor"]
    assert autor == {"id": None, "nombre": "Usuario eliminado"}
