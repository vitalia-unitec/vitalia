import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.errors import registrar_manejadores
from app.core.modelos import crear_tablas
from app.modules.auth.router import router as auth_router
from app.modules.categorias.router import router as categorias_router
from app.modules.clinicas.router import router as clinicas_router
from app.modules.clinicas.router_negocio import router as negocio_router
from app.modules.comunidad.router import router as comunidad_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.resenas.router import router as resenas_router
from app.modules.salud.router import router as salud_router
from app.modules.usuarios.router import router as usuarios_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    crear_tablas()
    yield


def crear_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_nombre,
        description="Backend del directorio veterinario Vitalia",
        version="0.3.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=ciclo_de_vida,
    )

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origenes,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Errores
    registrar_manejadores(app)

    # Fotos; en producción las sirve Apache
    if settings.app_entorno == "local":
        settings.fotos_ruta_absoluta.mkdir(parents=True, exist_ok=True)
        app.mount("/fotos", StaticFiles(directory=settings.fotos_ruta_absoluta), name="fotos")

    # Rutas
    app.include_router(salud_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(usuarios_router, prefix="/api/v1")
    app.include_router(categorias_router, prefix="/api/v1")
    app.include_router(clinicas_router, prefix="/api/v1")
    app.include_router(negocio_router, prefix="/api/v1")
    app.include_router(comunidad_router, prefix="/api/v1")
    app.include_router(resenas_router, prefix="/api/v1")
    app.include_router(mascotas_router, prefix="/api/v1")

    return app


app = crear_app()
