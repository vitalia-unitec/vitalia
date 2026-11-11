from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.resenas.models import Resena


def buscar_de_autor(db: Session, clinica_id: int, autor_id: int) -> Resena | None:
    consulta = select(Resena).where(Resena.clinica_id == clinica_id, Resena.autor_id == autor_id)
    return db.scalar(consulta)


def promedio_y_total(db: Session, clinica_id: int) -> tuple[float | None, int]:
    consulta = select(func.avg(Resena.calificacion), func.count(Resena.id)).where(
        Resena.clinica_id == clinica_id
    )
    promedio, total = db.execute(consulta).one()
    return promedio, total
