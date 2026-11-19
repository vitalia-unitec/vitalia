import sqlite3
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "db" / "esquema.sql"


# Crea una base vacía con las migraciones y copia su SQL
def main() -> None:
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "esquema.db"

        import os

        os.environ["DB_RUTA"] = str(ruta)
        from app.core.database import engine
        from app.core.modelos import migrar

        migrar()
        engine.dispose()

        with sqlite3.connect(ruta) as conexion:
            filas = conexion.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
                "AND name != 'alembic_version' "
                "ORDER BY type DESC, name"
            ).fetchall()
        conexion.close()

    sentencias = ["\n".join(linea.rstrip() for linea in fila[0].splitlines()) for fila in filas]
    encabezado = "-- Esquema de Vitalia generado desde las migraciones de Alembic\n"
    encabezado += "-- No editar a mano: python -m scripts.exportar_esquema\n\n"
    DESTINO.write_text(encabezado + ";\n\n".join(sentencias) + ";\n", encoding="utf-8")
    print(f"Esquema escrito en {DESTINO}")


if __name__ == "__main__":
    sys.exit(main())
