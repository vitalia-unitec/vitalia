from datetime import datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.tiempo import ahora_utc


# Contraseñas
def hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


HASH_FALSO = hashear_password("hash-para-igualar-tiempos")


# Tokens
def crear_token(usuario_id: int, rol: str) -> tuple[str, datetime]:
    settings = get_settings()
    emitido = ahora_utc()
    expira = emitido + timedelta(hours=settings.jwt_expira_horas)
    datos = {"sub": str(usuario_id), "rol": rol, "iat": emitido, "exp": expira}
    token = jwt.encode(datos, settings.jwt_secret, algorithm=settings.jwt_algoritmo)
    return token, expira


def decodificar_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algoritmo],
        options={"require": ["sub", "exp"]},
    )
