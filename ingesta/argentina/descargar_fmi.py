"""
Descarga del FMI (Fondo Monetario Internacional) tres series de Argentina.

El Banco de la República no tiene una API abierta para estas series, así que se
usa la API del FMI, que recibe los datos de cada banco central y los publica con
las mismas definiciones para todos los países. Eso facilita comparar con Argentina.

| Serie                        | Dataset del FMI                                   |
|------------------------------|---------------------------------------------------|
| Reservas internacionales     | IRFCL  (International Reserves and Foreign Currency Liquidity) |
| Dinero amplio                | MFS_MA (Monetary Aggregates)                      |
| Tasa del mercado monetario   | MFS_IR (Interest Rates)                           |

Guarda los datos tal como vienen de la API, sin modificarlos, en:
datos/crudos/argentina_fmi.csv
"""

import io
import time
from pathlib import Path

import pandas as pd
import requests

URL_BASE = "https://api.imf.org/external/sdmx/2.1/data/IMF.STA"

# Pide la respuesta en formato CSV (por defecto la API responde en XML)
ENCABEZADOS = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}

PAIS = "ARG"

# Cada serie es un dataset + una "clave" con sus dimensiones separadas por puntos.
# Ejemplo: ARG.BM_MAI.XDC.M = Argentina . dinero amplio . moneda local . mensual
SERIES = [
    ("IRFCL", f"{PAIS}.IRFCLDT1_IRFCL65_USD.S1XS1311.M"),
    ("MFS_MA", f"{PAIS}.BM_MAI.XDC.M"),
    ("MFS_IR", f"{PAIS}.MMRT_RT_PT_A_PT.M"),
]

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_SALIDA = RAIZ / "datos" / "crudos" / "argentina_fmi.csv"


def descargar_serie(dataset, clave):
    """Pide una serie a la API del FMI y la devuelve como DataFrame."""
    url = f"{URL_BASE},{dataset}/{clave}"
    respuesta = requests.get(url, headers=ENCABEZADOS, timeout=90)
    respuesta.raise_for_status()

    # La respuesta ya es un CSV en texto: io.StringIO deja que pandas lo lea como si fuera un archivo
    return pd.read_csv(io.StringIO(respuesta.text), low_memory=False)


def main():
    partes = []
    for dataset, clave in SERIES:
        print(f"Descargando {dataset}: {clave}...")
        serie = descargar_serie(dataset, clave)
        print(f"  {len(serie)} meses, desde {serie['TIME_PERIOD'].min()} hasta {serie['TIME_PERIOD'].max()}")
        partes.append(serie)
        time.sleep(1)  # una pausa corta entre consultas para no saturar la API

    fmi = pd.concat(partes, ignore_index=True)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fmi.to_csv(ARCHIVO_SALIDA, index=False)
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
