"""
Limpia el tipo de cambio mayorista del BCRA y lo lleva al esquema común del proyecto.

Entrada: datos/crudos/argentina_tipo_cambio.csv   (un valor por día hábil)
Salida:  datos/limpios/argentina_tipo_cambio.csv  (un valor por mes, desde 2017)

Pasos (iguales a los de la TRM de Colombia):
1. Pasar a una serie diaria completa (incluye fines de semana y feriados).
2. Calcular el promedio mensual.
3. Quedarse con los meses completos desde enero de 2017.
4. Dar el formato del esquema común.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_ENTRADA = RAIZ / "datos" / "crudos" / "argentina_tipo_cambio.csv"
ARCHIVO_SALIDA = RAIZ / "datos" / "limpios" / "argentina_tipo_cambio.csv"

FECHA_INICIO = "2017-01-01"


def leer_crudos():
    """Lee el CSV crudo con las columnas en el tipo de dato correcto."""
    tipo_cambio = pd.read_csv(ARCHIVO_ENTRADA)
    tipo_cambio["fecha"] = pd.to_datetime(tipo_cambio["fecha"])
    tipo_cambio["valor"] = pd.to_numeric(tipo_cambio["valor"])
    return tipo_cambio


def a_serie_diaria(tipo_cambio):
    """
    Completa los días que faltan (fines de semana y feriados).

    El tipo de cambio de un viernes sigue vigente el fin de semana. Por eso
    cada día faltante toma el último valor publicado (ffill).
    """
    serie = tipo_cambio.drop_duplicates("fecha", keep="last").set_index("fecha")["valor"].sort_index()
    return serie.resample("D").ffill()


def a_promedio_mensual(diaria):
    """Promedio de cada mes, quitando el mes actual si todavía no terminó."""
    mensual = diaria.resample("MS").mean()  # MS = el mes se identifica con su primer día

    ultimo_dia = diaria.index.max()
    if not ultimo_dia.is_month_end:
        mensual = mensual.iloc[:-1]

    return mensual[mensual.index >= FECHA_INICIO]


def al_esquema_comun(mensual):
    """Da a la serie las columnas de la tabla observaciones."""
    return pd.DataFrame({
        "fecha": mensual.index.date,
        "pais": "Argentina",
        "indicador": "tipo_cambio_oficial",
        "valor": mensual.round(2).values,
        "unidad": "ARS por USD",
        "fuente": "BCRA",
        "serie_id": "monetarias/5",
    })


def main():
    tipo_cambio = leer_crudos()
    diaria = a_serie_diaria(tipo_cambio)
    mensual = a_promedio_mensual(diaria)
    limpia = al_esquema_comun(mensual)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    limpia.to_csv(ARCHIVO_SALIDA, index=False)

    print(f"Meses: {len(limpia)} (desde {limpia['fecha'].min()} hasta {limpia['fecha'].max()})")
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
