from fastapi import APIRouter, Response, status

from app.core.database import DbSesion
from app.core.paginacion import ParametrosPagina
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import UsuarioActual, UsuarioOpcional
from app.modules.comunidad import repository, service
from app.modules.comunidad.schemas import ComentarioEntrada, PublicacionEntrada

router = APIRouter(prefix="/comunidad", tags=["Comunidad"])


# Publicaciones
@router.get("", summary="Publicaciones, la más reciente primero")
def listar_publicaciones(db: DbSesion, usuario: UsuarioOpcional, pag: ParametrosPagina) -> dict:
    publicaciones, total = repository.listar_publicaciones(db, pag.desde, pag.por_pagina)
    datos = [service.armar_publicacion(p, usuario) for p in publicaciones]
    return ok(datos, pag.meta(total))


@router.get("/{publicacion_id}", summary="Una publicación")
def ver_publicacion(publicacion_id: IdRuta, db: DbSesion, usuario: UsuarioOpcional) -> dict:
    publicacion = service.obtener_publicacion(db, publicacion_id)
    return ok(service.armar_publicacion(publicacion, usuario))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Publicar")
def publicar(datos: PublicacionEntrada, usuario: UsuarioActual, db: DbSesion) -> dict:
    publicacion = service.publicar(db, usuario, datos)
    return ok(service.armar_publicacion(publicacion, usuario))


@router.put("/{publicacion_id}", summary="Editar mi publicación")
def editar(
    publicacion_id: IdRuta, datos: PublicacionEntrada, usuario: UsuarioActual, db: DbSesion
) -> dict:
    publicacion = service.obtener_publicacion(db, publicacion_id)
    publicacion = service.editar(db, publicacion, usuario, datos)
    return ok(service.armar_publicacion(publicacion, usuario))


@router.delete(
    "/{publicacion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrar publicación"
)
def borrar(publicacion_id: IdRuta, usuario: UsuarioActual, db: DbSesion) -> Response:
    publicacion = service.obtener_publicacion(db, publicacion_id)
    service.borrar(db, publicacion, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Comentarios
@router.get("/{publicacion_id}/comentarios", summary="Comentarios, el más antiguo primero")
def listar_comentarios(
    publicacion_id: IdRuta, db: DbSesion, usuario: UsuarioOpcional, pag: ParametrosPagina
) -> dict:
    service.obtener_publicacion(db, publicacion_id)
    comentarios, total = repository.listar_comentarios(
        db, publicacion_id, pag.desde, pag.por_pagina
    )
    datos = [service.armar_comentario(c, usuario) for c in comentarios]
    return ok(datos, pag.meta(total))


@router.post(
    "/{publicacion_id}/comentarios", status_code=status.HTTP_201_CREATED, summary="Comentar"
)
def comentar(
    publicacion_id: IdRuta, datos: ComentarioEntrada, usuario: UsuarioActual, db: DbSesion
) -> dict:
    publicacion = service.obtener_publicacion(db, publicacion_id)
    comentario = service.comentar(db, publicacion, usuario, datos)
    return ok(service.armar_comentario(comentario, usuario))


@router.delete(
    "/{publicacion_id}/comentarios/{comentario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Borrar comentario",
)
def borrar_comentario(
    publicacion_id: IdRuta, comentario_id: IdRuta, usuario: UsuarioActual, db: DbSesion
) -> Response:
    publicacion = service.obtener_publicacion(db, publicacion_id)
    service.borrar_comentario(db, publicacion, comentario_id, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
