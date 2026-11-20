from datetime import datetime

from pydantic import Field, field_serializer, field_validator

from app.core.schemas import EsquemaBase
from app.core.tiempo import a_hora_local
from app.modules.usuarios.schemas import AutorSalida


class ResenaEntrada(EsquemaBase):
    calificacion: int = Field(ge=1, le=5)
    comentario: str | None = Field(default=None, max_length=1000)

    @field_validator("comentario")
    @classmethod
    def vacio_es_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class ResenaSalida(EsquemaBase):
    id: int
    calificacion: int
    comentario: str | None
    autor: AutorSalida
    es_mia: bool | None
    creado_en: datetime
    editado_en: datetime | None

    @field_serializer("creado_en", "editado_en")
    def serializar_fecha(self, valor: datetime | None) -> str | None:
        return a_hora_local(valor).isoformat(timespec="seconds") if valor else None
