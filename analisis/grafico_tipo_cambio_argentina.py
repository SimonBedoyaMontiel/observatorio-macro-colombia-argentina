"""
Gráfico del tipo de cambio oficial de Argentina, leyendo los datos desde PostgreSQL.

Igual que el de la TRM de Colombia, pero con una diferencia: el dólar en
Argentina pasó de unos 16 pesos (2017) a más de mil, así que en escala lineal
los primeros años se verían como una línea pegada al piso. Por eso el eje
vertical usa escala logarítmica: cada marca vale diez veces la anterior, y una
misma pendiente significa el mismo porcentaje de suba.

Salida: analisis/graficos/tipo_cambio_argentina.png
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_SALIDA = RAIZ / "analisis" / "graficos" / "tipo_cambio_argentina.png"

# Mismos colores que el gráfico de la TRM
COLOR_LINEA = "#2a78d6"
COLOR_TEXTO = "#0b0b0b"
COLOR_TEXTO_SUAVE = "#52514e"
COLOR_GRILLA = "#e4e3df"
COLOR_FONDO = "#fcfcfb"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

CONSULTA = """
    SELECT fecha, valor
    FROM observaciones
    WHERE pais = 'Argentina'
      AND indicador = 'tipo_cambio_oficial'
    ORDER BY fecha
"""


def conectar():
    """Crea la conexión a PostgreSQL con los datos del archivo .env."""
    load_dotenv(RAIZ / ".env")

    url = URL.create(
        "postgresql+psycopg2",
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return create_engine(url)


def formato_pesos(valor):
    """1500 -> '$1.500' (punto como separador de miles)."""
    return f"${valor:,.0f}".replace(",", ".")


def nombre_mes(fecha):
    return f"{MESES[fecha.month - 1]} {fecha.year}"


def graficar(tc):
    """Dibuja la serie y marca el mayor salto mensual y el último dato."""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    fig.patch.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)

    ax.plot(tc["fecha"], tc["valor"], color=COLOR_LINEA, linewidth=2)
    ax.set_yscale("log")

    # Dos puntos clave. En una serie que casi siempre sube, el máximo coincide con
    # el último dato; por eso se marca en cambio el mes de mayor suba respecto del anterior.
    suba = tc["valor"].pct_change()
    salto = tc.loc[suba.idxmax()]
    ultimo = tc.iloc[-1]
    puntos = [
        (salto, f"Mayor suba mensual\n{nombre_mes(salto['fecha'])}: +{suba.max() * 100:.0f}%", "right"),
        (ultimo, f"Último dato\n{nombre_mes(ultimo['fecha'])}: {formato_pesos(ultimo['valor'])}", "right"),
    ]
    for punto, texto, alineacion in puntos:
        ax.scatter(punto["fecha"], punto["valor"], color=COLOR_LINEA, s=40, zorder=3,
                   edgecolor=COLOR_FONDO, linewidth=2)
        ax.annotate(
            texto,
            xy=(punto["fecha"], punto["valor"]),
            xytext=(-8, 10) if alineacion == "right" else (8, 10), textcoords="offset points",
            ha=alineacion, va="bottom", fontsize=9, color=COLOR_TEXTO,
        )

    # Títulos
    desde, hasta = tc["fecha"].min().year, tc["fecha"].max().year
    fig.text(0.06, 0.95, f"Tipo de cambio oficial promedio mensual, {desde} – {hasta}",
             fontsize=14, fontweight="bold", color=COLOR_TEXTO)
    fig.text(0.06, 0.90, "Pesos argentinos por dólar (escala logarítmica) · Fuente: BCRA, tipo de cambio mayorista",
             fontsize=9, color=COLOR_TEXTO_SUAVE)

    # Ejes discretos: sin bordes arriba ni a la derecha, grilla suave
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_GRILLA)
    ax.grid(axis="y", which="major", color=COLOR_GRILLA, linewidth=0.8)
    ax.tick_params(colors=COLOR_TEXTO_SUAVE, labelsize=9, length=0)
    ax.tick_params(axis="y", which="minor", length=0, labelleft=False)
    ax.yaxis.set_major_formatter(lambda valor, _: formato_pesos(valor))
    ax.set_ylim(top=tc["valor"].max() * 2.2)  # espacio para las etiquetas

    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.08)
    return fig


def main():
    engine = conectar()
    tc = pd.read_sql(CONSULTA, engine, parse_dates=["fecha"])

    fig = graficar(tc)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ARCHIVO_SALIDA, facecolor=COLOR_FONDO)

    print(f"Gráfico guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
