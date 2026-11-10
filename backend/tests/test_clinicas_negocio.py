from tests.conftest import DATOS_CLINICA

URL = "/api/v1/negocio/clinicas"


# Registrar
def test_registrar_clinica(crear_clinica):
    clinica, _ = crear_clinica()

    assert clinica["nombre"] == "Clínica Veterinaria Patitas"
    assert clinica["tipos"] == ["veterinaria"]
    assert clinica["activa"] is True
    assert clinica["verificada"] is False
    assert clinica["direccion"]["textoCompleto"].startswith("Av. Insurgentes 123, Col. Del Valle")
    assert clinica["horarios"] == []
    assert clinica["servicios"] == []


def test_un_dueno_no_puede_registrar_clinicas(client, encabezados):
    respuesta = client.post(URL, json=DATOS_CLINICA, headers=encabezados())

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERMISO"


def test_sin_sesion_no_puede_registrar(client):
    respuesta = client.post(URL, json=DATOS_CLINICA)

    assert respuesta.status_code == 401


def test_registrar_valida_tipos_y_codigo_postal(client, encabezados_clinica):
    cabeceras = encabezados_clinica()
    sin_tipos = {**DATOS_CLINICA, "tipos": []}
    tipo_raro = {**DATOS_CLINICA, "tipos": ["peluqueria"]}
    cp_malo = {**DATOS_CLINICA, "direccion": {**DATOS_CLINICA["direccion"], "codigoPostal": "123"}}

    for datos in (sin_tipos, tipo_raro, cp_malo):
        respuesta = client.post(URL, json=datos, headers=cabeceras)
        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_tipos_repetidos_se_guardan_una_vez(crear_clinica):
    clinica, _ = crear_clinica(tipos=["estetica", "veterinaria", "estetica"])

    assert clinica["tipos"] == ["estetica", "veterinaria"]


# Consultar y editar
def test_listar_solo_mis_clinicas(client, crear_clinica, encabezados_clinica):
    _, mias = crear_clinica()
    crear_clinica(nombre="Otra Clínica", cabeceras=encabezados_clinica("otra@mail.com"))

    respuesta = client.get(URL, headers=mias)

    nombres = [c["nombre"] for c in respuesta.json()["data"]]
    assert nombres == ["Clínica Veterinaria Patitas"]


def test_editar_mi_clinica(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    cambios = {**DATOS_CLINICA, "nombre": "Patitas Del Valle", "tipos": ["hospital", "estetica"]}

    respuesta = client.put(f"{URL}/{clinica['id']}", json=cambios, headers=cabeceras)

    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert data["nombre"] == "Patitas Del Valle"
    assert data["tipos"] == ["estetica", "hospital"]


def test_no_puedo_editar_una_clinica_ajena(client, crear_clinica, encabezados_clinica):
    clinica, _ = crear_clinica()
    intruso = encabezados_clinica("intruso@mail.com")

    respuesta = client.put(f"{URL}/{clinica['id']}", json=DATOS_CLINICA, headers=intruso)

    assert respuesta.status_code == 403


def test_clinica_inexistente(client, encabezados_clinica):
    respuesta = client.get(f"{URL}/999", headers=encabezados_clinica())

    assert respuesta.status_code == 404


def test_dar_de_baja_la_oculta_al_publico(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    assert client.delete(f"{URL}/{clinica['id']}", headers=cabeceras).status_code == 204
    assert client.get(f"/api/v1/clinicas/{clinica['id']}").status_code == 404
    mis_clinicas = client.get(URL, headers=cabeceras).json()["data"]
    assert mis_clinicas[0]["activa"] is False


# Horarios
def test_reemplazar_horarios(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    horarios = {
        "horarios": [
            {"diaSemana": 6, "abre": "10:00", "cierra": "15:00"},
            {"diaSemana": 1, "abre": "16:00", "cierra": "21:00"},
            {"diaSemana": 1, "abre": "09:00", "cierra": "14:00"},
        ]
    }

    respuesta = client.put(f"{URL}/{clinica['id']}/horarios", json=horarios, headers=cabeceras)

    assert respuesta.status_code == 200
    assert respuesta.json()["data"] == [
        {"diaSemana": 1, "abre": "09:00", "cierra": "14:00"},
        {"diaSemana": 1, "abre": "16:00", "cierra": "21:00"},
        {"diaSemana": 6, "abre": "10:00", "cierra": "15:00"},
    ]


def test_horario_con_cierre_antes_de_abrir(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    malo = {"horarios": [{"diaSemana": 1, "abre": "21:00", "cierra": "09:00"}]}

    respuesta = client.put(f"{URL}/{clinica['id']}/horarios", json=malo, headers=cabeceras)

    assert respuesta.status_code == 400


def test_horarios_encimados(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    encimados = {
        "horarios": [
            {"diaSemana": 2, "abre": "09:00", "cierra": "14:00"},
            {"diaSemana": 2, "abre": "13:00", "cierra": "18:00"},
        ]
    }

    respuesta = client.put(f"{URL}/{clinica['id']}/horarios", json=encimados, headers=cabeceras)

    assert respuesta.status_code == 400
    assert "martes" in respuesta.json()["error"]["detalles"][0]["mensaje"]


# Servicios
def test_agregar_editar_y_borrar_servicio(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    base = f"{URL}/{clinica['id']}/servicios"
    datos = {"categoriaId": 4, "nombre": "Cirugía", "precio": 2000, "esPrecioDesde": True}

    creado = client.post(base, json=datos, headers=cabeceras)
    assert creado.status_code == 201
    servicio = creado.json()["data"]
    assert servicio["categoria"]["slug"] == "cirugia"
    assert servicio["precio"] == 2000.0

    editado = client.put(
        f"{base}/{servicio['id']}", json={**datos, "precio": 2500}, headers=cabeceras
    )
    assert editado.json()["data"]["precio"] == 2500.0

    assert client.delete(f"{base}/{servicio['id']}", headers=cabeceras).status_code == 204
    assert client.get(f"/api/v1/clinicas/{clinica['id']}/servicios").json()["data"] == []


def test_servicio_con_categoria_inexistente(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    datos = {"categoriaId": 99, "nombre": "Algo", "precio": 100}

    respuesta = client.post(f"{URL}/{clinica['id']}/servicios", json=datos, headers=cabeceras)

    assert respuesta.status_code == 400


def test_sin_precio_no_puede_ser_precio_desde(client, crear_clinica):
    clinica, cabeceras = crear_clinica()
    datos = {"categoriaId": 1, "nombre": "Consulta", "precio": None, "esPrecioDesde": True}

    respuesta = client.post(f"{URL}/{clinica['id']}/servicios", json=datos, headers=cabeceras)

    assert respuesta.json()["data"]["esPrecioDesde"] is False


def test_servicio_de_otra_clinica(client, crear_clinica):
    clinica_a, cabeceras = crear_clinica()
    clinica_b, _ = crear_clinica(cabeceras=cabeceras, nombre="Sucursal Sur")
    servicio = client.post(
        f"{URL}/{clinica_a['id']}/servicios",
        json={"categoriaId": 1, "nombre": "Consulta", "precio": 350},
        headers=cabeceras,
    ).json()["data"]

    respuesta = client.delete(
        f"{URL}/{clinica_b['id']}/servicios/{servicio['id']}", headers=cabeceras
    )

    assert respuesta.status_code == 404


# Borrar cuenta de clínica
def test_no_se_borra_cuenta_con_clinicas_activas(client, crear_clinica):
    clinica, cabeceras = crear_clinica()

    respuesta = client.delete("/api/v1/me", headers=cabeceras)
    assert respuesta.status_code == 409

    client.delete(f"{URL}/{clinica['id']}", headers=cabeceras)
    assert client.delete("/api/v1/me", headers=cabeceras).status_code == 204
