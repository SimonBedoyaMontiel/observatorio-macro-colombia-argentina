"""
Descarga el IPC (Índice de Precios al Consumidor) de Colombia.

Fuente: DANE, anexo "Índices - Serie de empalme" (base diciembre de 2018 = 100).

El DANE no tiene una API para el IPC: publica un Excel nuevo cada mes, y su
dirección cambia con el mes (por ejemplo .../IPC/sep2026/anex-IPC-Indices-sep2026.xlsx).
Por eso el script primero busca el enlace vigente en la página del IPC y
después descarga ese archivo.

Guarda el Excel tal como viene, sin modificarlo, en:
datos/crudos/colombia_ipc.xlsx
"""

import re
from pathlib import Path

import requests

PAGINA_IPC = "https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc"
DOMINIO = "https://www.dane.gov.co"

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_SALIDA = RAIZ / "datos" / "crudos" / "colombia_ipc.xlsx"


def buscar_enlace_excel():
    """Busca en la página del DANE el enlace al Excel de índices del IPC."""
    respuesta = requests.get(PAGINA_IPC, timeout=60)
    respuesta.raise_for_status()

    # Busca un enlace del tipo /files/operaciones/IPC/<mes>/anex-IPC-Indices-<mes>.xlsx
    coincidencia = re.search(r'href="([^"]*anex-IPC-Indices-[^"]*\.xlsx)"', respuesta.text)
    if coincidencia is None:
        raise RuntimeError("No se encontró el Excel de índices en la página del DANE. "
                           "Puede que hayan cambiado el nombre del archivo.")

    return DOMINIO + coincidencia.group(1)


def main():
    print("Buscando el Excel del IPC en la página del DANE...")
    url_excel = buscar_enlace_excel()
    print(f"Encontrado: {url_excel}")

    respuesta = requests.get(url_excel, timeout=60)
    respuesta.raise_for_status()

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_SALIDA.write_bytes(respuesta.content)  # el Excel se guarda tal cual, en binario

    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
