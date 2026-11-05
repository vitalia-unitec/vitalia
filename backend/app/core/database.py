from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Archivo de la base
ruta_bd = settings.db_ruta_absoluta
ruta_bd.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{ruta_bd.as_posix()}",
    connect_args={"check_same_thread": False, "timeout": 5},
)


# Ajustes de SQLite en cada conexión
@event.listens_for(engine, "connect")
def configurar_sqlite(conexion, _registro) -> None:
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA busy_timeout = 5000")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Base para los modelos
class Base(DeclarativeBase):
    pass


# Dependencia para los endpoints
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSesion = Annotated[Session, Depends(get_db)]
