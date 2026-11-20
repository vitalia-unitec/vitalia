from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tiempo import ahora_utc
from app.modules.usuarios.models import Usuario


class Resena(Base):
    __tablename__ = "resenas"
    __table_args__ = (
        CheckConstraint("calificacion BETWEEN 1 AND 5", name="ck_resenas_calificacion"),
        UniqueConstraint("clinica_id", "autor_id", name="uq_resenas_clinica_autor"),
        Index("ix_resenas_clinica_fecha", "clinica_id", "creado_en"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    clinica_id: Mapped[int] = mapped_column(ForeignKey("clinicas.id", ondelete="CASCADE"))
    autor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    calificacion: Mapped[int] = mapped_column(Integer)
    comentario: Mapped[str | None] = mapped_column(Text, default=None)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora_utc)
    editado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    autor: Mapped[Usuario | None] = relationship(lazy="joined")
