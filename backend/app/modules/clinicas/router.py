from fastapi import APIRouter

from app.core.database import DbSesion
from app.core.paginacion import ParametrosPagina
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.clinicas import service
from app.modules.clinicas.filtros import Latitud, Longitud, ParametrosBusqueda, revisar_ubicacion
from app.modules.clinicas.schemas import ServicioSalida

router = APIRouter(prefix="/clinicas", tags=["Clínicas"])


@router.get("", summary="Buscar clínicas")
def buscar_clinicas(db: DbSesion, filtros: ParametrosBusqueda, pag: ParametrosPagina) -> dict:
    datos, total = service.buscar(db, filtros, pag)
    return ok(datos, {**pag.meta(total), "busqueda": filtros.meta()})


@router.get("/{clinica_id}", summary="Detalle completo de una clínica")
def ver_clinica(
    clinica_id: IdRuta,
    db: DbSesion,
    lat: Latitud = None,
    lng: Longitud = None,
) -> dict:
    revisar_ubicacion(lat, lng)
    clinica = service.obtener_publica(db, clinica_id)
    return ok(service.armar_detalle(clinica, lat, lng))


@router.get("/{clinica_id}/servicios", summary="Servicios con precio de una clínica")
def ver_servicios(clinica_id: IdRuta, db: DbSesion) -> dict:
    clinica = service.obtener_publica(db, clinica_id)
    return ok([ServicioSalida.model_validate(s).a_json() for s in clinica.servicios])


@router.get("/{clinica_id}/fotos", summary="Galería completa de una clínica")
def ver_fotos(clinica_id: IdRuta, db: DbSesion) -> dict:
    clinica = service.obtener_publica(db, clinica_id)
    return ok(service.armar_fotos(clinica.fotos))
