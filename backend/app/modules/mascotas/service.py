from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado
from app.modules.mascotas import repository
from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaEntrada
from app.modules.usuarios.models import Usuario

MAX_MASCOTAS = 10


def obtener_mia(db: Session, mascota_id: int, usuario: Usuario) -> Mascota:
    mascota = repository.obtener_de_dueno(db, mascota_id, usuario.id)
    if mascota is None:
        raise NoEncontrado("La mascota no existe")
    return mascota


def crear(db: Session, usuario: Usuario, datos: MascotaEntrada) -> Mascota:
    if repository.contar_de_dueno(db, usuario.id) >= MAX_MASCOTAS:
        raise Conflicto(f"Puedes registrar máximo {MAX_MASCOTAS} mascotas")
    mascota = Mascota(dueno_id=usuario.id, **datos.model_dump())
    repository.guardar(db, mascota)
    return mascota


def editar(db: Session, mascota: Mascota, datos: MascotaEntrada) -> Mascota:
    for campo, valor in datos.model_dump().items():
        setattr(mascota, campo, valor)
    repository.guardar(db, mascota)
    return mascota
