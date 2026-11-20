from datetime import timedelta

import jwt
from fastapi import Depends

from app.core.config import get_settings
from app.core.tiempo import ahora_utc
from app.main import app
from app.modules.auth.dependencies import requerir_rol
from tests.conftest import DATOS_DUENO

URL_REGISTRO = "/api/v1/auth/registro"
URL_LOGIN = "/api/v1/auth/login"
URL_ME = "/api/v1/auth/me"


# Registro
def test_registro_exitoso_regresa_token_y_usuario(client):
    respuesta = client.post(URL_REGISTRO, json=DATOS_DUENO)

    assert respuesta.status_code == 201
    data = respuesta.json()["data"]
    assert data["token"]
    assert data["expiraEn"].endswith("-06:00")
    assert data["usuario"]["email"] == "rosa@mail.com"
    assert data["usuario"]["rol"] == "dueno"
    assert "password" not in data["usuario"]
    assert "passwordHash" not in data["usuario"]


def test_registro_normaliza_el_correo(client):
    respuesta = client.post(URL_REGISTRO, json={**DATOS_DUENO, "email": "Rosa@MAIL.com"})

    assert respuesta.json()["data"]["usuario"]["email"] == "rosa@mail.com"


def test_registro_con_correo_repetido_da_conflicto(client, registrar):
    registrar()
    respuesta = client.post(URL_REGISTRO, json={**DATOS_DUENO, "email": "ROSA@mail.com"})

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CONFLICTO"


def test_registro_rechaza_password_debil(client):
    respuesta = client.post(URL_REGISTRO, json={**DATOS_DUENO, "password": "soloLetras"})

    assert respuesta.status_code == 400
    error = respuesta.json()["error"]
    assert error["codigo"] == "VALIDACION"
    assert error["detalles"][0]["campo"] == "password"
    assert "número" in error["detalles"][0]["mensaje"]


def test_registro_no_permite_crear_admin(client):
    respuesta = client.post(URL_REGISTRO, json={**DATOS_DUENO, "rol": "admin"})

    assert respuesta.status_code == 400


def test_registro_valida_telefono(client):
    respuesta = client.post(URL_REGISTRO, json={**DATOS_DUENO, "telefono": "55-1234"})

    assert respuesta.status_code == 400


# Login
def test_login_exitoso(client, registrar):
    registrar()
    respuesta = client.post(URL_LOGIN, json={"email": "rosa@mail.com", "password": "Perrito2026"})

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["usuario"]["nombre"] == "Rosa Martínez"


def test_login_con_password_incorrecta(client, registrar):
    registrar()
    respuesta = client.post(URL_LOGIN, json={"email": "rosa@mail.com", "password": "Otra2026x"})

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


def test_login_con_correo_inexistente_da_el_mismo_error(client):
    respuesta = client.post(URL_LOGIN, json={"email": "nadie@mail.com", "password": "Perrito2026"})

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


def test_login_se_bloquea_tras_cinco_fallos(client, registrar):
    registrar()
    malos = {"email": "rosa@mail.com", "password": "Mala12345"}
    for _ in range(5):
        assert client.post(URL_LOGIN, json=malos).status_code == 401

    bueno = {"email": "rosa@mail.com", "password": "Perrito2026"}
    respuesta = client.post(URL_LOGIN, json=bueno)

    assert respuesta.status_code == 429
    assert respuesta.json()["error"]["codigo"] == "DEMASIADAS_PETICIONES"


# Token y /auth/me
def test_me_sin_token(client):
    respuesta = client.get(URL_ME)

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_me_con_token_alterado(client, registrar):
    token = registrar()["token"]
    respuesta = client.get(URL_ME, headers={"Authorization": f"Bearer {token}x"})

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "TOKEN_INVALIDO"


def test_me_con_token_vencido(client, registrar):
    usuario_id = registrar()["usuario"]["id"]
    settings = get_settings()
    vencido = jwt.encode(
        {"sub": str(usuario_id), "rol": "dueno", "exp": ahora_utc() - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algoritmo,
    )
    respuesta = client.get(URL_ME, headers={"Authorization": f"Bearer {vencido}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "TOKEN_INVALIDO"


def test_me_con_token_valido(client, encabezados):
    respuesta = client.get(URL_ME, headers=encabezados())

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["email"] == "rosa@mail.com"


# Roles
def test_requerir_rol_bloquea_a_otros_roles(client, encabezados):
    @app.get("/api/v1/prueba-solo-clinica", dependencies=[Depends(requerir_rol("clinica"))])
    def solo_clinica() -> dict:
        return {"ok": True}

    try:
        dueno = client.get("/api/v1/prueba-solo-clinica", headers=encabezados())
        clinica = client.get(
            "/api/v1/prueba-solo-clinica",
            headers=encabezados(email="vet@mail.com", rol="clinica"),
        )
    finally:
        app.router.routes.pop()

    assert dueno.status_code == 403
    assert dueno.json()["error"]["codigo"] == "SIN_PERMISO"
    assert clinica.status_code == 200
