from sqlalchemy.orm import Session

from app.core.errors import Conflicto, CredencialesInvalidas, DemasiadasPeticiones
from app.core.security import HASH_FALSO, crear_token, hashear_password, verificar_password
from app.modules.auth.limitador import limitador_login
from app.modules.auth.schemas import LoginEntrada, RegistroEntrada, SesionSalida
from app.modules.usuarios import repository
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioSalida


def _armar_sesion(usuario: Usuario) -> SesionSalida:
    token, expira = crear_token(usuario.id, usuario.rol)
    datos_usuario = UsuarioSalida.model_validate(usuario)
    return SesionSalida(token=token, expira_en=expira, usuario=datos_usuario)


def registrar(db: Session, datos: RegistroEntrada) -> SesionSalida:
    if repository.buscar_por_email(db, datos.email):
        raise Conflicto("Ya existe una cuenta con ese correo")

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password_hash=hashear_password(datos.password),
        telefono=datos.telefono,
        rol=datos.rol,
    )
    return _armar_sesion(repository.crear(db, usuario))


def iniciar_sesion(db: Session, datos: LoginEntrada, ip: str) -> SesionSalida:
    if limitador_login.bloqueado(ip):
        raise DemasiadasPeticiones()

    usuario = repository.buscar_por_email(db, datos.email)
    hash_a_revisar = usuario.password_hash if usuario else HASH_FALSO

    if not verificar_password(datos.password, hash_a_revisar) or usuario is None:
        limitador_login.registrar_fallo(ip)
        raise CredencialesInvalidas()

    limitador_login.reiniciar(ip)
    return _armar_sesion(usuario)
