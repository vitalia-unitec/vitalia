from app.core.database import Base, SessionLocal, engine
from app.modules.categorias import models as categorias_models  # noqa: F401
from app.modules.categorias.datos_iniciales import sembrar_categorias
from app.modules.clinicas import models as clinicas_models  # noqa: F401
from app.modules.comunidad import models as comunidad_models  # noqa: F401
from app.modules.usuarios import models as usuarios_models  # noqa: F401


def crear_tablas() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        sembrar_categorias(db)
