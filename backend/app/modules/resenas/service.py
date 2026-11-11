from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, SinPermiso
from app.core.tiempo import ahora_utc
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


def armar_resumen(db: Session, clinica: Clinica) -> dict:
    conteo = repository.distribucion(db, clinica.id)
    promedio = clinica.calificacion_prom
    return {
        "promedio": round(promedio, 1) if promedio is not None else None,
        "total": clinica.total_resenas,
        "distribucion": {str(estrellas): conteo.get(estrellas, 0) for estrellas in range(5, 0, -1)},
    }


# Mantener al día la calificación de la clínica
def recalcular_calificacion(db: Session, clinica: Clinica) -> None:
    promedio, total = repository.promedio_y_total(db, clinica.id)
    clinica.calificacion_prom = promedio
    clinica.total_resenas = total


def _recalcular_de(db: Session, resena: Resena) -> None:
    clinica = db.get(Clinica, resena.clinica_id)
    if clinica is not None:
        recalcular_calificacion(db, clinica)


# Buscar y revisar permisos
def obtener(db: Session, resena_id: int) -> Resena:
    resena = repository.obtener(db, resena_id)
    if resena is None:
        raise NoEncontrado("La reseña no existe")
    return resena


def _revisar_autor(resena: Resena, usuario: Usuario) -> None:
    if resena.autor_id != usuario.id:
        raise SinPermiso("Solo el autor puede modificar esta reseña")


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


# Editar
def editar(db: Session, resena: Resena, usuario: Usuario, datos: ResenaEntrada) -> Resena:
    _revisar_autor(resena, usuario)
    resena.calificacion = datos.calificacion
    resena.comentario = datos.comentario
    resena.editado_en = ahora_utc()
    db.flush()

    _recalcular_de(db, resena)
    db.commit()
    db.refresh(resena)
    return resena


# Borrar
def borrar(db: Session, resena: Resena, usuario: Usuario) -> None:
    _revisar_autor(resena, usuario)
    db.delete(resena)
    db.flush()

    _recalcular_de(db, resena)
    db.commit()
