# Vitalia Backend

API del directorio veterinario Vitalia: búsqueda de veterinarias, reseñas, carnet de mascotas, comunidad y panel para clínicas. Hecha con Python, FastAPI, SQLAlchemy, Alembic y SQLite.

El contrato de la API, con todas las rutas, campos y errores, está en `docs/Vitalia_Contrato_API_v1.3.pdf`.

## Requisitos

- Python 3.12 o superior, probado con 3.14
- Git

No hace falta Docker ni un servidor de base de datos: SQLite guarda todo en un archivo.

## Instalación

Todos los comandos se corren dentro de `backend/`, con Git Bash en Windows.

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m pytest
python -m uvicorn app.main:app --reload
```

En Linux o Mac el entorno se activa con `source .venv/bin/activate`.

Al arrancar, la API crea `data/vitalia.db`, aplica las migraciones pendientes y siembra las 10 categorías de servicios.

Para comprobar que funciona:

- http://localhost:8000/api/v1/salud debe responder `"baseDatos": "conectada"`
- http://localhost:8000/docs muestra Swagger con todas las rutas

Usa siempre `python -m` delante de `pytest`, `pip`, `ruff`, `uvicorn` y `alembic`; en Windows llamarlos directo puede fallar.

## Variables de entorno

Se definen en `.env`, que nunca se sube al repo. `.env.example` trae los valores para desarrollo.

| Variable | Valor local | Para qué |
|---|---|---|
| `APP_NOMBRE` | `Vitalia API` | Título en Swagger |
| `APP_ENTORNO` | `local` | Fuera de `local`, la API exige un `JWT_SECRET` propio |
| `APP_DEBUG` | `true` | Logs detallados |
| `APP_ZONA_HORARIA` | `America/Mexico_City` | Fechas y cálculo de abierto ahora |
| `DB_RUTA` | `data/vitalia.db` | Archivo de la base SQLite |
| `JWT_SECRET` | el de ejemplo | Firma de los tokens; en el servidor, propio y de 32 caracteres o más |
| `JWT_EXPIRA_HORAS` | `8` | Duración de la sesión |
| `FOTOS_RUTA` | `data/fotos` | Carpeta donde se guardan las fotos subidas |
| `FOTOS_URL_BASE` | `http://localhost:8000/fotos` | Dirección pública de las fotos |
| `CORS_ORIGENES` | `["http://localhost:3000","http://localhost:5173"]` | Dominios del front permitidos |

## Comandos frecuentes

| Comando | Para qué |
|---|---|
| `python -m pytest` | Corre todas las pruebas |
| `python -m pytest tests/test_resenas.py` | Corre un solo archivo |
| `python -m ruff check . --fix` | Revisa el estilo y corrige lo automático |
| `python -m ruff format .` | Acomoda el formato |
| `python -m scripts.crear_admin` | Crea un usuario admin; pide nombre, correo y contraseña |
| `python -m scripts.sembrar_demo 200` | Crea 200 clínicas ficticias de demostración; con `0` las borra; solo en local |
| `python -m scripts.cargar_clinicas archivo.csv` | Carga clínicas reales desde un CSV |

## Migraciones

La estructura de la base se maneja con Alembic. Las migraciones viven en `migraciones/versions/` y la API las aplica sola al arrancar.

Cuando cambies un modelo:

```bash
python -m alembic revision --autogenerate -m "describe el cambio"
```

Revisa siempre el archivo generado antes de subirlo: Alembic no detecta todo, por ejemplo un cambio de nombre de columna lo ve como borrar una y crear otra. Luego corre las pruebas; `test_migraciones.py` falla si un modelo cambió sin su migración.

Comandos útiles:

| Comando | Para qué |
|---|---|
| `python -m alembic current` | En qué migración está tu base |
| `python -m alembic check` | Si los modelos y la base coinciden |
| `python -m alembic history` | Lista de migraciones |
| `python -m alembic downgrade -1` | Deshace la última migración |

Una base creada antes de Alembic se adopta sola al arrancar la API, sin perder datos.

## Cargar clínicas reales

1. Copia `scripts/plantilla_clinicas.csv` y llénalo en Excel o Google Sheets; una clínica por fila.
2. Guárdalo como **CSV UTF-8 delimitado por comas**.
3. Corre `python -m scripts.cargar_clinicas tu_archivo.csv`.

Reglas del archivo:

- Obligatorias: `nombre`, `tipos`, `calle`, `colonia`, `alcaldia_municipio`, `ciudad`, `estado`, `codigo_postal`, `lat`, `lng` y `telefono`.
- `tipos`: `veterinaria`, `hospital`, `estetica`, `hospedaje` o `adiestramiento`; varios separados con `|`.
- `telefono` de 10 dígitos y `codigo_postal` de 5, sin espacios.
- `lat` y `lng`: clic derecho sobre el lugar en Google Maps.
- `urgencias_24h`: `sí` si atiende las 24 horas.

Si una fila tiene errores, no se carga ninguna y el script dice qué fila y qué campo corregir. Una clínica con el mismo nombre y código postal que otra ya cargada se omite, así que el script se puede correr varias veces. Las clínicas cargadas quedan verificadas y sin cuenta propietaria.

## Rutas

Todas cuelgan de `/api/v1`. El detalle de cada una está en el contrato y en Swagger.

| Grupo | Prefijo | Acceso |
|---|---|---|
| Salud | `/salud` | Público |
| Autenticación | `/auth` | Público, salvo `/auth/me` |
| Mi cuenta | `/me` | Sesión |
| Categorías | `/categorias` | Público |
| Clínicas y búsqueda | `/clinicas` | Público |
| Reseñas | `/clinicas/{id}/resenas` y `/resenas/{id}` | Leer es público; escribir pide rol dueño |
| Negocio | `/negocio/clinicas` | Rol clínica, dueña del recurso |
| Mis mascotas | `/me/mascotas` | Rol dueño |
| Comunidad | `/comunidad` | Leer es público; escribir pide sesión |
| Admin | `/admin` | Rol admin |

Las rutas protegidas esperan el encabezado `Authorization: Bearer <token>`.

## Estructura

```
app/
  core/          configuración, base de datos, migraciones, errores, fotos y utilidades
  modules/       un módulo por funcionalidad, con router, service, repository, models y schemas
  main.py        arma la aplicación
migraciones/     migraciones de Alembic
scripts/         crear admin, datos de demostración y carga de clínicas
tests/           pruebas automáticas
data/            base SQLite y fotos; no se sube al repo
```

## Pruebas e integración continua

GitHub corre `ruff` y `pytest` en cada pull request que toque `backend/`. Un PR solo se mezcla con el check en verde y la aprobación del otro integrante de backend.

## Problemas comunes

| Problema | Solución |
|---|---|
| `No module named 'app'` | Corre el comando dentro de `backend/` |
| `pytest: Permission denied` | Usa `python -m pytest` |
| La API no arranca y pide `JWT_SECRET` | Copia `.env.example` a `.env` |
| `table ... already exists` al arrancar | Corre `python -m alembic current`; si está vacío, avisa al equipo de backend |
| `I001 Import block is un-sorted` | `python -m ruff check . --fix` |
