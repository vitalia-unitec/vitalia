import re
from datetime import datetime

from pydantic import EmailStr, Field, field_serializer, field_validator

from app.core.schemas import EsquemaBase
from app.core.tiempo import a_hora_local

PATRON_TELEFONO = r"^\d{10}$"


def validar_password(valor: str) -> str:
    if len(valor) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if len(valor.encode("utf-8")) > 72:
        raise ValueError("La contraseña es demasiado larga")
    if not re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", valor) or not re.search(r"\d", valor):
        raise ValueError("La contraseña debe tener al menos una letra y un número")
    return valor


class UsuarioSalida(EsquemaBase):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    rol: str
    creado_en: datetime

    @field_serializer("creado_en")
    def serializar_fecha(self, valor: datetime) -> str:
        return a_hora_local(valor).isoformat(timespec="seconds")


class ActualizarPerfil(EsquemaBase):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    telefono: str | None = Field(default=None, pattern=PATRON_TELEFONO)


class CambiarPassword(EsquemaBase):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def revisar_password(cls, valor: str) -> str:
        return validar_password(valor)
