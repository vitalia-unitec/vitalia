from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.categorias.models import Categoria

CATEGORIAS = [
    ("Consulta general", "consulta-general", "stethoscope"),
    ("Urgencias", "urgencias", "siren"),
    ("Vacunas", "vacunas", "syringe"),
    ("Cirugía", "cirugia", "scissors"),
    ("Desparasitación", "desparasitacion", "pill"),
    ("Rayos X", "rayos-x", "scan"),
    ("Estética", "estetica", "sparkles"),
    ("Hospedaje", "hospedaje", "home"),
    ("Adiestramiento", "adiestramiento", "graduation-cap"),
    ("Hospitalización", "hospitalizacion", "bed"),
]


def sembrar_categorias(db: Session) -> None:
    if db.scalar(select(func.count(Categoria.id))):
        return
    db.add_all(Categoria(nombre=n, slug=s, icono=i) for n, s, i in CATEGORIAS)
    db.commit()
