from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.database import DbSesion
from app.core.paginacion import ParametrosPagina
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import UsuarioActual, UsuarioOpcional, requerir_rol
from app.modules.clinicas import service as clinicas_service
from app.modules.resenas import repository, service
from app.modules.resenas.repository import OrdenResenas
from app.modules.resenas.schemas import ResenaEntrada
from app.modules.usuarios.models import Usuario

router = APIRouter(tags=["Reseñas"])

UsuarioDueno = Annotated[Usuario, Depends(requerir_rol("dueno"))]


# Reseñas de una clínica
@router.get("/clinicas/{clinica_id}/resenas", summary="Reseñas de una clínica")
def listar_resenas(
    clinica_id: IdRuta,
    db: DbSesion,
    usuario: UsuarioOpcional,
    pag: ParametrosPagina,
    orden: Annotated[OrdenResenas, Query()] = "recientes",
) -> dict:
    clinica = clinicas_service.obtener_publica(db, clinica_id)
    resenas = repository.listar(db, clinica.id, orden, pag.desde, pag.por_pagina)
    meta = {**pag.meta(clinica.total_resenas), "resumen": service.armar_resumen(db, clinica)}
    return ok([service.armar_resena(r, usuario) for r in resenas], meta)


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


# Mi reseña
@router.put("/resenas/{resena_id}", summary="Editar mi reseña")
def editar_resena(
    resena_id: IdRuta, datos: ResenaEntrada, usuario: UsuarioActual, db: DbSesion
) -> dict:
    resena = service.obtener(db, resena_id)
    resena = service.editar(db, resena, usuario, datos)
    return ok(service.armar_resena(resena, usuario))


@router.delete(
    "/resenas/{resena_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrar mi reseña"
)
def borrar_resena(resena_id: IdRuta, usuario: UsuarioActual, db: DbSesion) -> Response:
    resena = service.obtener(db, resena_id)
    service.borrar(db, resena, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
