from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.database import DbSesion
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import requerir_rol
from app.modules.clinicas import repository, service
from app.modules.clinicas.schemas import (
    ClinicaEntrada,
    HorarioSalida,
    HorariosEntrada,
    ServicioEntrada,
    ServicioSalida,
)
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/negocio/clinicas", tags=["Negocio"])

UsuarioClinica = Annotated[Usuario, Depends(requerir_rol("clinica"))]


# Clínicas
@router.get("", summary="Mis clínicas, activas o no")
def listar_mis_clinicas(usuario: UsuarioClinica, db: DbSesion) -> dict:
    clinicas = repository.listar_de_propietario(db, usuario.id)
    return ok([service.armar_detalle(c, para_negocio=True) for c in clinicas])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Registrar una clínica")
def registrar_clinica(datos: ClinicaEntrada, usuario: UsuarioClinica, db: DbSesion) -> dict:
    clinica = service.crear(db, usuario, datos)
    return ok(service.armar_detalle(clinica, para_negocio=True))


@router.get("/{clinica_id}", summary="Ver mi clínica con datos internos")
def ver_mi_clinica(clinica_id: IdRuta, usuario: UsuarioClinica, db: DbSesion) -> dict:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    return ok(service.armar_detalle(clinica, para_negocio=True))


@router.put("/{clinica_id}", summary="Editar datos generales")
def editar_clinica(
    clinica_id: IdRuta, datos: ClinicaEntrada, usuario: UsuarioClinica, db: DbSesion
) -> dict:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    clinica = service.editar(db, clinica, datos)
    return ok(service.armar_detalle(clinica, para_negocio=True))


@router.delete("/{clinica_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Dar de baja")
def dar_de_baja(clinica_id: IdRuta, usuario: UsuarioClinica, db: DbSesion) -> Response:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    service.dar_de_baja(db, clinica)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Horarios
@router.put("/{clinica_id}/horarios", summary="Reemplazar todos los horarios")
def reemplazar_horarios(
    clinica_id: IdRuta, datos: HorariosEntrada, usuario: UsuarioClinica, db: DbSesion
) -> dict:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    horarios = service.reemplazar_horarios(db, clinica, datos)
    return ok([HorarioSalida.model_validate(h).a_json() for h in horarios])


# Servicios
@router.post(
    "/{clinica_id}/servicios", status_code=status.HTTP_201_CREATED, summary="Agregar servicio"
)
def agregar_servicio(
    clinica_id: IdRuta, datos: ServicioEntrada, usuario: UsuarioClinica, db: DbSesion
) -> dict:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    servicio = service.agregar_servicio(db, clinica, datos)
    return ok(ServicioSalida.model_validate(servicio).a_json())


@router.put("/{clinica_id}/servicios/{servicio_id}", summary="Editar servicio")
def editar_servicio(
    clinica_id: IdRuta,
    servicio_id: IdRuta,
    datos: ServicioEntrada,
    usuario: UsuarioClinica,
    db: DbSesion,
) -> dict:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    servicio = service.editar_servicio(db, clinica, servicio_id, datos)
    return ok(ServicioSalida.model_validate(servicio).a_json())


@router.delete(
    "/{clinica_id}/servicios/{servicio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar servicio",
)
def borrar_servicio(
    clinica_id: IdRuta, servicio_id: IdRuta, usuario: UsuarioClinica, db: DbSesion
) -> Response:
    clinica = service.obtener_propia(db, clinica_id, usuario)
    service.borrar_servicio(db, clinica, servicio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
