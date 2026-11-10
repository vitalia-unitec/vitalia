from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query

from app.core.errors import AppError
from app.modules.clinicas.schemas import TipoClinica

Latitud = Annotated[float | None, Query(ge=-90, le=90, description="Tu latitud")]
Longitud = Annotated[float | None, Query(ge=-180, le=180, description="Tu longitud")]


def revisar_ubicacion(lat: float | None, lng: float | None) -> None:
    if (lat is None) != (lng is None):
        raise AppError("VALIDACION", "lat y lng deben enviarse juntos", 400)


@dataclass
class FiltrosBusqueda:
    q: str | None = None
    tipo: str | None = None
    categoria: str | None = None
    urgencias: bool = False
    lat: float | None = None
    lng: float | None = None
    radio_km: float = 5

    @property
    def tiene_ubicacion(self) -> bool:
        return self.lat is not None and self.lng is not None


def leer_filtros(
    q: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
    tipo: Annotated[TipoClinica | None, Query()] = None,
    categoria: Annotated[str | None, Query(max_length=50)] = None,
    urgencias: bool = False,
    lat: Latitud = None,
    lng: Longitud = None,
    radio_km: Annotated[float, Query(alias="radioKm", ge=1, le=50)] = 5,
) -> FiltrosBusqueda:
    revisar_ubicacion(lat, lng)
    return FiltrosBusqueda(
        q=q,
        tipo=tipo,
        categoria=categoria,
        urgencias=urgencias,
        lat=lat,
        lng=lng,
        radio_km=radio_km,
    )


ParametrosBusqueda = Annotated[FiltrosBusqueda, Depends(leer_filtros)]
