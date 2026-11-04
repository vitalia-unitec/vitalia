from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.database import DbSesion
from app.core.responses import ok

router = APIRouter(tags=["Salud"])


@router.get("/salud", summary="Revisa que la API y la base de datos respondan")
def revisar_salud(db: DbSesion) -> dict:
    settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
        estado_bd = "conectada"
    except SQLAlchemyError:
        estado_bd = "sin conexion"

    return ok(
        {
            "api": "funcionando",
            "baseDatos": estado_bd,
            "entorno": settings.app_entorno,
            "version": "0.1.0",
        }
    )
