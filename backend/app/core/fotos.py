import secrets
from pathlib import Path
from typing import Annotated

from fastapi import File, UploadFile

from app.core.config import get_settings
from app.core.errors import ArchivoInvalido

TAMANO_MAXIMO = 5 * 1024 * 1024

# Archivo que llega en el campo foto de un formulario multipart
ArchivoFoto = Annotated[UploadFile, File(alias="foto", description="JPG, PNG o WebP de hasta 5 MB")]


# El formato se decide por los primeros bytes del archivo, no por su nombre
def detectar_extension(contenido: bytes) -> str | None:
    if contenido.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return "webp"
    return None


def _carpeta_base() -> Path:
    return get_settings().fotos_ruta_absoluta


# Guarda la foto con un nombre al azar y regresa su ruta relativa, como clinicas/ab12.jpg
def guardar_foto(archivo: UploadFile, carpeta: str) -> str:
    contenido = archivo.file.read(TAMANO_MAXIMO + 1)
    if not contenido:
        raise ArchivoInvalido("La foto está vacía")
    if len(contenido) > TAMANO_MAXIMO:
        raise ArchivoInvalido("La foto no puede pesar más de 5 MB")

    extension = detectar_extension(contenido)
    if extension is None:
        raise ArchivoInvalido("La foto debe ser JPG, PNG o WebP")

    destino = _carpeta_base() / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    nombre = f"{secrets.token_hex(16)}.{extension}"
    (destino / nombre).write_bytes(contenido)
    return f"{carpeta}/{nombre}"


def borrar_foto(ruta: str | None) -> None:
    if not ruta:
        return
    base = _carpeta_base()
    archivo = (base / ruta).resolve()
    if archivo.is_relative_to(base):
        archivo.unlink(missing_ok=True)


def url_publica(ruta: str | None) -> str | None:
    if not ruta:
        return None
    return f"{get_settings().fotos_url_base.rstrip('/')}/{ruta}"
