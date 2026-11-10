from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.clinicas.models import Clinica


def obtener(db: Session, clinica_id: int) -> Clinica | None:
    return db.get(Clinica, clinica_id)


def listar_activas(db: Session) -> list[Clinica]:
    consulta = select(Clinica).where(Clinica.activa.is_(True))
    return list(db.scalars(consulta))


def listar_de_propietario(db: Session, propietario_id: int) -> list[Clinica]:
    consulta = select(Clinica).where(Clinica.propietario_id == propietario_id).order_by(Clinica.id)
    return list(db.scalars(consulta))


def contar_activas_de(db: Session, propietario_id: int) -> int:
    consulta = select(func.count(Clinica.id)).where(
        Clinica.propietario_id == propietario_id, Clinica.activa.is_(True)
    )
    return db.scalar(consulta) or 0


def guardar(db: Session, objeto: object) -> None:
    db.add(objeto)
    db.commit()
    db.refresh(objeto)
