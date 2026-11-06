import getpass
import sys

from app.core.database import SessionLocal
from app.core.modelos import crear_tablas
from app.core.security import hashear_password
from app.modules.usuarios import repository
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import validar_password


def main() -> None:
    crear_tablas()
    nombre = input("Nombre del admin: ").strip()
    email = input("Correo del admin: ").strip().lower()
    password = getpass.getpass("Contraseña: ")

    try:
        validar_password(password)
    except ValueError as error:
        sys.exit(str(error))

    with SessionLocal() as db:
        if repository.buscar_por_email(db, email):
            sys.exit("Ya existe una cuenta con ese correo")
        admin = Usuario(
            nombre=nombre,
            email=email,
            password_hash=hashear_password(password),
            rol="admin",
        )
        repository.crear(db, admin)
    print(f"Admin {email} creado")


if __name__ == "__main__":
    main()
