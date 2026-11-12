from datetime import time
from typing import Literal

from pydantic import (
    Field,
    HttpUrl,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.core.schemas import EsquemaBase
from app.modules.categorias.schemas import CategoriaSalida

TipoClinica = Literal["veterinaria", "hospital", "estetica", "hospedaje", "adiestramiento"]
DIAS = ["", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _hhmm(valor: time | None) -> str | None:
    return valor.strftime("%H:%M") if valor else None


# Dirección
class DireccionEntrada(EsquemaBase):
    calle: str = Field(min_length=3, max_length=200)
    colonia: str = Field(min_length=2, max_length=100)
    alcaldia_municipio: str = Field(min_length=2, max_length=100)
    ciudad: str = Field(min_length=2, max_length=100)
    estado: str = Field(min_length=2, max_length=100)
    codigo_postal: str = Field(pattern=r"^\d{5}$")


class DireccionSalida(DireccionEntrada):
    @computed_field
    @property
    def texto_completo(self) -> str:
        return (
            f"{self.calle}, Col. {self.colonia}, {self.alcaldia_municipio}, "
            f"{self.codigo_postal} {self.ciudad}, {self.estado}"
        )


# Clínica, lo que manda el panel de negocio
class ClinicaEntrada(EsquemaBase):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, max_length=1000)
    tipos: list[TipoClinica] = Field(min_length=1, max_length=5)
    direccion: DireccionEntrada
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    telefono: str = Field(pattern=r"^\d{10}$")
    whatsapp: str | None = Field(default=None, pattern=r"^\d{10,13}$")
    sitio_web: HttpUrl | None = None
    urgencias_24h: bool = False

    @field_validator("tipos")
    @classmethod
    def quitar_repetidos(cls, valor: list[str]) -> list[str]:
        return list(dict.fromkeys(valor))


# Horarios
class HorarioEntrada(EsquemaBase):
    dia_semana: int = Field(ge=1, le=7)
    abre: time
    cierra: time

    @model_validator(mode="after")
    def revisar_rango(self) -> "HorarioEntrada":
        if self.cierra <= self.abre:
            raise ValueError("La hora de cierre debe ser mayor que la de apertura")
        return self


class HorariosEntrada(EsquemaBase):
    horarios: list[HorarioEntrada] = Field(max_length=21)

    @model_validator(mode="after")
    def revisar_encimados(self) -> "HorariosEntrada":
        ordenados = sorted(self.horarios, key=lambda h: (h.dia_semana, h.abre))
        for anterior, actual in zip(ordenados, ordenados[1:], strict=False):
            if anterior.dia_semana == actual.dia_semana and actual.abre < anterior.cierra:
                raise ValueError(f"Los horarios del {DIAS[actual.dia_semana]} se enciman")
        return self


class HorarioSalida(EsquemaBase):
    dia_semana: int
    abre: time
    cierra: time

    @field_serializer("abre", "cierra")
    def serializar_hora(self, valor: time) -> str:
        return valor.strftime("%H:%M")


# Servicios
class ServicioEntrada(EsquemaBase):
    categoria_id: int = Field(ge=1)
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: float | None = Field(default=None, ge=0, le=1_000_000)
    es_precio_desde: bool = False

    @model_validator(mode="after")
    def sin_precio_no_es_desde(self) -> "ServicioEntrada":
        if self.precio is None:
            self.es_precio_desde = False
        return self


class ServicioSalida(EsquemaBase):
    id: int
    categoria: CategoriaSalida
    nombre: str
    descripcion: str | None
    precio: float | None
    es_precio_desde: bool


# Salidas de clínica
class ClinicaResumenSalida(EsquemaBase):
    id: int
    nombre: str
    tipos: list[str]
    calificacion: float | None
    total_resenas: int
    distancia_km: float | None
    abierto: bool
    cierra_a: time | None
    abre_a: time | None
    urgencias_24h: bool
    verificada: bool
    foto_principal: str | None
    servicios_destacados: list[str]
    lat: float
    lng: float

    @field_serializer("cierra_a", "abre_a")
    def serializar_hora(self, valor: time | None) -> str | None:
        return _hhmm(valor)


# Fotos
class FotoSalida(EsquemaBase):
    id: int
    url: str
    orden: int


class OrdenFotosEntrada(EsquemaBase):
    ids: list[int] = Field(min_length=1, max_length=10)


class ClinicaDetalleSalida(ClinicaResumenSalida):
    descripcion: str | None
    direccion: DireccionSalida
    telefono: str
    whatsapp: str | None
    sitio_web: str | None
    horarios: list[HorarioSalida]
    fotos: list[FotoSalida]
    servicios: list[ServicioSalida]


class ClinicaNegocioSalida(ClinicaDetalleSalida):
    activa: bool
