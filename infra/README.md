# Requisitos del backend en el servidor

Complementa el plan de infraestructura. Las rutas son las acordadas: código en `/opt/vitalia/app/`, base en `/var/vitalia/data/`, fotos en `/var/vitalia/fotos/` y respaldos en `/var/vitalia/respaldos/`.

## Base de datos

La API crea la base y aplica las migraciones de Alembic sola al arrancar. **No se crean tablas a mano ni con el SQL de `db/`**: ese archivo es solo de referencia. Un cambio de estructura siempre llega como migración nueva y se aplica al reiniciar el servicio.

## Instalar o actualizar

Dentro de `/opt/vitalia/app/`, que es el contenido de la carpeta `backend/` del repo:

```bash
.venv/bin/python -m pip install -r requirements.txt
sudo systemctl restart vitalia
```

En el servidor va `requirements.txt`, no `requirements-dev.txt`.

## Variables del `.env`

```
APP_NOMBRE=Vitalia API
APP_ENTORNO=produccion
APP_DEBUG=false
APP_ZONA_HORARIA=America/Mexico_City
DB_RUTA=/var/vitalia/data/vitalia.db
JWT_SECRET=PEGAR_AQUI_EL_SECRETO
JWT_EXPIRA_HORAS=8
FOTOS_RUTA=/var/vitalia/fotos
FOTOS_URL_BASE=https://TU_DOMINIO/fotos
CORS_ORIGENES=["https://TU_DOMINIO"]
```

El secreto se genera con `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`. Sin `APP_ENTORNO` distinto de `local` y un `JWT_SECRET` propio de 32 caracteres o más, la API no arranca. El `.env` con permisos `600`.

El usuario del servicio necesita escribir en `/var/vitalia/data/` y `/var/vitalia/fotos/`.

## Comando del servicio

```
ExecStart=/opt/vitalia/app/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips 127.0.0.1
WorkingDirectory=/opt/vitalia/app
```

`--proxy-headers` es obligatorio detrás de Apache: sin él, la API ve la IP de Apache en todas las peticiones y el límite de 5 intentos de login bloquearía a todos los usuarios a la vez.

## Apache

```apache
ProxyPreserveHost On
ProxyPass        /api http://127.0.0.1:8000/api
ProxyPassReverse /api http://127.0.0.1:8000/api
RequestHeader set X-Forwarded-Proto "https"

Alias /fotos /var/vitalia/fotos
<Directory /var/vitalia/fotos>
    Require all granted
    Options -Indexes
    Header set X-Content-Type-Options "nosniff"
</Directory>

LimitRequestBody 6291456
```

- En producción la API no sirve las fotos; las sirve Apache con `nosniff` y sin listar la carpeta.
- `LimitRequestBody` permite fotos de hasta 5 MB.
- Swagger, en `/docs` y `/openapi.json`, queda sin publicar. Si se quiere en el servidor, se agrega un `ProxyPass` para cada uno.

Comprobación: `https://TU_DOMINIO/api/v1/salud` responde `"baseDatos": "conectada"`.

## Respaldos

La base trabaja en modo WAL: **no se respalda copiando el archivo**, porque una copia mientras la API escribe puede quedar incompleta. Se usa:

```bash
sqlite3 /var/vitalia/data/vitalia.db ".backup /var/vitalia/respaldos/vitalia-$(date +%F).db"
```

## Primer admin y clínicas

Dentro de `/opt/vitalia/app/`, con el usuario del servicio:

```bash
.venv/bin/python -m scripts.crear_admin
.venv/bin/python -m scripts.cargar_clinicas /ruta/al/archivo.csv
```
