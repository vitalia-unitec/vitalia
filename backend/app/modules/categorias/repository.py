from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.categorias.models import Categoria


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.id)))


def buscar_por_id(db: Session, categoria_id: int) -> Categoria | None:
    return db.get(Categoria, categoria_id)
