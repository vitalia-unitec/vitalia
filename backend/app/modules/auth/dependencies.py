from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import DbSesion
from app.core.errors import NoAutenticado, SinPermiso, TokenInvalido
from app.core.security import decodificar_token
from app.modules.usuarios import repository
from app.modules.usuarios.models import Usuario

esquema_bearer = HTTPBearer(auto_error=False, description="Token que regresa el login")
Credenciales = Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)]


def _usuario_desde_token(db: DbSesion, token: str) -> Usuario:
    try:
        datos = decodificar_token(token)
        usuario_id = int(datos["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise TokenInvalido() from exc

    usuario = repository.buscar_por_id(db, usuario_id)
    if usuario is None:
        raise TokenInvalido()
    return usuario


# Usuario obligatorio
def obtener_usuario_actual(db: DbSesion, credenciales: Credenciales) -> Usuario:
    if credenciales is None:
        raise NoAutenticado()
    return _usuario_desde_token(db, credenciales.credentials)


# Usuario opcional, para endpoints públicos que cambian si hay sesión
def obtener_usuario_opcional(db: DbSesion, credenciales: Credenciales) -> Usuario | None:
    if credenciales is None:
        return None
    try:
        return _usuario_desde_token(db, credenciales.credentials)
    except TokenInvalido:
        return None


UsuarioActual = Annotated[Usuario, Depends(obtener_usuario_actual)]
UsuarioOpcional = Annotated[Usuario | None, Depends(obtener_usuario_opcional)]


# Control por rol
def requerir_rol(*roles: str) -> Callable[[Usuario], Usuario]:
    def revisar(usuario: UsuarioActual) -> Usuario:
        if usuario.rol not in roles:
            raise SinPermiso()
        return usuario

    return revisar


UsuarioDueno = Annotated[Usuario, Depends(requerir_rol("dueno"))]
UsuarioAdmin = Annotated[Usuario, Depends(requerir_rol("admin"))]
