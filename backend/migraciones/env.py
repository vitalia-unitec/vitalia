from logging.config import fileConfig

from alembic import context

from app.core.database import Base, engine
from app.core.modelos import cargar_modelos

config = context.config

# Logs de Alembic solo cuando se usa desde la terminal
if config.config_file_name is not None and not config.attributes.get("sin_logs"):
    fileConfig(config.config_file_name)

cargar_modelos()
target_metadata = Base.metadata


def correr_migraciones() -> None:
    conexion = config.attributes.get("conexion")
    if conexion is not None:
        _migrar_con(conexion)
        return
    with engine.connect() as conexion:
        _migrar_con(conexion)


def _migrar_con(conexion) -> None:
    context.configure(
        connection=conexion,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


correr_migraciones()
