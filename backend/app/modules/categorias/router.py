from fastapi import APIRouter

from app.core.database import DbSesion
from app.core.responses import ok
from app.modules.categorias import repository
from app.modules.categorias.schemas import CategoriaSalida

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", summary="Catálogo de categorías de servicios")
def listar_categorias(db: DbSesion) -> dict:
    categorias = repository.listar(db)
    return ok([CategoriaSalida.model_validate(c).a_json() for c in categorias])
