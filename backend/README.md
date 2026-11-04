# Vitalia Backend

API del directorio veterinario Vitalia, hecha con Python, FastAPI y MySQL.

## Requisitos

- Python 3.12 o superior, probado con 3.14
- Docker Desktop
- Git

## Arranque en Windows con Git Bash

```bash
# 1. Entorno virtual
python -m venv .venv
source .venv/Scripts/activate

# 2. Dependencias
pip install -r requirements-dev.txt

# 3. Variables de entorno
cp .env.example .env

# 4. Base de datos
docker compose up -d
docker compose ps

# 5. Servidor
uvicorn app.main:app --reload
```

En Linux o Mac el paso 1 cambia a `source .venv/bin/activate`.

## Revisar que funciona

- Salud de la API: http://localhost:8000/api/v1/salud
- Documentación Swagger: http://localhost:8000/docs

## Comandos útiles

```bash
pytest              # correr pruebas
ruff check .        # revisar estilo
ruff format .       # formatear código
docker compose down # apagar MySQL sin borrar datos
```

## Estructura

```
app/
  core/       configuración, conexión a BD, respuestas y errores
  modules/    un módulo por funcionalidad
  main.py     punto de entrada
tests/        pruebas automáticas
```
