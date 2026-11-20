from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.modules.clinicas.horario import estado_apertura

CDMX = ZoneInfo("America/Mexico_City")


@dataclass
class Rango:
    dia_semana: int
    abre: time
    cierra: time


# Lunes de 9 a 14 y de 16 a 20, sábado de 10 a 15
SEMANA = [
    Rango(1, time(9), time(14)),
    Rango(1, time(16), time(20)),
    Rango(6, time(10), time(15)),
]


def lunes(hora: int, minuto: int = 0) -> datetime:
    return datetime(2026, 11, 2, hora, minuto, tzinfo=CDMX)


def test_abierta_dentro_de_un_rango():
    estado = estado_apertura(SEMANA, False, lunes(10))

    assert estado.abierto is True
    assert estado.cierra_a == time(14)


def test_en_la_hora_exacta_de_cierre_ya_esta_cerrada():
    estado = estado_apertura(SEMANA, False, lunes(14))

    assert estado.abierto is False
    assert estado.abre_a == time(16)


def test_cerrada_entre_dos_rangos_dice_cuando_vuelve_a_abrir():
    estado = estado_apertura(SEMANA, False, lunes(15, 30))

    assert estado.abierto is False
    assert estado.abre_a == time(16)


def test_cerrada_en_la_noche_busca_el_siguiente_dia_con_horario():
    estado = estado_apertura(SEMANA, False, lunes(21))

    assert estado.abierto is False
    assert estado.abre_a == time(10)


def test_urgencias_24h_siempre_abierta():
    estado = estado_apertura([], True, lunes(3))

    assert estado.abierto is True
    assert estado.cierra_a is None


def test_sin_horarios_esta_cerrada_sin_hora_de_apertura():
    estado = estado_apertura([], False, lunes(10))

    assert estado.abierto is False
    assert estado.abre_a is None
