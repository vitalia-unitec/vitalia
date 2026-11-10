import argparse
import random
import secrets
import sys
from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.modelos import crear_tablas
from app.core.security import hashear_password
from app.modules.clinicas.models import Clinica, ClinicaTipo, Horario, ServicioClinica
from app.modules.usuarios.models import Usuario

EMAIL_DEMO = "demo@vitalia.local"
CENTRO_LAT, CENTRO_LNG = 19.4326, -99.1332
DISPERSION_GRADOS = 0.35

TIPOS = ["veterinaria", "hospital", "estetica", "hospedaje", "adiestramiento"]
NOMBRES_POR_TIPO = {
    "veterinaria": "Veterinaria",
    "hospital": "Hospital",
    "estetica": "Estética",
    "hospedaje": "Hospedaje",
    "adiestramiento": "Adiestramiento",
}
COLONIAS = [
    ("Del Valle", "Benito Juárez"),
    ("Nápoles", "Benito Juárez"),
    ("Roma Norte", "Cuauhtémoc"),
    ("Condesa", "Cuauhtémoc"),
    ("Clavería", "Azcapotzalco"),
    ("Lindavista", "Gustavo A. Madero"),
    ("Coyoacán Centro", "Coyoacán"),
    ("Portales", "Benito Juárez"),
    ("Polanco", "Miguel Hidalgo"),
    ("Tacuba", "Miguel Hidalgo"),
]
SERVICIOS = [
    (1, "Consulta general", 350),
    (2, "Atención de urgencias", 900),
    (3, "Vacuna antirrábica", 250),
    (3, "Vacuna múltiple", 450),
    (4, "Esterilización", 1800),
    (5, "Desparasitación", 200),
    (6, "Rayos X", 700),
    (7, "Baño y corte", 400),
    (8, "Hospedaje por noche", 300),
    (9, "Clase de adiestramiento", 500),
    (10, "Hospitalización por día", 1200),
]


# Usuario dueño de todas las clínicas de demostración
def obtener_usuario_demo(db: Session) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == EMAIL_DEMO))
    if usuario is None:
        usuario = Usuario(
            nombre="Datos de demostración",
            email=EMAIL_DEMO,
            password_hash=hashear_password(secrets.token_urlsafe(24)),
            rol="clinica",
        )
        db.add(usuario)
        db.flush()
    return usuario


def borrar_demo(db: Session) -> int:
    usuario = db.scalar(select(Usuario).where(Usuario.email == EMAIL_DEMO))
    if usuario is None:
        return 0
    clinicas = list(db.scalars(select(Clinica).where(Clinica.propietario_id == usuario.id)))
    for clinica in clinicas:
        db.delete(clinica)
    db.commit()
    return len(clinicas)


# Armar una clínica ficticia
def _horarios(azar: random.Random) -> list[Horario]:
    if azar.random() < 0.05:
        return []
    horarios = []
    for dia in range(1, 6):
        if azar.random() < 0.3:
            horarios.append(Horario(dia_semana=dia, abre=time(9), cierra=time(14)))
            horarios.append(Horario(dia_semana=dia, abre=time(16), cierra=time(20)))
        else:
            horarios.append(Horario(dia_semana=dia, abre=time(9), cierra=time(19)))
    if azar.random() < 0.7:
        horarios.append(Horario(dia_semana=6, abre=time(10), cierra=time(14)))
    return horarios


def _servicios(azar: random.Random) -> list[ServicioClinica]:
    elegidos = azar.sample(SERVICIOS, k=azar.randint(2, 6))
    return [
        ServicioClinica(
            categoria_id=categoria_id,
            nombre=nombre,
            precio=precio + azar.choice([0, 50, 100]),
            es_precio_desde=azar.random() < 0.3,
        )
        for categoria_id, nombre, precio in elegidos
    ]


def _clinica(azar: random.Random, numero: int, propietario_id: int) -> Clinica:
    tipos = azar.sample(TIPOS, k=azar.choice([1, 1, 2]))
    colonia, alcaldia = azar.choice(COLONIAS)
    con_resenas = azar.random() < 0.8
    return Clinica(
        propietario_id=propietario_id,
        nombre=f"{NOMBRES_POR_TIPO[tipos[0]]} Demo {numero:04d}",
        descripcion="Clínica ficticia para pruebas y demostraciones. No existe.",
        calle=f"Calle Demo {numero}",
        colonia=colonia,
        alcaldia_municipio=alcaldia,
        ciudad="Ciudad de México",
        estado="CDMX",
        codigo_postal="00000",
        lat=round(CENTRO_LAT + azar.uniform(-DISPERSION_GRADOS, DISPERSION_GRADOS), 6),
        lng=round(CENTRO_LNG + azar.uniform(-DISPERSION_GRADOS, DISPERSION_GRADOS), 6),
        telefono=f"550000{numero:04d}",
        urgencias_24h=azar.random() < 0.1,
        verificada=False,
        calificacion_prom=round(azar.uniform(3.0, 5.0), 1) if con_resenas else None,
        total_resenas=azar.randint(1, 300) if con_resenas else 0,
        tipos_rel=[ClinicaTipo(tipo=tipo) for tipo in tipos],
        horarios=_horarios(azar),
        servicios=_servicios(azar),
    )


def sembrar(db: Session, cantidad: int, semilla: int = 2026) -> int:
    borrar_demo(db)
    if cantidad == 0:
        return 0
    azar = random.Random(semilla)
    usuario = obtener_usuario_demo(db)
    db.add_all(_clinica(azar, numero, usuario.id) for numero in range(1, cantidad + 1))
    db.commit()
    return cantidad


def main() -> None:
    lector = argparse.ArgumentParser(description="Crea clínicas ficticias de demostración")
    lector.add_argument("cantidad", type=int, help="Cuántas crear; 0 solo borra las que haya")
    lector.add_argument("--forzar", action="store_true", help="Permite correrlo fuera de local")
    opciones = lector.parse_args()

    if not 0 <= opciones.cantidad <= 5000:
        sys.exit("La cantidad debe estar entre 0 y 5000")
    if get_settings().app_entorno != "local" and not opciones.forzar:
        sys.exit("Este script solo corre con APP_ENTORNO=local; usa --forzar si estás seguro")

    crear_tablas()
    with SessionLocal() as db:
        creadas = sembrar(db, opciones.cantidad)
    print(f"Clínicas de demostración en la base: {creadas}")


if __name__ == "__main__":
    main()
