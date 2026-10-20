"""
Descarga la TRM (Tasa Representativa del Mercado) de Colombia.

Fuente: datos.gov.co, dataset "Tasa de Cambio Representativa del Mercado - Histórico"
(https://www.datos.gov.co/d/32sa-8pi3), publicado por la Superintendencia Financiera.

Guarda los datos tal como vienen de la API, sin modificarlos, en:
datos/crudos/colombia_trm.csv
"""

from pathlib import Path

import pandas as pd
import requests

# URL de la API del dataset (formato Socrata)
URL = "https://www.datos.gov.co/resource/32sa-8pi3.json"

# Carpeta raíz del repositorio: dos niveles arriba de este archivo
# (ingesta/colombia/descargar_trm.py -> ingesta/colombia -> ingesta -> raíz)
RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_SALIDA = RAIZ / "datos" / "crudos" / "colombia_trm.csv"


def descargar_trm():
    """Pide a la API todo el histórico de la TRM y lo devuelve como DataFrame."""
    parametros = {
        "$limit": 50000,               # la API devuelve solo 1.000 filas si no se indica otro límite
        "$order": "vigenciadesde ASC", # de la fecha más antigua a la más reciente
    }

    respuesta = requests.get(URL, params=parametros, timeout=60)
    respuesta.raise_for_status()  # si la API responde con error, el script se detiene aquí

    return pd.DataFrame(respuesta.json())


def main():
    print("Descargando la TRM desde datos.gov.co...")
    trm = descargar_trm()

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    trm.to_csv(ARCHIVO_SALIDA, index=False)

    print(f"Filas descargadas: {len(trm)}")
    print(f"Desde {trm['vigenciadesde'].min()[:10]} hasta {trm['vigenciadesde'].max()[:10]}")
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
