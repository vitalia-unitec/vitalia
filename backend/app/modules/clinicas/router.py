from typing import Annotated

from fastapi import APIRouter, Query

from app.core.database import DbSesion
from app.core.errors import AppError
from app.core.paginacion import ParametrosPagina
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.clinicas import service
from app.modules.clinicas.filtros import ParametrosBusqueda
from app.modules.clinicas.schemas import ServicioSalida

router = APIRouter(prefix="/clinicas", tags=["Clínicas"])

Latitud = Annotated[float | None, Query(ge=-90, le=90, description="Tu latitud")]
Longitud = Annotated[float | None, Query(ge=-180, le=180, description="Tu longitud")]


@router.get("", summary="Buscar clínicas")
def buscar_clinicas(db: DbSesion, filtros: ParametrosBusqueda, pag: ParametrosPagina) -> dict:
    datos, total = service.buscar(db, filtros, pag)
    return ok(datos, pag.meta(total))


@router.get("/{clinica_id}", summary="Detalle completo de una clínica")
def ver_clinica(
    clinica_id: IdRuta,
    db: DbSesion,
    lat: Latitud = None,
    lng: Longitud = None,
) -> dict:
    if (lat is None) != (lng is None):
        raise AppError("VALIDACION", "lat y lng deben enviarse juntos", 400)
    clinica = service.obtener_publica(db, clinica_id)
    return ok(service.armar_detalle(clinica, lat, lng))


@router.get("/{clinica_id}/servicios", summary="Servicios con precio de una clínica")
def ver_servicios(clinica_id: IdRuta, db: DbSesion) -> dict:
    clinica = service.obtener_publica(db, clinica_id)
    return ok([ServicioSalida.model_validate(s).a_json() for s in clinica.servicios])
