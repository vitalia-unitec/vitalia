from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tiempo import ahora_utc
from app.modules.categorias.models import Categoria

TIPOS_CLINICA = ("veterinaria", "hospital", "estetica", "hospedaje", "adiestramiento")


# Tipos de cada clínica, una fila por tipo
class ClinicaTipo(Base):
    __tablename__ = "clinica_tipos"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('veterinaria', 'hospital', 'estetica', 'hospedaje', 'adiestramiento')",
            name="ck_clinica_tipos_tipo",
        ),
    )

    clinica_id: Mapped[int] = mapped_column(
        ForeignKey("clinicas.id", ondelete="CASCADE"), primary_key=True
    )
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)


# Horarios, varios por día si hace falta
class Horario(Base):
    __tablename__ = "horarios"
    __table_args__ = (
        CheckConstraint("dia_semana BETWEEN 1 AND 7", name="ck_horarios_dia"),
        CheckConstraint("cierra > abre", name="ck_horarios_rango"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    clinica_id: Mapped[int] = mapped_column(
        ForeignKey("clinicas.id", ondelete="CASCADE"), index=True
    )
    dia_semana: Mapped[int] = mapped_column(Integer)
    abre: Mapped[time] = mapped_column(Time)
    cierra: Mapped[time] = mapped_column(Time)


# Servicios con precio
class ServicioClinica(Base):
    __tablename__ = "servicios_clinica"

    id: Mapped[int] = mapped_column(primary_key=True)
    clinica_id: Mapped[int] = mapped_column(
        ForeignKey("clinicas.id", ondelete="CASCADE"), index=True
    )
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500), default=None)
    precio: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False), default=None)
    es_precio_desde: Mapped[bool] = mapped_column(Boolean, default=False)

    categoria: Mapped[Categoria] = relationship(lazy="joined")


# Clínica
class Clinica(Base):
    __tablename__ = "clinicas"
    __table_args__ = (Index("ix_clinicas_lat_lng", "lat", "lng"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    propietario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str | None] = mapped_column(Text, default=None)

    calle: Mapped[str] = mapped_column(String(200))
    colonia: Mapped[str] = mapped_column(String(100))
    alcaldia_municipio: Mapped[str] = mapped_column(String(100))
    ciudad: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(100))
    codigo_postal: Mapped[str] = mapped_column(String(5))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)

    telefono: Mapped[str] = mapped_column(String(10))
    whatsapp: Mapped[str | None] = mapped_column(String(13), default=None)
    sitio_web: Mapped[str | None] = mapped_column(String(300), default=None)

    urgencias_24h: Mapped[bool] = mapped_column(Boolean, default=False)
    verificada: Mapped[bool] = mapped_column(Boolean, default=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    calificacion_prom: Mapped[float | None] = mapped_column(Float, default=None)
    total_resenas: Mapped[int] = mapped_column(Integer, default=0)

    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora_utc)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora_utc, onupdate=ahora_utc
    )

    tipos_rel: Mapped[list[ClinicaTipo]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by=ClinicaTipo.tipo
    )
    horarios: Mapped[list[Horario]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=(Horario.dia_semana, Horario.abre),
    )
    servicios: Mapped[list[ServicioClinica]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=(ServicioClinica.categoria_id, ServicioClinica.nombre),
    )

    @property
    def tipos(self) -> list[str]:
        return [t.tipo for t in self.tipos_rel]
