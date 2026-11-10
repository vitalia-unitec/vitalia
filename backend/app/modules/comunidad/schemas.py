from datetime import datetime

from pydantic import Field, field_serializer

from app.core.schemas import EsquemaBase
from app.core.tiempo import a_hora_local
from app.modules.usuarios.models import Usuario


def _fecha(valor: datetime | None) -> str | None:
    return a_hora_local(valor).isoformat(timespec="seconds") if valor else None


class AutorSalida(EsquemaBase):
    id: int | None
    nombre: str

    @classmethod
    def desde_usuario(cls, usuario: Usuario | None) -> "AutorSalida":
        if usuario is None:
            return cls(id=None, nombre="Usuario eliminado")
        partes = usuario.nombre.split()
        nombre = partes[0] if len(partes) == 1 else f"{partes[0]} {partes[1][0]}."
        return cls(id=usuario.id, nombre=nombre)


# Entradas
class PublicacionEntrada(EsquemaBase):
    texto: str = Field(min_length=1, max_length=2000)


class ComentarioEntrada(EsquemaBase):
    texto: str = Field(min_length=1, max_length=1000)


# Salidas
class PublicacionSalida(EsquemaBase):
    id: int
    autor: AutorSalida
    texto: str
    fotos: list[dict]
    total_comentarios: int
    es_mia: bool | None
    creado_en: datetime
    editado_en: datetime | None

    @field_serializer("creado_en", "editado_en")
    def serializar_fecha(self, valor: datetime | None) -> str | None:
        return _fecha(valor)


class ComentarioSalida(EsquemaBase):
    id: int
    autor: AutorSalida
    texto: str
    es_mio: bool | None
    creado_en: datetime

    @field_serializer("creado_en")
    def serializar_fecha(self, valor: datetime) -> str | None:
        return _fecha(valor)
