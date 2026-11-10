from typing import Annotated

from fastapi import Path

# Mayor entero que SQLite puede guardar en una columna INTEGER
ID_MAXIMO = 2**63 - 1

IdRuta = Annotated[int, Path(ge=1, le=ID_MAXIMO, description="Identificador del recurso")]
