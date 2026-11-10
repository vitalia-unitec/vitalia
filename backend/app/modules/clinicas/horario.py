from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol


class RangoHorario(Protocol):
    dia_semana: int
    abre: time
    cierra: time


@dataclass
class EstadoApertura:
    abierto: bool
    cierra_a: time | None = None
    abre_a: time | None = None


def _del_dia(horarios: Sequence[RangoHorario], dia: int) -> list[RangoHorario]:
    return sorted((h for h in horarios if h.dia_semana == dia), key=lambda h: h.abre)


def estado_apertura(
    horarios: Sequence[RangoHorario], urgencias_24h: bool, ahora: datetime
) -> EstadoApertura:
    if urgencias_24h:
        return EstadoApertura(abierto=True)

    hoy = ahora.isoweekday()
    hora = ahora.time().replace(second=0, microsecond=0)
    rangos_hoy = _del_dia(horarios, hoy)

    # ¿Está dentro de algún rango de hoy?
    for rango in rangos_hoy:
        if rango.abre <= hora < rango.cierra:
            return EstadoApertura(abierto=True, cierra_a=rango.cierra)

    # ¿Todavía abre más tarde hoy?
    for rango in rangos_hoy:
        if rango.abre > hora:
            return EstadoApertura(abierto=False, abre_a=rango.abre)

    # Primer horario de los siguientes días
    for dias_despues in range(1, 8):
        dia = (hoy - 1 + dias_despues) % 7 + 1
        rangos = _del_dia(horarios, dia)
        if rangos:
            return EstadoApertura(abierto=False, abre_a=rangos[0].abre)

    return EstadoApertura(abierto=False)
