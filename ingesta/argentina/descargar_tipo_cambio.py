"""
Descarga el tipo de cambio mayorista de referencia (Com. A 3500) del BCRA.

API de Estadísticas Monetarias v4.0 del BCRA (no pide clave).
La versión 3.0 está dada de baja, por eso se usa la 4.0.

Serie: variable 5 = tipo de cambio mayorista de referencia, pesos por dólar (un valor por día hábil)

La API devuelve como máximo 3000 datos por consulta, así que se pide por páginas.

Guarda los datos tal como vienen de la API, sin modificarlos, en:
datos/crudos/argentina_tipo_cambio.csv
"""

import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

URL = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"
ID_VARIABLE = 5
DESDE = "2016-12-01"  # un mes antes de 2017, por si hace falta rellenar el inicio
POR_PAGINA = 3000

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_SALIDA = RAIZ / "datos" / "crudos" / "argentina_tipo_cambio.csv"


def descargar():
    """Recorre las páginas de la API y devuelve todos los datos en un DataFrame."""
    filas = []
    while True:
        respuesta = requests.get(
            f"{URL}/{ID_VARIABLE}",
            params={"desde": DESDE, "hasta": date.today().isoformat(), "limit": POR_PAGINA, "offset": len(filas)},
            timeout=90,
        )
        respuesta.raise_for_status()
        pagina = respuesta.json()

        datos = [d for resultado in pagina["results"] for d in resultado["detalle"]]
        filas.extend(datos)

        total = pagina["metadata"]["resultset"]["count"]
        if not datos or len(filas) >= total:
            break
        time.sleep(1)  # pausa corta: la API controla el tráfico por IP

    return pd.DataFrame(filas)


def main():
    print(f"Descargando tipo de cambio mayorista (variable {ID_VARIABLE})...")
    tipo_cambio = descargar()
    print(f"  {len(tipo_cambio)} días, desde {tipo_cambio['fecha'].min()} hasta {tipo_cambio['fecha'].max()}")

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tipo_cambio.to_csv(ARCHIVO_SALIDA, index=False)
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
