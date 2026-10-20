"""
Gráfico de la TRM mensual, leyendo los datos desde PostgreSQL.

Cierra el primer hito del proyecto: la serie hizo el recorrido completo
(descarga -> limpieza -> base de datos -> gráfico).

Salida: analisis/graficos/trm_colombia.png
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO_SALIDA = RAIZ / "analisis" / "graficos" / "trm_colombia.png"

# Colores del gráfico
COLOR_LINEA = "#2a78d6"
COLOR_TEXTO = "#0b0b0b"
COLOR_TEXTO_SUAVE = "#52514e"
COLOR_GRILLA = "#e4e3df"
COLOR_FONDO = "#fcfcfb"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

CONSULTA = """
    SELECT fecha, valor
    FROM observaciones
    WHERE pais = 'Colombia'
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


def graficar(trm):
    """Dibuja la serie y marca el valor máximo y el último dato."""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    fig.patch.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)

    ax.plot(trm["fecha"], trm["valor"], color=COLOR_LINEA, linewidth=2)

    # Etiquetas solo en dos puntos clave: el máximo y el último dato
    maximo = trm.loc[trm["valor"].idxmax()]
    ultimo = trm.iloc[-1]
    for punto, texto in [(maximo, "Máximo"), (ultimo, "Último dato")]:
        ax.scatter(punto["fecha"], punto["valor"], color=COLOR_LINEA, s=40, zorder=3,
                   edgecolor=COLOR_FONDO, linewidth=2)
        mes = f"{MESES[punto['fecha'].month - 1]} {punto['fecha'].year}"
        ax.annotate(
            f"{texto}\n{mes}: ${punto['valor']:,.0f}".replace(",", "."),
            xy=(punto["fecha"], punto["valor"]),
            xytext=(0, 12), textcoords="offset points",
            ha="center", va="bottom", fontsize=9, color=COLOR_TEXTO,
        )

    # Títulos
    fig.text(0.06, 0.95, "TRM promedio mensual, 2017 – 2026",
             fontsize=14, fontweight="bold", color=COLOR_TEXTO)
    fig.text(0.06, 0.90, "Pesos colombianos por dólar · Fuente: Superintendencia Financiera (datos.gov.co)",
             fontsize=9, color=COLOR_TEXTO_SUAVE)

    # Ejes discretos: sin bordes arriba ni a la derecha, grilla suave
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_GRILLA)
    ax.grid(axis="y", color=COLOR_GRILLA, linewidth=0.8)
    ax.tick_params(colors=COLOR_TEXTO_SUAVE, labelsize=9, length=0)
    ax.yaxis.set_major_formatter(lambda valor, _: f"${valor:,.0f}".replace(",", "."))
    ax.set_ylim(top=trm["valor"].max() * 1.12)  # espacio para la etiqueta del máximo

    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.08)
    return fig


def main():
    engine = conectar()
    trm = pd.read_sql(CONSULTA, engine, parse_dates=["fecha"])

    fig = graficar(trm)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ARCHIVO_SALIDA, facecolor=COLOR_FONDO)

    print(f"Gráfico guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
