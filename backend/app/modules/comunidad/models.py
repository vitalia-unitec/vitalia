from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.core.database import Base
from app.core.tiempo import ahora_utc
from app.modules.usuarios.models import Usuario


# Comentarios de una publicación
class Comentario(Base):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    publicacion_id: Mapped[int] = mapped_column(
        ForeignKey("publicaciones.id", ondelete="CASCADE"), index=True
    )
    autor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    texto: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora_utc)

    autor: Mapped[Usuario | None] = relationship(lazy="joined")


# Publicaciones de la comunidad
class Publicacion(Base):
    __tablename__ = "publicaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    autor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    texto: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora_utc, index=True
    )
    editado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    autor: Mapped[Usuario | None] = relationship(lazy="joined")
    comentarios: Mapped[list[Comentario]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )

    total_comentarios: Mapped[int] = column_property(
        select(func.count(Comentario.id))
        .where(Comentario.publicacion_id == id)
        .correlate_except(Comentario)
        .scalar_subquery()
    )
