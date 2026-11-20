from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core import fotos
from app.core.config import get_settings
from app.core.errors import ArchivoInvalido

JPG = b"\xff\xd8\xff\xe0" + b"0" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 200
WEBP = b"RIFF" + b"0000" + b"WEBP" + b"0" * 200


def archivo(contenido: bytes, nombre: str = "foto.jpg") -> UploadFile:
    return UploadFile(file=BytesIO(contenido), filename=nombre)


@pytest.mark.parametrize(
    ("contenido", "extension"),
    [(JPG, "jpg"), (PNG, "png"), (WEBP, "webp"), (b"GIF89a" + b"0" * 50, None), (b"", None)],
    ids=["jpg", "png", "webp", "gif", "vacio"],
)
def test_detecta_el_formato_por_el_contenido(contenido, extension):
    assert fotos.detectar_extension(contenido) == extension


def test_guarda_la_foto_con_nombre_al_azar():
    primera = fotos.guardar_foto(archivo(JPG), "clinicas")
    segunda = fotos.guardar_foto(archivo(JPG), "clinicas")

    guardada = get_settings().fotos_ruta_absoluta / primera
    assert guardada.read_bytes() == JPG
    assert primera.startswith("clinicas/")
    assert primera.endswith(".jpg")
    assert primera != segunda


def test_la_extension_sale_del_contenido_y_no_del_nombre():
    ruta = fotos.guardar_foto(archivo(PNG, "../../truco.jpg.exe"), "mascotas")

    assert ruta.startswith("mascotas/")
    assert ruta.endswith(".png")
    assert "truco" not in ruta
    assert ".." not in ruta


@pytest.mark.parametrize(
    ("contenido", "mensaje"),
    [
        (b"", "vacía"),
        (b"<script>alert(1)</script>", "JPG, PNG o WebP"),
        (b"%PDF-1.7 documento", "JPG, PNG o WebP"),
        (JPG + b"0" * fotos.TAMANO_MAXIMO, "5 MB"),
    ],
    ids=["vacia", "html", "pdf", "mas-de-5-mb"],
)
def test_rechaza_archivos_invalidos(contenido, mensaje):
    with pytest.raises(ArchivoInvalido, match=mensaje) as error:
        fotos.guardar_foto(archivo(contenido), "clinicas")

    assert error.value.codigo == "ARCHIVO_INVALIDO"
    assert error.value.status_code == 400


def test_acepta_una_foto_de_justo_5_mb():
    contenido = JPG + b"0" * (fotos.TAMANO_MAXIMO - len(JPG))

    assert fotos.guardar_foto(archivo(contenido), "clinicas").endswith(".jpg")


def test_borra_la_foto_y_no_falla_si_ya_no_existe():
    ruta = fotos.guardar_foto(archivo(JPG), "clinicas")
    guardada = get_settings().fotos_ruta_absoluta / ruta

    fotos.borrar_foto(ruta)
    fotos.borrar_foto(ruta)
    fotos.borrar_foto(None)

    assert not guardada.exists()


def test_borrar_no_sale_de_la_carpeta_de_fotos(tmp_path):
    ajeno = tmp_path / "importante.txt"
    ajeno.write_text("no me borres")

    fotos.borrar_foto(f"../../../../../../../..{ajeno}")
    fotos.borrar_foto(str(ajeno))

    assert ajeno.exists()


def test_url_publica():
    assert fotos.url_publica("clinicas/ab12.jpg") == "http://testserver/fotos/clinicas/ab12.jpg"
    assert fotos.url_publica(None) is None


def test_en_local_la_api_sirve_las_fotos(client):
    ruta = fotos.guardar_foto(archivo(PNG), "clinicas")

    respuesta = client.get(f"/fotos/{ruta}")

    assert respuesta.status_code == 200
    assert respuesta.content == PNG
    assert respuesta.headers["content-type"] == "image/png"
