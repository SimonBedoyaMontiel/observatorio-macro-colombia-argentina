"""
Limpia el IPC del DANE y lo lleva al esquema común del proyecto.

Entrada: datos/crudos/colombia_ipc.xlsx   (tabla ancha: meses en filas, años en columnas)
Salida:  datos/limpios/colombia_ipc.csv   (formato largo, desde 2017)

Genera tres indicadores:
- ipc                 el índice (base diciembre de 2018 = 100)
- inflacion_mensual   variación % frente al mes anterior
- inflacion_anual     variación % frente al mismo mes del año anterior

Pasos:
1. Encontrar la tabla dentro del Excel.
2. Pasar de formato ancho (un año por columna) a largo (una fila por mes).
3. Calcular las variaciones con todo el histórico.
4. Quedarse con los datos desde enero de 2017 y dar el formato del esquema común.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_ENTRADA = RAIZ / "datos" / "crudos" / "colombia_ipc.xlsx"
ARCHIVO_SALIDA = RAIZ / "datos" / "limpios" / "colombia_ipc.csv"

FECHA_INICIO = "2017-01-01"

MESES = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


def leer_tabla():
    """
    Lee el Excel y se queda solo con la tabla de índices.

    El Excel trae títulos y notas arriba y abajo de la tabla. En vez de fijar
    a mano en qué fila empieza, se busca la fila cuya primera celda dice "Mes":
    así el script sigue funcionando si el DANE agrega o quita una línea de título.
    """
    hoja = pd.read_excel(ARCHIVO_ENTRADA, header=None)

    fila_encabezado = hoja.index[hoja[0] == "Mes"][0]
    tabla = hoja.iloc[fila_encabezado + 1:].copy()
    tabla.columns = hoja.iloc[fila_encabezado]

    # Solo las filas de meses (descarta las notas del final, como "Fuente: DANE.")
    return tabla[tabla["Mes"].isin(MESES.keys())]


def a_formato_largo(tabla):
    """Pasa de un año por columna a una fila por mes, ordenada por fecha."""
    larga = tabla.melt(id_vars="Mes", var_name="anio", value_name="valor")
    larga = larga.dropna(subset=["valor"])  # meses que todavía no se publican

    larga["fecha"] = pd.to_datetime({
        "year": larga["anio"].astype(float).astype(int),
        "month": larga["Mes"].map(MESES),
        "day": 1,
    })
    larga["valor"] = pd.to_numeric(larga["valor"])

    return larga.set_index("fecha")["valor"].sort_index()


def calcular_indicadores(ipc):
    """Calcula las dos inflaciones a partir del índice."""
    return {
        "ipc": (ipc, "indice (dic 2018 = 100)"),
        "inflacion_mensual": ((ipc / ipc.shift(1) - 1) * 100, "porcentaje"),
        "inflacion_anual": ((ipc / ipc.shift(12) - 1) * 100, "porcentaje"),
    }


def al_esquema_comun(indicadores):
    """Une los tres indicadores en una sola tabla con el formato de observaciones."""
    partes = []
    for nombre, (serie, unidad) in indicadores.items():
        serie = serie[serie.index >= FECHA_INICIO]
        partes.append(pd.DataFrame({
            "fecha": serie.index.date,
            "pais": "Colombia",
            "indicador": nombre,
            "valor": serie.round(2).values,
            "unidad": unidad,
            "fuente": "DANE",
            "serie_id": "IPC total nacional, serie de empalme",
        }))
    return pd.concat(partes, ignore_index=True)


def main():
    tabla = leer_tabla()
    ipc = a_formato_largo(tabla)
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
