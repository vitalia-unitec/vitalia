from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def ahora_utc() -> datetime:
    return datetime.now(UTC)


def a_hora_local(fecha: datetime) -> datetime:
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=UTC)
    return fecha.astimezone(ZoneInfo(get_settings().app_zona_horaria))
