"""
Carga a PostgreSQL todos los CSV de datos/limpios/.

Cada CSV debe tener las columnas del esquema común
(fecha, pais, indicador, valor, unidad, fuente, serie_id).

Si un indicador ya estaba cargado, primero se borran sus filas y después se
insertan las nuevas. Así el script se puede ejecutar las veces que haga falta
sin duplicar datos.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_LIMPIOS = RAIZ / "datos" / "limpios"


def conectar():
    """Crea la conexión a PostgreSQL con los datos del archivo .env."""
    load_dotenv(RAIZ / ".env")

    url = URL.create(
        "postgresql+psycopg2",
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return create_engine(url)


def cargar_archivo(engine, archivo):
    """Reemplaza en la tabla observaciones los datos de un CSV limpio."""
    datos = pd.read_csv(archivo, parse_dates=["fecha"])

    # engine.begin() abre una transacción: si algo falla, no se guarda nada
    with engine.begin() as conexion:
        for (pais, indicador), _ in datos.groupby(["pais", "indicador"]):
            conexion.execute(
                text("DELETE FROM observaciones WHERE pais = :pais AND indicador = :indicador"),
                {"pais": pais, "indicador": indicador},
            )
        datos.to_sql("observaciones", conexion, if_exists="append", index=False)

    print(f"{archivo.name}: {len(datos)} filas cargadas")


def main():
    engine = conectar()

    archivos = sorted(CARPETA_LIMPIOS.glob("*.csv"))
    if not archivos:
        print("No hay archivos en datos/limpios/")
        return

    for archivo in archivos:
        cargar_archivo(engine, archivo)


if __name__ == "__main__":
    main()
