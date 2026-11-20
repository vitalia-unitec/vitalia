from app.core.schemas import EsquemaBase


class CategoriaSalida(EsquemaBase):
    id: int
    nombre: str
    slug: str
    icono: str
