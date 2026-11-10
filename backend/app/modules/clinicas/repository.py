from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.texto import normalizar
from app.modules.categorias.models import Categoria
from app.modules.clinicas.filtros import FiltrosBusqueda
from app.modules.clinicas.models import Clinica, ClinicaTipo, ServicioClinica


def obtener(db: Session, clinica_id: int) -> Clinica | None:
    return db.get(Clinica, clinica_id)


def buscar_activas(db: Session, filtros: FiltrosBusqueda) -> list[Clinica]:
    consulta = select(Clinica).where(Clinica.activa.is_(True))

    if filtros.q:
        texto = normalizar(filtros.q)
        consulta = consulta.where(
            or_(
                func.normalizar(Clinica.nombre).contains(texto, autoescape=True),
                func.normalizar(Clinica.colonia).contains(texto, autoescape=True),
            )
        )
    if filtros.tipo:
        consulta = consulta.where(Clinica.tipos_rel.any(ClinicaTipo.tipo == filtros.tipo))
    if filtros.categoria:
        de_la_categoria = ServicioClinica.categoria.has(Categoria.slug == filtros.categoria)
        consulta = consulta.where(Clinica.servicios.any(de_la_categoria))
    if filtros.urgencias:
        consulta = consulta.where(Clinica.urgencias_24h.is_(True))

    return list(db.scalars(consulta))


def listar_de_propietario(db: Session, propietario_id: int) -> list[Clinica]:
    consulta = select(Clinica).where(Clinica.propietario_id == propietario_id).order_by(Clinica.id)
    return list(db.scalars(consulta))


def contar_activas_de(db: Session, propietario_id: int) -> int:
    consulta = select(func.count(Clinica.id)).where(
        Clinica.propietario_id == propietario_id, Clinica.activa.is_(True)
    )
    return db.scalar(consulta) or 0


def guardar(db: Session, objeto: object) -> None:
    db.add(objeto)
    db.commit()
    db.refresh(objeto)
