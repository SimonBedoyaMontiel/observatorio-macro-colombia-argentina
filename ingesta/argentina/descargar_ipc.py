"""
Descarga el IPC nacional (nivel general) del INDEC, a través de datos.gob.ar.

La API de series de tiempo de datos.gob.ar no pide clave. Su servidor a veces
responde lento o con error 5xx, así que se reintenta unas cuantas veces.

Serie: 148.3_INIVELNAL_DICI_M_26  (IPC nivel general nacional, base dic 2016 = 100)

Guarda los datos tal como vienen de la API, sin modificarlos, en:
datos/crudos/argentina_ipc.csv
"""

import io
import time
from pathlib import Path

import pandas as pd
import requests

URL = "https://apis.datos.gob.ar/series/api/series/"
SERIE_ID = "148.3_INIVELNAL_DICI_M_26"

REINTENTOS = 5
ESPERA_SEG = 5  # se multiplica por el número de intento

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_SALIDA = RAIZ / "datos" / "crudos" / "argentina_ipc.csv"


def descargar():
    """Pide la serie en formato CSV; reintenta si el servidor falla o tarda."""
    parametros = {"ids": SERIE_ID, "format": "csv", "limit": 1000, "sort": "asc"}

    for intento in range(1, REINTENTOS + 1):
        try:
            respuesta = requests.get(URL, params=parametros, timeout=120)
            respuesta.raise_for_status()
            return pd.read_csv(io.StringIO(respuesta.text))
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as error:
            es_error_de_cliente = (
                isinstance(error, requests.HTTPError)
                and error.response is not None
                and error.response.status_code < 500
            )
            if es_error_de_cliente or intento == REINTENTOS:
                raise
            print(f"  Intento {intento} falló ({type(error).__name__}); reintento en {ESPERA_SEG * intento} s")
            time.sleep(ESPERA_SEG * intento)


def main():
    print(f"Descargando IPC {SERIE_ID}...")
    ipc = descargar()
    print(f"  {len(ipc)} meses, desde {ipc.iloc[0, 0]} hasta {ipc.iloc[-1, 0]}")

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ipc.to_csv(ARCHIVO_SALIDA, index=False)
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
