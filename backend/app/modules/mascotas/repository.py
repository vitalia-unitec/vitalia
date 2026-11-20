from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mascotas.models import Mascota


def listar_de_dueno(db: Session, dueno_id: int) -> list[Mascota]:
    consulta = select(Mascota).where(Mascota.dueno_id == dueno_id).order_by(Mascota.id)
    return list(db.scalars(consulta))


def obtener_de_dueno(db: Session, mascota_id: int, dueno_id: int) -> Mascota | None:
    consulta = select(Mascota).where(Mascota.id == mascota_id, Mascota.dueno_id == dueno_id)
    return db.scalar(consulta)


def contar_de_dueno(db: Session, dueno_id: int) -> int:
    consulta = select(func.count(Mascota.id)).where(Mascota.dueno_id == dueno_id)
    return db.scalar(consulta) or 0


def guardar(db: Session, mascota: Mascota) -> None:
    db.add(mascota)
    db.commit()
    db.refresh(mascota)


def borrar(db: Session, mascota: Mascota) -> None:
    db.delete(mascota)
    db.commit()
