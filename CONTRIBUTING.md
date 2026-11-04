# Cómo trabajamos en Vitalia

## Ramas

- `main`: versión estable que se entrega. Nadie sube directo aquí.
- `develop`: integración de todos los equipos. Se actualiza solo con pull requests.
- Ramas de trabajo, siempre desde `develop`:

| Tipo | Formato | Ejemplo |
|---|---|---|
| Funcionalidad | `feature/<equipo>-<tema>` | `feature/backend-auth` |
| Corrección | `fix/<equipo>-<tema>` | `fix/frontend-mapa-pines` |
| Documentación | `docs/<tema>` | `docs/contrato-v1.2` |

## Flujo

```bash
git checkout develop
git pull
git checkout -b feature/backend-auth
# trabajar y hacer commits
git push -u origin feature/backend-auth
```

Después abre un pull request hacia `develop` en GitHub.

## Commits

Mensajes cortos en español que digan qué se hizo:

```
backend: agrega endpoint de login
frontend: pinta tarjetas de clínicas cercanas
db: crea tabla de horarios
infra: configura Apache para /api
```

## Pull requests

- Siempre hacia `develop`, nunca hacia `main`.
- Llena la plantilla que aparece al abrirlo.
- Necesita al menos una aprobación de alguien de tu equipo.
- Si toca el contrato de la API, también aprueba alguien de backend.
- Liga el issue que resuelve con `Cierra #12` en la descripción.

## Issues

Usa la plantilla que corresponda:

- **Tarea**: algo que hay que hacer.
- **Error**: algo que no funciona.
- **Cambio al contrato**: pedir una ruta, campo o regla nueva en la API.
- **Duda entre equipos**: preguntas que necesitan respuesta de otro equipo.

Ponle la etiqueta de tu equipo y asígnatelo si lo vas a hacer tú.

## Lo que nunca se sube

- Archivos `.env`, contraseñas o llaves de API.
- La base de datos `.db`.
- Carpetas como `.venv/` o `node_modules/`.
