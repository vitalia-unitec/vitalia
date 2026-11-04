import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import registrar_manejadores
from app.modules.salud.router import router as salud_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def crear_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_nombre,
        description="Backend del directorio veterinario Vitalia",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
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

    # Rutas
    app.include_router(salud_router, prefix="/api/v1")

    return app


app = crear_app()
