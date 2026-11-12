from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.resenas.models import Resena

OrdenResenas = Literal["recientes", "mejores", "peores"]

ORDENES = {
    "recientes": (Resena.creado_en.desc(), Resena.id.desc()),
    "mejores": (Resena.calificacion.desc(), Resena.creado_en.desc(), Resena.id.desc()),
    "peores": (Resena.calificacion.asc(), Resena.creado_en.desc(), Resena.id.desc()),
}


def obtener(db: Session, resena_id: int) -> Resena | None:
    return db.get(Resena, resena_id)


def buscar_de_autor(db: Session, clinica_id: int, autor_id: int) -> Resena | None:
    consulta = select(Resena).where(Resena.clinica_id == clinica_id, Resena.autor_id == autor_id)
    return db.scalar(consulta)


def listar(
    db: Session, clinica_id: int, orden: OrdenResenas, desde: int, cuantas: int
) -> list[Resena]:
    consulta = (
        select(Resena)
        .where(Resena.clinica_id == clinica_id)
        .order_by(*ORDENES[orden])
        .offset(desde)
        .limit(cuantas)
    )
    return list(db.scalars(consulta))


def promedio_y_total(db: Session, clinica_id: int) -> tuple[float | None, int]:
    consulta = select(func.avg(Resena.calificacion), func.count(Resena.id)).where(
        Resena.clinica_id == clinica_id
    )
    promedio, total = db.execute(consulta).one()
    return promedio, total


def distribucion(db: Session, clinica_id: int) -> dict[int, int]:
    consulta = (
        select(Resena.calificacion, func.count(Resena.id))
        .where(Resena.clinica_id == clinica_id)
        .group_by(Resena.calificacion)
    )
    return {calificacion: cuantas for calificacion, cuantas in db.execute(consulta)}
