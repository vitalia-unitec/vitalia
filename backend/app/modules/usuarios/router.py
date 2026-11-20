from fastapi import APIRouter, Response, status

from app.core.database import DbSesion
from app.core.responses import ok
from app.modules.auth.dependencies import UsuarioActual
from app.modules.usuarios import service
from app.modules.usuarios.schemas import ActualizarPerfil, CambiarPassword, UsuarioSalida

router = APIRouter(prefix="/me", tags=["Mi cuenta"])


@router.patch("", summary="Editar nombre o teléfono")
def editar_perfil(datos: ActualizarPerfil, usuario: UsuarioActual, db: DbSesion) -> dict:
    actualizado = service.actualizar_perfil(db, usuario, datos)
    return ok(UsuarioSalida.model_validate(actualizado).a_json())


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT, summary="Cambiar contraseña")
def cambiar_password(datos: CambiarPassword, usuario: UsuarioActual, db: DbSesion) -> Response:
    service.cambiar_password(db, usuario, datos)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Borrar mi cuenta")
def borrar_cuenta(usuario: UsuarioActual, db: DbSesion) -> Response:
    service.borrar_cuenta(db, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
