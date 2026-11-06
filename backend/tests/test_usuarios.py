URL_ME = "/api/v1/me"
URL_LOGIN = "/api/v1/auth/login"


def test_editar_perfil(client, encabezados):
    respuesta = client.patch(
        URL_ME, json={"nombre": "Rosa M. López", "telefono": "5511112222"}, headers=encabezados()
    )

    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert data["nombre"] == "Rosa M. López"
    assert data["telefono"] == "5511112222"


def test_editar_perfil_no_cambia_correo_ni_rol(client, encabezados):
    respuesta = client.patch(
        URL_ME, json={"email": "otro@mail.com", "rol": "admin"}, headers=encabezados()
    )

    data = respuesta.json()["data"]
    assert data["email"] == "rosa@mail.com"
    assert data["rol"] == "dueno"


def test_cambiar_password(client, encabezados):
    cabeceras = encabezados()
    respuesta = client.put(
        f"{URL_ME}/password",
        json={"passwordActual": "Perrito2026", "passwordNueva": "Gatito2027"},
        headers=cabeceras,
    )

    assert respuesta.status_code == 204
    login = client.post(URL_LOGIN, json={"email": "rosa@mail.com", "password": "Gatito2027"})
    assert login.status_code == 200


def test_cambiar_password_con_actual_incorrecta(client, encabezados):
    respuesta = client.put(
        f"{URL_ME}/password",
        json={"passwordActual": "NoEsLaMia1", "passwordNueva": "Gatito2027"},
        headers=encabezados(),
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


def test_borrar_cuenta_invalida_el_token(client, encabezados):
    cabeceras = encabezados()

    assert client.delete(URL_ME, headers=cabeceras).status_code == 204
    respuesta = client.get("/api/v1/auth/me", headers=cabeceras)
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "TOKEN_INVALIDO"
