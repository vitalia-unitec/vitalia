from sqlalchemy.orm import Session

from app.core.errors import CredencialesInvalidas
from app.core.security import hashear_password, verificar_password
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
    # En las etapas 4 y 6 se agregan las reglas de clínicas registradas y reseñas
    repository.borrar(db, usuario)
