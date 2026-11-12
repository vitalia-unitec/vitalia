from sqlalchemy.orm import Session

from app.core.errors import AppError, Conflicto, NoEncontrado
from app.modules.clinicas.models import Clinica
from app.modules.mascotas import mensaje, repository
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


def armar_mensaje_whatsapp(mascota: Mascota, clinica: Clinica) -> dict:
    if not clinica.whatsapp:
        raise AppError("VALIDACION", "Esta clínica no tiene WhatsApp registrado", 400)

    texto = mensaje.armar_texto(
        clinica=clinica.nombre,
        nombre=mascota.nombre,
        especie=mascota.especie,
        sexo=mascota.sexo,
        raza=mascota.raza,
        edad_anios=mascota.edad_anios,
        edad_meses=mascota.edad_meses,
        color=mascota.color,
    )
    return {"texto": texto, "url": mensaje.armar_url(clinica.whatsapp, texto)}
