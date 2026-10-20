"""
Limpia las series del FMI y las lleva al esquema común del proyecto.

Entrada: datos/crudos/colombia_fmi.csv   (formato de la API del FMI)
Salida:  datos/limpios/colombia_fmi.csv  (formato largo, desde 2017)

Pasos:
1. Quedarse solo con las columnas necesarias.
2. Convertir el periodo del FMI ("2026-M07") a fecha (2026-07-01).
3. Pasar cada serie a una unidad fácil de leer (millones, miles de millones).
4. Quedarse con los datos desde enero de 2017 y dar el formato del esquema común.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_ENTRADA = RAIZ / "datos" / "crudos" / "colombia_fmi.csv"
ARCHIVO_SALIDA = RAIZ / "datos" / "limpios" / "colombia_fmi.csv"

FECHA_INICIO = "2017-01-01"

# Código del FMI -> (nombre en el proyecto, unidad, divisor)
# El FMI entrega los valores en unidades (por ejemplo, 66.394.345.354 dólares);
# el divisor los pasa a una escala más legible.
INDICADORES = {
    "IRFCLDT1_IRFCL65_USD": ("reservas_internacionales", "millones de USD", 1e6),
    "BM_MAI": ("dinero_amplio", "miles de millones de COP", 1e9),
    "MMRT_RT_PT_A_PT": ("tasa_mercado_monetario", "porcentaje", 1),
}


def leer_crudos():
    """Lee el CSV crudo con solo las columnas que se usan."""
    return pd.read_csv(ARCHIVO_ENTRADA, usecols=["DATAFLOW", "INDICATOR", "TIME_PERIOD", "OBS_VALUE"])


def a_fecha(periodo):
    """Convierte el periodo del FMI a fecha: "2026-M07" -> 2026-07-01."""
    return pd.to_datetime(periodo.str.replace("-M", "-") + "-01")


def al_esquema_comun(fmi):
    """Da a las series las columnas de la tabla observaciones."""
    nombre, unidad, divisor = zip(*fmi["INDICATOR"].map(INDICADORES))

    limpia = pd.DataFrame({
        "fecha": a_fecha(fmi["TIME_PERIOD"]),
        "pais": "Colombia",
        "indicador": nombre,
        "valor": (fmi["OBS_VALUE"] / divisor).round(2),
        "unidad": unidad,
        "fuente": "FMI",
        "serie_id": fmi["DATAFLOW"].str.extract(r":(\w+)\(")[0] + "/" + fmi["INDICATOR"],
    })

    limpia = limpia[limpia["fecha"] >= FECHA_INICIO]
    limpia["fecha"] = limpia["fecha"].dt.date
    return limpia.sort_values(["indicador", "fecha"])


def main():
    fmi = leer_crudos()
    limpia = al_esquema_comun(fmi)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    limpia.to_csv(ARCHIVO_SALIDA, index=False)

    resumen = limpia.groupby("indicador")["fecha"].agg(["count", "min", "max"])
    for indicador, fila in resumen.iterrows():
        print(f"{indicador}: {fila['count']} meses (desde {fila['min']} hasta {fila['max']})")
    print(f"Guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
