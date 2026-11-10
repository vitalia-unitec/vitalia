from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import Depends, Query

from app.core.errors import AppError
from app.modules.clinicas.schemas import TipoClinica

Latitud = Annotated[float | None, Query(ge=-90, le=90, description="Tu latitud")]
Longitud = Annotated[float | None, Query(ge=-180, le=180, description="Tu longitud")]
Orden = Literal["distancia", "calificacion", "resenas"]


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
    abierto_ahora: bool = False
    orden: str = "calificacion"

    @property
    def tiene_ubicacion(self) -> bool:
        return self.lat is not None and self.lng is not None

    def meta(self) -> dict:
        if not self.tiene_ubicacion:
            return {"lat": None, "lng": None, "radioKm": None}
        return {"lat": self.lat, "lng": self.lng, "radioKm": self.radio_km}


def leer_filtros(
    q: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
    tipo: Annotated[TipoClinica | None, Query()] = None,
    categoria: Annotated[str | None, Query(max_length=50)] = None,
    urgencias: bool = False,
    lat: Latitud = None,
    lng: Longitud = None,
    radio_km: Annotated[float, Query(alias="radioKm", ge=1, le=50)] = 5,
    abierto_ahora: Annotated[bool, Query(alias="abiertoAhora")] = False,
    orden: Annotated[Orden | None, Query()] = None,
) -> FiltrosBusqueda:
    revisar_ubicacion(lat, lng)
    con_ubicacion = lat is not None
    if orden == "distancia" and not con_ubicacion:
        raise AppError("VALIDACION", "Para ordenar por distancia envía lat y lng", 400)
    if orden is None:
        orden = "distancia" if con_ubicacion else "calificacion"
    return FiltrosBusqueda(
        q=q,
        tipo=tipo,
        categoria=categoria,
        urgencias=urgencias,
        lat=lat,
        lng=lng,
        radio_km=radio_km,
        abierto_ahora=abierto_ahora,
        orden=orden,
    )


ParametrosBusqueda = Annotated[FiltrosBusqueda, Depends(leer_filtros)]
