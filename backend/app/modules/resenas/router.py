from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.database import DbSesion
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import requerir_rol
from app.modules.clinicas import service as clinicas_service
from app.modules.resenas import service
from app.modules.resenas.schemas import ResenaEntrada
from app.modules.usuarios.models import Usuario

router = APIRouter(tags=["Reseñas"])

UsuarioDueno = Annotated[Usuario, Depends(requerir_rol("dueno"))]


@router.post(
    "/clinicas/{clinica_id}/resenas",
    status_code=status.HTTP_201_CREATED,
    summary="Dejar una reseña",
)
def crear_resena(
    clinica_id: IdRuta, datos: ResenaEntrada, usuario: UsuarioDueno, db: DbSesion
) -> dict:
    clinica = clinicas_service.obtener_publica(db, clinica_id)
    resena = service.crear(db, clinica, usuario, datos)
    return ok(service.armar_resena(resena, usuario))
