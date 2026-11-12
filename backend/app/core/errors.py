import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.responses import error

logger = logging.getLogger("vitalia")


# Errores propios de la aplicación
class AppError(Exception):
    def __init__(self, codigo: str, mensaje: str, status_code: int = 400):
        self.codigo = codigo
        self.mensaje = mensaje
        self.status_code = status_code
        super().__init__(mensaje)


class NoEncontrado(AppError):
    def __init__(self, mensaje: str = "Recurso no encontrado"):
        super().__init__("NO_ENCONTRADO", mensaje, 404)


class NoAutenticado(AppError):
    def __init__(self, mensaje: str = "Necesitas iniciar sesión"):
        super().__init__("NO_AUTENTICADO", mensaje, 401)


class SinPermiso(AppError):
    def __init__(self, mensaje: str = "No tienes permiso para esta acción"):
        super().__init__("SIN_PERMISO", mensaje, 403)


class Conflicto(AppError):
    def __init__(self, mensaje: str = "El recurso ya existe"):
        super().__init__("CONFLICTO", mensaje, 409)


class TokenInvalido(AppError):
    def __init__(self, mensaje: str = "Tu sesión no es válida o ya venció"):
        super().__init__("TOKEN_INVALIDO", mensaje, 401)


class CredencialesInvalidas(AppError):
    def __init__(self, mensaje: str = "Correo o contraseña incorrectos"):
        super().__init__("CREDENCIALES_INVALIDAS", mensaje, 401)


class DemasiadasPeticiones(AppError):
    def __init__(self, mensaje: str = "Demasiados intentos, espera unos minutos"):
        super().__init__("DEMASIADAS_PETICIONES", mensaje, 429)


class ArchivoInvalido(AppError):
    def __init__(self, mensaje: str = "El archivo no es una foto válida"):
        super().__init__("ARCHIVO_INVALIDO", mensaje, 400)


# Manejadores globales
def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def manejar_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error(exc.codigo, exc.mensaje))

    @app.exception_handler(RequestValidationError)
    async def manejar_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        detalles = [
            {
                "campo": ".".join(str(p) for p in e["loc"][1:]),
                "mensaje": e["msg"].removeprefix("Value error, "),
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=error("VALIDACION", "Los datos enviados no son válidos", detalles),
        )

    @app.exception_handler(StarletteHTTPException)
    async def manejar_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        codigos = {404: "NO_ENCONTRADO", 405: "METODO_NO_PERMITIDO"}
        codigo = codigos.get(exc.status_code, f"HTTP_{exc.status_code}")
        return JSONResponse(status_code=exc.status_code, content=error(codigo, str(exc.detail)))

    @app.exception_handler(Exception)
    async def manejar_inesperado(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no controlado: %s", exc)
        return JSONResponse(
            status_code=500,
            content=error("ERROR_INTERNO", "Ocurrió un error inesperado"),
        )
