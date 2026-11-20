from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.tiempo import ahora_utc

ROLES = ("dueno", "clinica", "admin")


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("rol IN ('dueno', 'clinica', 'admin')", name="ck_usuarios_rol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(10), default=None)
    rol: Mapped[str] = mapped_column(String(10))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora_utc)
