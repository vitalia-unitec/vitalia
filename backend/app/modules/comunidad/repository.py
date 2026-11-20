from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.comunidad.models import Comentario, Publicacion


def listar_publicaciones(db: Session, desde: int, cuantas: int) -> tuple[list[Publicacion], int]:
    total = db.scalar(select(func.count(Publicacion.id))) or 0
    consulta = (
        select(Publicacion)
        .order_by(Publicacion.creado_en.desc(), Publicacion.id.desc())
        .offset(desde)
        .limit(cuantas)
    )
    return list(db.scalars(consulta)), total


def obtener_publicacion(db: Session, publicacion_id: int) -> Publicacion | None:
    return db.get(Publicacion, publicacion_id)


def listar_comentarios(
    db: Session, publicacion_id: int, desde: int, cuantos: int
) -> tuple[list[Comentario], int]:
    filtro = Comentario.publicacion_id == publicacion_id
    total = db.scalar(select(func.count(Comentario.id)).where(filtro)) or 0
    consulta = (
        select(Comentario)
        .where(filtro)
        .order_by(Comentario.creado_en, Comentario.id)
        .offset(desde)
        .limit(cuantos)
    )
    return list(db.scalars(consulta)), total


def obtener_comentario(db: Session, comentario_id: int) -> Comentario | None:
    return db.get(Comentario, comentario_id)


def guardar(db: Session, objeto: object) -> None:
    db.add(objeto)
    db.commit()
    db.refresh(objeto)


def borrar(db: Session, objeto: object) -> None:
    db.delete(objeto)
    db.commit()
