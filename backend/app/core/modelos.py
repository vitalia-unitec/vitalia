from app.core.database import Base, engine
from app.modules.usuarios import models as usuarios_models  # noqa: F401


def crear_tablas() -> None:
    Base.metadata.create_all(bind=engine)
