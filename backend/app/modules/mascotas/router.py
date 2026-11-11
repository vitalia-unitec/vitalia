from fastapi import APIRouter, Response, status

from app.core.database import DbSesion
from app.core.responses import ok
from app.core.rutas import IdRuta
from app.modules.auth.dependencies import UsuarioDueno
from app.modules.mascotas import repository, service
from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaEntrada, MascotaSalida

router = APIRouter(prefix="/me/mascotas", tags=["Mis mascotas"])


def _salida(mascota: Mascota) -> dict:
    return MascotaSalida.model_validate(mascota).a_json()


@router.get("", summary="Mis mascotas")
def listar_mascotas(usuario: UsuarioDueno, db: DbSesion) -> dict:
    return ok([_salida(m) for m in repository.listar_de_dueno(db, usuario.id)])


@router.get("/{mascota_id}", summary="Una de mis mascotas")
def ver_mascota(mascota_id: IdRuta, usuario: UsuarioDueno, db: DbSesion) -> dict:
    return ok(_salida(service.obtener_mia(db, mascota_id, usuario)))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear carnet")
def crear_mascota(datos: MascotaEntrada, usuario: UsuarioDueno, db: DbSesion) -> dict:
    return ok(_salida(service.crear(db, usuario, datos)))


@router.put("/{mascota_id}", summary="Editar carnet")
def editar_mascota(
    mascota_id: IdRuta, datos: MascotaEntrada, usuario: UsuarioDueno, db: DbSesion
) -> dict:
    mascota = service.obtener_mia(db, mascota_id, usuario)
    return ok(_salida(service.editar(db, mascota, datos)))


@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrar carnet")
def borrar_mascota(mascota_id: IdRuta, usuario: UsuarioDueno, db: DbSesion) -> Response:
    mascota = service.obtener_mia(db, mascota_id, usuario)
    repository.borrar(db, mascota)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
