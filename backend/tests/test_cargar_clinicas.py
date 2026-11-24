import pytest

from app.core.database import SessionLocal
from scripts.cargar_clinicas import COLUMNAS, cargar, leer_csv, validar

PATITAS = {
    "nombre": "Clínica Veterinaria Patitas",
    "tipos": "veterinaria|estetica",
    "descripcion": "Atención para perros y gatos",
    "calle": "Av. Insurgentes 123",
    "colonia": "Del Valle",
    "alcaldia_municipio": "Benito Juárez",
    "ciudad": "Ciudad de México",
    "estado": "CDMX",
    "codigo_postal": "03100",
    "lat": "19.3801",
    "lng": "-99.1702",
    "telefono": "5598765432",
    "whatsapp": "",
    "sitio_web": "",
    "urgencias_24h": "sí",
}


def escribir_csv(ruta, filas: list[dict], con_bom: bool = False) -> None:
    lineas = [",".join(COLUMNAS)]
    for fila in filas:
        lineas.append(",".join(f'"{fila.get(c, "")}"' for c in COLUMNAS))
    ruta.write_text("\n".join(lineas), encoding="utf-8-sig" if con_bom else "utf-8")


def cargar_archivo(ruta) -> tuple[int, int]:
    clinicas, errores = validar(leer_csv(ruta))
    assert errores == []
    with SessionLocal() as db:
        return cargar(db, clinicas)


def test_carga_clinicas_verificadas_y_visibles_en_busqueda(client, tmp_path):
    archivo = tmp_path / "clinicas.csv"
    escribir_csv(archivo, [PATITAS], con_bom=True)

    assert cargar_archivo(archivo) == (1, 0)

    resultado = client.get("/api/v1/clinicas", params={"q": "patitas"}).json()["data"]
    assert len(resultado) == 1
    assert resultado[0]["verificada"] is True
    assert resultado[0]["urgencias24h"] is True
    assert sorted(resultado[0]["tipos"]) == ["estetica", "veterinaria"]


def test_volver_a_cargar_no_duplica(client, tmp_path):
    archivo = tmp_path / "clinicas.csv"
    escribir_csv(archivo, [PATITAS])
    cargar_archivo(archivo)

    assert cargar_archivo(archivo) == (0, 1)


def test_volver_a_cargar_no_duplica_nombres_con_mayusculas_acentuadas(client, tmp_path):
    archivo = tmp_path / "clinicas.csv"
    escribir_csv(archivo, [{**PATITAS, "nombre": "Veterinaria San Ángel"}])
    cargar_archivo(archivo)

    assert cargar_archivo(archivo) == (0, 1)


def test_una_fila_mala_reporta_su_numero(client, tmp_path):
    archivo = tmp_path / "clinicas.csv"
    escribir_csv(archivo, [PATITAS, {**PATITAS, "nombre": "Otra", "telefono": "123"}])

    clinicas, errores = validar(leer_csv(archivo))

    assert len(clinicas) == 1
    assert len(errores) == 1
    assert errores[0].startswith("Fila 3, telefono")


def test_falta_una_columna(tmp_path):
    archivo = tmp_path / "clinicas.csv"
    archivo.write_text("nombre,tipos\nPatitas,veterinaria", encoding="utf-8")

    with pytest.raises(ValueError, match="Faltan columnas"):
        leer_csv(archivo)
