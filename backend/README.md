# Vitalia Backend

API del directorio veterinario Vitalia, hecha con Python, FastAPI y SQLite.

## Requisitos

- Python 3.12 o superior, probado con 3.14
- Git

No se necesita Docker ni instalar un servidor de base de datos: SQLite guarda todo en un archivo.

## Arranque en Windows con Git Bash

Todos los comandos se corren dentro de la carpeta `backend/`.

```bash
cd backend

# 1. Entorno virtual
python -m venv .venv
source .venv/Scripts/activate

# 2. Dependencias
pip install -r requirements-dev.txt

# 3. Variables de entorno
cp .env.example .env

# 4. Servidor
uvicorn app.main:app --reload
```

En Linux o Mac el activado es `source .venv/bin/activate`.

La primera vez que arranca, se crea solo el archivo `data/vitalia.db`.

## Revisar que funciona

- Salud de la API: http://localhost:8000/api/v1/salud
- Documentación Swagger: http://localhost:8000/docs

## Comandos útiles

```bash
pytest              # correr pruebas
ruff check .        # revisar estilo
ruff format .       # formatear código
```

## Estructura

```
app/
  core/       configuración, conexión a BD, respuestas y errores
  modules/    un módulo por funcionalidad
  main.py     punto de entrada
tests/        pruebas automáticas
data/         archivo SQLite, no se sube al repo
```
