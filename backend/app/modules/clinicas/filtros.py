from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query

from app.modules.clinicas.schemas import TipoClinica


@dataclass
class FiltrosBusqueda:
    q: str | None = None
    tipo: str | None = None
    categoria: str | None = None
    urgencias: bool = False


def leer_filtros(
    q: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
    tipo: Annotated[TipoClinica | None, Query()] = None,
    categoria: Annotated[str | None, Query(max_length=50)] = None,
    urgencias: bool = False,
) -> FiltrosBusqueda:
    return FiltrosBusqueda(q=q, tipo=tipo, categoria=categoria, urgencias=urgencias)


ParametrosBusqueda = Annotated[FiltrosBusqueda, Depends(leer_filtros)]
