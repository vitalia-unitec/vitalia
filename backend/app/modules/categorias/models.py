from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    icono: Mapped[str] = mapped_column(String(40))
