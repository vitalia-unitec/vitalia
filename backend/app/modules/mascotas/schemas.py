from typing import Literal

from pydantic import Field, field_validator

from app.core.schemas import EsquemaBase

Especie = Literal["perro", "gato", "ave", "conejo", "reptil", "otro"]
Sexo = Literal["macho", "hembra"]


class MascotaEntrada(EsquemaBase):
    nombre: str = Field(min_length=1, max_length=50)
    especie: Especie
    raza: str | None = Field(default=None, max_length=60)
    sexo: Sexo
    edad_anios: int | None = Field(default=None, ge=0, le=40)
    edad_meses: int | None = Field(default=None, ge=0, le=11)
    color: str | None = Field(default=None, max_length=40)

    @field_validator("raza", "color")
    @classmethod
    def vacio_es_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class MascotaSalida(EsquemaBase):
    id: int
    nombre: str
    especie: str
    raza: str | None
    sexo: str
    edad_anios: int | None
    edad_meses: int | None
    color: str | None
    foto_url: str | None
