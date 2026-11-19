from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.core.database import Base
from app.core.modelos import cargar_modelos, config_alembic


def test_las_migraciones_crean_lo_mismo_que_los_modelos(tmp_path):
    cargar_modelos()
    motor = create_engine(f"sqlite:///{(tmp_path / 'nueva.db').as_posix()}")
    config = config_alembic()

    with motor.begin() as conexion:
        config.attributes["conexion"] = conexion
        command.upgrade(config, "head")
        diferencias = compare_metadata(MigrationContext.configure(conexion), Base.metadata)
    motor.dispose()

    assert diferencias == [], "Cambiaste un modelo sin generar su migración"


def test_downgrade_deja_la_base_vacia(tmp_path):
    cargar_modelos()
    motor = create_engine(f"sqlite:///{(tmp_path / 'vacia.db').as_posix()}")
    config = config_alembic()

    with motor.begin() as conexion:
        config.attributes["conexion"] = conexion
        command.upgrade(config, "head")
        command.downgrade(config, "base")
        tablas = inspect(conexion).get_table_names()
    motor.dispose()

    assert tablas == ["alembic_version"]
