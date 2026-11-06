from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, field_serializer, field_validator

from app.core.schemas import EsquemaBase
from app.core.tiempo import a_hora_local
from app.modules.usuarios.schemas import PATRON_TELEFONO, UsuarioSalida, validar_password


class RegistroEntrada(EsquemaBase):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str
    telefono: str | None = Field(default=None, pattern=PATRON_TELEFONO)
    rol: Literal["dueno", "clinica"]

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.lower()

    @field_validator("password")
    @classmethod
    def revisar_password(cls, valor: str) -> str:
        return validar_password(valor)


class LoginEntrada(EsquemaBase):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.lower()


class SesionSalida(EsquemaBase):
    token: str
    expira_en: datetime
    usuario: UsuarioSalida

    @field_serializer("expira_en")
    def serializar_fecha(self, valor: datetime) -> str:
        return a_hora_local(valor).isoformat(timespec="seconds")
