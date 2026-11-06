from fastapi import APIRouter, Request, status

from app.core.database import DbSesion
from app.core.responses import ok
from app.modules.auth import service
from app.modules.auth.dependencies import UsuarioActual
from app.modules.auth.schemas import LoginEntrada, RegistroEntrada
from app.modules.usuarios.schemas import UsuarioSalida

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", status_code=status.HTTP_201_CREATED, summary="Crear cuenta")
def registrar(datos: RegistroEntrada, db: DbSesion) -> dict:
    return ok(service.registrar(db, datos).a_json())


@router.post("/login", summary="Iniciar sesión")
def iniciar_sesion(datos: LoginEntrada, request: Request, db: DbSesion) -> dict:
    ip = request.client.host if request.client else "desconocida"
    return ok(service.iniciar_sesion(db, datos, ip).a_json())


@router.get("/me", summary="Datos del usuario actual")
def ver_mi_usuario(usuario: UsuarioActual) -> dict:
    return ok(UsuarioSalida.model_validate(usuario).a_json())
