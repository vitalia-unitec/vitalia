from typing import Any


def ok(data: Any = None, meta: dict | None = None) -> dict:
    respuesta: dict[str, Any] = {"ok": True, "data": data}
    if meta is not None:
        respuesta["meta"] = meta
    return respuesta


def error(codigo: str, mensaje: str, detalles: list | None = None) -> dict:
    cuerpo: dict[str, Any] = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        cuerpo["detalles"] = detalles
    return {"ok": False, "error": cuerpo}
