from sqlalchemy.orm import Session

from app.core.errors import Conflicto, CredencialesInvalidas
from app.core.fotos import borrar_foto
from app.core.security import hashear_password, verificar_password
from app.modules.clinicas import repository as clinicas_repository
from app.modules.mascotas import service as mascotas_service
from app.modules.usuarios import repository
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import ActualizarPerfil, CambiarPassword


def actualizar_perfil(db: Session, usuario: Usuario, datos: ActualizarPerfil) -> Usuario:
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        if valor is not None or campo == "telefono":
            setattr(usuario, campo, valor)
    return repository.guardar(db, usuario)


def cambiar_password(db: Session, usuario: Usuario, datos: CambiarPassword) -> None:
    if not verificar_password(datos.password_actual, usuario.password_hash):
        raise CredencialesInvalidas("La contraseña actual no coincide")
    usuario.password_hash = hashear_password(datos.password_nueva)
    repository.guardar(db, usuario)


def borrar_cuenta(db: Session, usuario: Usuario) -> None:
    if usuario.rol == "clinica" and clinicas_repository.contar_activas_de(db, usuario.id):
        raise Conflicto("Primero da de baja tus clínicas")

    fotos_de_mascotas = mascotas_service.rutas_de_fotos_de_dueno(db, usuario.id)
    repository.borrar(db, usuario)
    for ruta in fotos_de_mascotas:
        borrar_foto(ruta)
