from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.tiempo import ahora_utc

ESPECIES = ("perro", "gato", "ave", "conejo", "reptil", "otro")
SEXOS = ("macho", "hembra")


class Mascota(Base):
    __tablename__ = "mascotas"
    __table_args__ = (
        CheckConstraint(
            "especie IN ('perro', 'gato', 'ave', 'conejo', 'reptil', 'otro')",
            name="ck_mascotas_especie",
        ),
        CheckConstraint("sexo IN ('macho', 'hembra')", name="ck_mascotas_sexo"),
        CheckConstraint("edad_anios BETWEEN 0 AND 40", name="ck_mascotas_edad_anios"),
        CheckConstraint("edad_meses BETWEEN 0 AND 11", name="ck_mascotas_edad_meses"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dueno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(50))
    especie: Mapped[str] = mapped_column(String(10))
    raza: Mapped[str | None] = mapped_column(String(60), default=None)
    sexo: Mapped[str] = mapped_column(String(10))
    edad_anios: Mapped[int | None] = mapped_column(Integer, default=None)
    edad_meses: Mapped[int | None] = mapped_column(Integer, default=None)
    color: Mapped[str | None] = mapped_column(String(40), default=None)
    foto_url: Mapped[str | None] = mapped_column(String(300), default=None)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora_utc)
