"""
Limpia la TRM y la lleva al esquema común del proyecto.

Entrada: datos/crudos/colombia_trm.csv   (un valor por día hábil, desde 1991)
Salida:  datos/limpios/colombia_trm.csv  (un valor por mes, desde 2017)

Pasos:
1. Pasar a una serie diaria completa (incluye fines de semana y festivos).
2. Calcular el promedio mensual.
3. Quedarse con los meses completos desde enero de 2017.
4. Dar el formato del esquema común.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_ENTRADA = RAIZ / "datos" / "crudos" / "colombia_trm.csv"
ARCHIVO_SALIDA = RAIZ / "datos" / "limpios" / "colombia_trm.csv"

FECHA_INICIO = "2017-01-01"


def leer_crudos():
    """Lee el CSV crudo con las columnas en el tipo de dato correcto."""
    trm = pd.read_csv(ARCHIVO_ENTRADA)
    trm["vigenciadesde"] = pd.to_datetime(trm["vigenciadesde"])
    trm["valor"] = pd.to_numeric(trm["valor"])
    return trm


def a_serie_diaria(trm):
    """
    Completa los días que faltan (fines de semana y festivos).

    La TRM de un viernes sigue vigente el sábado, el domingo y hasta el lunes.
    Por eso cada día faltante toma el último valor publicado (ffill).
    """
    serie = trm.set_index("vigenciadesde")["valor"]
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
        "pais": "Colombia",
        "indicador": "tipo_cambio_oficial",
        "valor": mensual.round(2).values,
        "unidad": "COP por USD",
        "fuente": "Superintendencia Financiera (datos.gov.co)",
        "serie_id": "32sa-8pi3",
    })


def main():
    trm = leer_crudos()
    diaria = a_serie_diaria(trm)
    mensual = a_promedio_mensual(diaria)
    limpia = al_esquema_comun(mensual)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    limpia.to_csv(ARCHIVO_SALIDA, index=False)

    print(f"Meses: {len(limpia)} (desde {limpia['fecha'].min()} hasta {limpia['fecha'].max()})")
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
