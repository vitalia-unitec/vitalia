from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.usuarios.models import Usuario


def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email.lower()))


def crear(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def guardar(db: Session, usuario: Usuario) -> Usuario:
    db.commit()
    db.refresh(usuario)
    return usuario


def borrar(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()
