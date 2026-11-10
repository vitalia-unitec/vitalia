from sqlalchemy.orm import Session

from app.core.errors import NoEncontrado, SinPermiso
from app.core.tiempo import ahora_utc
from app.modules.comunidad import repository
from app.modules.comunidad.models import Comentario, Publicacion
from app.modules.comunidad.schemas import (
    AutorSalida,
    ComentarioEntrada,
    ComentarioSalida,
    PublicacionEntrada,
    PublicacionSalida,
)
from app.modules.usuarios.models import Usuario


# Armar respuestas
def armar_publicacion(publicacion: Publicacion, usuario: Usuario | None) -> dict:
    return PublicacionSalida(
        id=publicacion.id,
        autor=AutorSalida.desde_usuario(publicacion.autor),
        texto=publicacion.texto,
        fotos=[],
        total_comentarios=publicacion.total_comentarios,
        es_mia=None if usuario is None else publicacion.autor_id == usuario.id,
        creado_en=publicacion.creado_en,
        editado_en=publicacion.editado_en,
    ).a_json()


def armar_comentario(comentario: Comentario, usuario: Usuario | None) -> dict:
    return ComentarioSalida(
        id=comentario.id,
        autor=AutorSalida.desde_usuario(comentario.autor),
        texto=comentario.texto,
        es_mio=None if usuario is None else comentario.autor_id == usuario.id,
        creado_en=comentario.creado_en,
    ).a_json()


# Permisos
def _puede_borrar(autor_id: int | None, usuario: Usuario) -> bool:
    return usuario.rol == "admin" or autor_id == usuario.id


def obtener_publicacion(db: Session, publicacion_id: int) -> Publicacion:
    publicacion = repository.obtener_publicacion(db, publicacion_id)
    if publicacion is None:
        raise NoEncontrado("La publicación no existe")
    return publicacion


# Publicaciones
def publicar(db: Session, usuario: Usuario, datos: PublicacionEntrada) -> Publicacion:
    publicacion = Publicacion(autor_id=usuario.id, texto=datos.texto)
    repository.guardar(db, publicacion)
    return publicacion


def editar(
    db: Session, publicacion: Publicacion, usuario: Usuario, datos: PublicacionEntrada
) -> Publicacion:
    if publicacion.autor_id != usuario.id:
        raise SinPermiso("Solo el autor puede editar esta publicación")
    publicacion.texto = datos.texto
    publicacion.editado_en = ahora_utc()
    repository.guardar(db, publicacion)
    return publicacion


def borrar(db: Session, publicacion: Publicacion, usuario: Usuario) -> None:
    if not _puede_borrar(publicacion.autor_id, usuario):
        raise SinPermiso("Solo el autor o un admin pueden borrar esta publicación")
    repository.borrar(db, publicacion)


# Comentarios
def comentar(
    db: Session, publicacion: Publicacion, usuario: Usuario, datos: ComentarioEntrada
) -> Comentario:
    comentario = Comentario(publicacion_id=publicacion.id, autor_id=usuario.id, texto=datos.texto)
    repository.guardar(db, comentario)
    return comentario


def borrar_comentario(
    db: Session, publicacion: Publicacion, comentario_id: int, usuario: Usuario
) -> None:
    comentario = repository.obtener_comentario(db, comentario_id)
    if comentario is None or comentario.publicacion_id != publicacion.id:
        raise NoEncontrado("El comentario no existe en esta publicación")
    if not _puede_borrar(comentario.autor_id, usuario):
        raise SinPermiso("Solo el autor o un admin pueden borrar este comentario")
    repository.borrar(db, comentario)
