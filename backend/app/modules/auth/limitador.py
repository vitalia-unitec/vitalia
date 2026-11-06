from collections import defaultdict, deque
from threading import Lock
from time import monotonic

MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60


class LimitadorLogin:
    def __init__(self, max_intentos: int = MAX_INTENTOS, ventana: int = VENTANA_SEGUNDOS):
        self.max_intentos = max_intentos
        self.ventana = ventana
        self._fallos: dict[str, deque[float]] = defaultdict(deque)
        self._candado = Lock()

    def _limpiar(self, clave: str, ahora: float) -> deque[float]:
        fallos = self._fallos[clave]
        while fallos and ahora - fallos[0] > self.ventana:
            fallos.popleft()
        return fallos

    def bloqueado(self, clave: str) -> bool:
        with self._candado:
            return len(self._limpiar(clave, monotonic())) >= self.max_intentos

    def registrar_fallo(self, clave: str) -> None:
        with self._candado:
            ahora = monotonic()
            self._limpiar(clave, ahora).append(ahora)

    def reiniciar(self, clave: str | None = None) -> None:
        with self._candado:
            if clave is None:
                self._fallos.clear()
            else:
                self._fallos.pop(clave, None)


limitador_login = LimitadorLogin()
