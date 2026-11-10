from dataclasses import dataclass
from math import ceil
from typing import Annotated

from fastapi import Depends, Query


@dataclass
class Paginacion:
    pagina: int
    por_pagina: int

    @property
    def desde(self) -> int:
        return (self.pagina - 1) * self.por_pagina

    def meta(self, total: int) -> dict:
        return {
            "pagina": self.pagina,
            "porPagina": self.por_pagina,
            "total": total,
            "totalPaginas": ceil(total / self.por_pagina) if total else 0,
        }


def leer_paginacion(
    pagina: Annotated[int, Query(ge=1)] = 1,
    por_pagina: Annotated[int, Query(alias="porPagina", ge=1, le=50)] = 10,
) -> Paginacion:
    return Paginacion(pagina=pagina, por_pagina=por_pagina)


ParametrosPagina = Annotated[Paginacion, Depends(leer_paginacion)]
