import argparse
import csv
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.modelos import preparar_base
from app.modules.clinicas.models import Clinica
from app.modules.clinicas.schemas import ClinicaEntrada
from app.modules.clinicas.service import aplicar_datos

COLUMNAS = [
    "nombre",
    "tipos",
    "descripcion",
    "calle",
    "colonia",
    "alcaldia_municipio",
    "ciudad",
    "estado",
    "codigo_postal",
    "lat",
    "lng",
    "telefono",
    "whatsapp",
    "sitio_web",
    "urgencias_24h",
]
VALORES_SI = {"si", "sí", "true", "1", "x"}


# Leer el archivo; utf-8-sig acepta el CSV que guarda Excel
def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        faltantes = set(COLUMNAS) - set(lector.fieldnames or [])
        if faltantes:
            raise ValueError(f"Faltan columnas en el CSV: {', '.join(sorted(faltantes))}")
        return list(lector)


# Convertir una fila del CSV en los datos que valida la API
def fila_a_entrada(fila: dict[str, str]) -> ClinicaEntrada:
    def texto(columna: str) -> str | None:
        valor = (fila.get(columna) or "").strip()
        return valor or None

    return ClinicaEntrada.model_validate(
        {
            "nombre": texto("nombre"),
            "tipos": [t.strip().lower() for t in (texto("tipos") or "").split("|") if t.strip()],
            "descripcion": texto("descripcion"),
            "direccion": {
                "calle": texto("calle"),
                "colonia": texto("colonia"),
                "alcaldia_municipio": texto("alcaldia_municipio"),
                "ciudad": texto("ciudad"),
                "estado": texto("estado"),
                "codigo_postal": texto("codigo_postal"),
            },
            "lat": texto("lat"),
            "lng": texto("lng"),
            "telefono": texto("telefono"),
            "whatsapp": texto("whatsapp"),
            "sitio_web": texto("sitio_web"),
            "urgencias_24h": (texto("urgencias_24h") or "").lower() in VALORES_SI,
        }
    )


# Una clínica es la misma si coincide el nombre y el código postal
def ya_existe(db: Session, datos: ClinicaEntrada) -> bool: ...  # Lo escribes tú en el paso 2.4


def validar(filas: list[dict[str, str]]) -> tuple[list[ClinicaEntrada], list[str]]:
    validas, errores = [], []
    for numero, fila in enumerate(filas, start=2):
        try:
            validas.append(fila_a_entrada(fila))
        except ValidationError as error:
            for detalle in error.errors():
                campo = ".".join(str(parte) for parte in detalle["loc"])
                errores.append(f"Fila {numero}, {campo}: {detalle['msg']}")
    return validas, errores


def cargar(db: Session, clinicas: list[ClinicaEntrada]) -> tuple[int, int]:
    creadas = omitidas = 0
    for datos in clinicas:
        if ya_existe(db, datos):
            omitidas += 1
            continue
        clinica = Clinica(propietario_id=None, verificada=True)
        aplicar_datos(clinica, datos)
        db.add(clinica)
        db.flush()
        creadas += 1
    db.commit()
    return creadas, omitidas


def main() -> None:
    lector = argparse.ArgumentParser(description="Carga clínicas reales desde un CSV")
    lector.add_argument("archivo", type=Path, help="Ruta del CSV con las clínicas")
    opciones = lector.parse_args()

    try:
        filas = leer_csv(opciones.archivo)
    except (OSError, ValueError) as error:
        sys.exit(str(error))

    clinicas, errores = validar(filas)
    if errores:
        print("No se cargó nada. Corrige estos errores y vuelve a intentar:")
        print("\n".join(errores))
        sys.exit(1)

    preparar_base()
    with SessionLocal() as db:
        creadas, omitidas = cargar(db, clinicas)
    print(f"Clínicas creadas: {creadas}. Ya existían y se omitieron: {omitidas}")


if __name__ == "__main__":
    main()


def ya_existe(db: Session, datos: ClinicaEntrada) -> bool:
    consulta = select(Clinica.id).where(
        func.lower(Clinica.nombre) == datos.nombre.lower(),
        Clinica.codigo_postal == datos.direccion.codigo_postal,
    )
    return db.scalar(consulta) is not None
