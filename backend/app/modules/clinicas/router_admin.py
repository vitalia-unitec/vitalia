from typing import Annotated

from fastapi import APIRouter, Query

from app.core.database import DbSesion
from app.core.paginacion import ParametrosPagina
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import UsuarioAdmin
from app.modules.clinicas import repository, service
from app.modules.clinicas.schemas import EstadoEntrada, VerificacionEntrada

router = APIRouter(prefix="/admin/clinicas", tags=["Admin"])


@router.get("", summary="Listar clínicas para revisarlas")
def listar_clinicas(
    admin: UsuarioAdmin,
    db: DbSesion,
    pag: ParametrosPagina,
    verificada: bool | None = None,
    activa: bool | None = None,
    q: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
) -> dict:
    clinicas, total = repository.listar_para_admin(
        db, verificada, activa, q, pag.desde, pag.por_pagina
    )
    return ok([service.armar_detalle(c, para_negocio=True) for c in clinicas], pag.meta(total))


@router.patch("/{clinica_id}/verificacion", summary="Marcar o quitar la verificación")
def verificar_clinica(
    clinica_id: IdRuta, datos: VerificacionEntrada, admin: UsuarioAdmin, db: DbSesion
) -> dict:
    clinica = service.obtener_para_admin(db, clinica_id)
    clinica = service.marcar_verificada(db, clinica, datos.verificada)
    return ok(service.armar_detalle(clinica, para_negocio=True))


@router.patch("/{clinica_id}/estado", summary="Activar o suspender una clínica")
def cambiar_estado(
    clinica_id: IdRuta, datos: EstadoEntrada, admin: UsuarioAdmin, db: DbSesion
) -> dict:
    clinica = service.obtener_para_admin(db, clinica_id)
    clinica = service.cambiar_estado(db, clinica, datos.activa)
    return ok(service.armar_detalle(clinica, para_negocio=True))
