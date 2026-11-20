from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect

from app.core.database import Base, SessionLocal, engine
from app.modules.categorias.datos_iniciales import sembrar_categorias

RUTA_ALEMBIC = Path(__file__).resolve().parents[2] / "alembic.ini"


# Importa todos los modelos para que Base.metadata los conozca
def cargar_modelos() -> None:
    from app.modules.categorias import models as categorias_models  # noqa: F401
    from app.modules.clinicas import models as clinicas_models  # noqa: F401
    from app.modules.comunidad import models as comunidad_models  # noqa: F401
    from app.modules.mascotas import models as mascotas_models  # noqa: F401
    from app.modules.resenas import models as resenas_models  # noqa: F401
    from app.modules.usuarios import models as usuarios_models  # noqa: F401


def config_alembic() -> Config:
    config = Config(str(RUTA_ALEMBIC))
    config.attributes["sin_logs"] = True
    return config


# Lleva la base a la última migración
def migrar() -> None:
    cargar_modelos()
    config = config_alembic()
    with engine.connect() as conexion:
        tablas = set(inspect(conexion).get_table_names())
        version = MigrationContext.configure(conexion).get_current_revision()

    if "usuarios" in tablas and version is None:
        # Base creada antes de Alembic: se completa y se marca como al día
        Base.metadata.create_all(bind=engine)
        command.stamp(config, "head")
    else:
        command.upgrade(config, "head")


def preparar_base() -> None:
    migrar()
    with SessionLocal() as db:
        sembrar_categorias(db)


# Solo para pruebas: crea las tablas directo desde los modelos
def crear_tablas() -> None:
    cargar_modelos()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        sembrar_categorias(db)
