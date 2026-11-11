from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto
from app.modules.clinicas.models import Clinica
from app.modules.resenas import repository
from app.modules.resenas.models import Resena
from app.modules.resenas.schemas import ResenaEntrada, ResenaSalida
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import AutorSalida

MENSAJE_REPETIDA = "Ya dejaste una reseña en esta clínica; puedes editarla"


# Armar la respuesta
def armar_resena(resena: Resena, usuario: Usuario | None) -> dict:
    return ResenaSalida(
        id=resena.id,
        calificacion=resena.calificacion,
        comentario=resena.comentario,
        autor=AutorSalida.desde_usuario(resena.autor),
        es_mia=None if usuario is None else resena.autor_id == usuario.id,
        creado_en=resena.creado_en,
        editado_en=resena.editado_en,
    ).a_json()


# Mantener al día la calificación de la clínica
def recalcular_calificacion(db: Session, clinica: Clinica) -> None:
    promedio, total = repository.promedio_y_total(db, clinica.id)
    clinica.calificacion_prom = promedio
    clinica.total_resenas = total


# Crear
def crear(db: Session, clinica: Clinica, usuario: Usuario, datos: ResenaEntrada) -> Resena:
    if repository.buscar_de_autor(db, clinica.id, usuario.id):
        raise Conflicto(MENSAJE_REPETIDA)

    resena = Resena(clinica_id=clinica.id, autor_id=usuario.id, **datos.model_dump())
    db.add(resena)
    try:
        db.flush()
    except IntegrityError as error:
        db.rollback()
        raise Conflicto(MENSAJE_REPETIDA) from error

    recalcular_calificacion(db, clinica)
    db.commit()
    db.refresh(resena)
    return resena
