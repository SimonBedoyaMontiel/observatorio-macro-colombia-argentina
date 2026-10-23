"""
Limpia el IPC del INDEC y lo lleva al esquema común del proyecto.

Entrada: datos/crudos/argentina_ipc.csv   (dos columnas: indice_tiempo y el valor del índice)
Salida:  datos/limpios/argentina_ipc.csv  (formato largo, desde 2017)

Genera tres indicadores:
- ipc                 el índice (base diciembre de 2016 = 100)
- inflacion_mensual   variación % frente al mes anterior
- inflacion_anual     variación % frente al mismo mes del año anterior

Diferencia con Colombia: la serie nacional del INDEC arranca en diciembre de 2016
(índice = 100), así que no hay datos de 2016 para calcular la inflación anual de
enero a noviembre de 2017. La inflación anual de Argentina empieza en diciembre
de 2017 (contra la base). La inflación mensual de enero de 2017 sí se calcula,
contra la base de diciembre de 2016.

Pasos:
1. Leer el índice y agregar la base (diciembre de 2016 = 100).
2. Calcular las variaciones con todo el histórico.
3. Quedarse con los datos desde enero de 2017 y dar el formato del esquema común.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_ENTRADA = RAIZ / "datos" / "crudos" / "argentina_ipc.csv"
ARCHIVO_SALIDA = RAIZ / "datos" / "limpios" / "argentina_ipc.csv"

FECHA_INICIO = "2017-01-01"
SERIE_ID = "148.3_INIVELNAL_DICI_M_26"


def leer_crudos():
    """Lee el índice como una serie con la fecha del primer día de cada mes."""
    crudo = pd.read_csv(ARCHIVO_ENTRADA)
    crudo["indice_tiempo"] = pd.to_datetime(crudo["indice_tiempo"])
    # El CSV trae dos columnas: la fecha y el índice. El nombre de la segunda
    # cambia según cómo responda la API, así que se la toma por posición.
    serie = crudo.set_index("indice_tiempo").iloc[:, 0].astype(float).dropna().sort_index()

    # La base de la serie es diciembre de 2016 = 100: se agrega para poder
    # calcular la inflación mensual de enero de 2017.
    base = pd.Series([100.0], index=[pd.Timestamp("2016-12-01")])
    return pd.concat([base, serie[serie.index > "2016-12-01"]])


def calcular_indicadores(ipc):
    """Calcula las dos inflaciones a partir del índice."""
    return {
        "ipc": (ipc, "indice (dic 2016 = 100)"),
        "inflacion_mensual": ((ipc / ipc.shift(1) - 1) * 100, "porcentaje"),
        "inflacion_anual": ((ipc / ipc.shift(12) - 1) * 100, "porcentaje"),
    }


def al_esquema_comun(indicadores):
    """Une los tres indicadores en una sola tabla con el formato de observaciones."""
    partes = []
    for nombre, (serie, unidad) in indicadores.items():
        serie = serie[serie.index >= FECHA_INICIO].dropna()
        partes.append(pd.DataFrame({
            "fecha": serie.index.date,
            "pais": "Argentina",
            "indicador": nombre,
            "valor": serie.round(2).values,
            "unidad": unidad,
            "fuente": "INDEC (datos.gob.ar)",
            "serie_id": SERIE_ID,
        }))
    return pd.concat(partes, ignore_index=True)


def main():
    ipc = leer_crudos()
    indicadores = calcular_indicadores(ipc)
    limpia = al_esquema_comun(indicadores)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    limpia.to_csv(ARCHIVO_SALIDA, index=False)

    for nombre, filas in limpia.groupby("indicador").size().items():
        print(f"{nombre}: {filas} meses")
    print(f"Desde {limpia['fecha'].min()} hasta {limpia['fecha'].max()}")
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
