<img src="https://capsule-render.vercel.app/api?type=rect&color=0B1220&height=180&text=Observatorio%20Macro-Financiero&fontSize=36&fontColor=ffffff&fontAlignY=42&desc=Colombia%20vs.%20Argentina%20%C2%B7%20Inflaci%C3%B3n%2C%20tipo%20de%20cambio%20y%20tasas&descAlignY=64&descSize=18&descColor=58a6ff" width="100%" alt="Observatorio Macro-Financiero: Colombia vs. Argentina">

<p align="center">
  <img src="https://img.shields.io/badge/Estado-En%20construcci%C3%B3n-F2C811?style=flat" alt="Estado: en construcción">
  <img src="https://img.shields.io/badge/Periodo-2017%20%E2%80%93%202026-58a6ff?style=flat" alt="Periodo 2017 a 2026">
  <img src="https://img.shields.io/badge/Datos-Fuentes%20oficiales-2ea44f?style=flat" alt="Datos de fuentes oficiales">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black" alt="Power BI">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit">
</p>

Proyecto en equipo que compara la inflación, el tipo de cambio, las tasas de interés y la política monetaria de **Colombia** y **Argentina** con datos oficiales: un pipeline en Python que descarga y limpia las series, una base común en PostgreSQL y dashboards en Power BI y Streamlit.

## 🎯 El problema en una línea

| 🇨🇴 Colombia | 🇦🇷 Argentina |
| --- | --- |
| Metas de inflación | Historial de alta inflación |
| Tipo de cambio flotante | Restricciones cambiarias y brecha con el dólar paralelo |

La pregunta: **¿cómo se comportan la inflación, el tipo de cambio y las tasas de interés en dos economías con regímenes tan distintos, y qué relaciones se pueden medir entre ellas?**

| | |
| --- | --- |
| 📅 **Periodo** | enero de 2017 a la fecha, frecuencia mensual |
| 📊 **Indicadores** | Inflación, tipo de cambio, tasas de interés, reservas internacionales y agregado monetario |
| 🏛️ **Fuentes** | DANE · datos.gov.co · FMI · BCRA · INDEC · datos.gob.ar |
| 🛠️ **Herramientas** | Python · pandas · PostgreSQL · SQL · Power BI · Streamlit |

## 🔄 Cómo fluyen los datos

```mermaid
flowchart LR
    A["🏛️ Fuentes<br/>DANE · datos.gov.co · FMI · BCRA · INDEC"] --> B["🐍 Ingesta<br/>Python · requests"]
    B --> C["📁 Datos crudos"]
    C --> D["🧹 Limpieza<br/>pandas"]
    D --> E[("🐘 PostgreSQL<br/>tabla común")]
    E --> F["📈 Power BI"]
    E --> G["🌐 Streamlit"]
```

## 🗺️ Cuatro fases, una por semana

| Fase | Qué se hace | Herramienta | Resultado | Estado |
| --- | --- | --- | --- | :---: |
| **1. Ingesta** | Descargar las series de las fuentes oficiales | Python · requests | Datos crudos de ambos países | 🔄 |
| **2. Limpieza y base de datos** | Llevar las series a un esquema común, controlar su calidad y cargarlas | pandas · PostgreSQL | Una tabla única y confiable | ⏳ |
| **3. Análisis** | Comparar inflación, tipo de cambio y tasas reales entre los dos países | SQL · pandas | Entre 4 y 6 hallazgos con su gráfico | ⏳ |
| **4. Dashboards** | Presentar los resultados de forma interactiva | Power BI · Streamlit | Dos dashboards y un informe | ⏳ |

✅ Terminada · 🔄 En curso · ⏳ Pendiente

## 📊 Indicadores

| Indicador | 🇨🇴 Colombia | 🇦🇷 Argentina |
| --- | --- | --- |
| 📈 Inflación (IPC) | DANE ✅ | INDEC ✅|
| 💱 Tipo de cambio oficial | TRM (datos.gov.co) ✅ | BCRA ✅ |
| 💵 Tipo de cambio paralelo | No aplica | A definir |
| 🏦 Tasa del mercado monetario | FMI ✅ | FMI ✅ |
| 🪙 Reservas internacionales | FMI ✅ | FMI ✅ |
| 💰 Dinero amplio | FMI ✅ | FMI ✅ |

✅ Serie descargada, limpia y cargada en PostgreSQL.

> 🌐 **Por qué el FMI:** el Banco de la República no tiene una API abierta para estas tres series. El FMI recibe los datos de cada banco central y los publica con **las mismas definiciones para todos los países**, lo que hace la comparación más justa.

Las decisiones detrás de cada elección están en [`docs/decisiones.md`](docs/decisiones.md).

## 📈 Primer vistazo

La primera serie que recorrió el pipeline completo (descarga → limpieza → PostgreSQL → gráfico):

<p align="center">
  <img src="analisis/graficos/trm_colombia.png" alt="TRM promedio mensual de Colombia entre 2017 y 2026, con un máximo en noviembre de 2022" width="100%">
</p>
<p align="center">
  <img src="analisis/graficos/tipo_cambio_argentina.png" alt="Tipo de cambio oficial promedio mensual de Argentina entre 2017 y 2026, en escala logarítmica" width="100%">
</p>
## 🔍 Hallazgos

> Se completarán en la fase 3.

## ▶️ Cómo ejecutarlo

```bash
git clone https://github.com/SimonBedoyaMontiel/observatorio-macro-colombia-argentina.git
cd observatorio-macro-colombia-argentina
pip install -r requirements.txt
```

Después:

1. Crear en PostgreSQL una base llamada `observatorio` y ejecutar [`sql/crear_tablas.sql`](sql/crear_tablas.sql).
2. Copiar `.env.example` como `.env` y completar los datos de conexión.
3. Ejecutar el pipeline:

```bash
python ingesta/colombia/descargar_trm.py   # 1. descarga
python ingesta/colombia/descargar_ipc.py
python ingesta/colombia/descargar_fmi.py
python ingesta/argentina/descargar_tipo_cambio.py
python ingesta/argentina/descargar_ipc.py
python ingesta/argentina/descargar_fmi.py
python limpieza/colombia/limpiar_trm.py    # 2. limpieza
python limpieza/colombia/limpiar_ipc.py
python limpieza/colombia/limpiar_fmi.py
python limpieza/argentina/limpiar_tipo_cambio.py
python limpieza/argentina/limpiar_ipc.py
python limpieza/argentina/limpiar_fmi.py
python carga/cargar_datos.py               # 3. carga a PostgreSQL
python analisis/grafico_trm.py             # 4. gráfico
```

## 📂 Estructura del repositorio

```
├── ingesta/
│   ├── colombia/            # Scripts de descarga de Colombia
│   └── argentina/           # Scripts de descarga de Argentina
├── limpieza/
│   ├── colombia/            # Scripts que llevan cada serie al esquema común
│   └── argentina/           
├── carga/
│   └── cargar_datos.py      # Carga los datos limpios a PostgreSQL
├── datos/
│   ├── crudos/              # Datos tal como vienen de la fuente
│   └── limpios/             # Datos en el esquema común
├── sql/
│   └── crear_tablas.sql     # Creación de la tabla de observaciones
├── analisis/
│   ├── grafico_trm.py       # Gráfico de la TRM desde PostgreSQL
│   └── graficos/            # Imágenes de los gráficos
├── dashboard/               # Dashboards en Power BI y Streamlit
├── docs/
│   └── decisiones.md        # Decisiones del proyecto y su motivo
├── .env.example             # Modelo de configuración de la base de datos
└── requirements.txt
```

## 👥 Equipo

| | País | Rol |
| --- | :---: | --- |
| **Simón Bedoya Montiel** | 🇨🇴 | Datos de Colombia · Dashboard en Power BI |
| **[Gonzalo Ducca](https://github.com/gonducca)** | 🇦🇷 | Datos de Argentina · Dashboard en Streamlit |

<p align="center">
  <a href="https://www.linkedin.com/in/simon-bedoya-montiel/">
    <img src="https://img.shields.io/badge/LinkedIn-Sim%C3%B3n%20Bedoya-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn de Simón Bedoya">
  </a>
  <a href="https://www.linkedin.com/in/gonzalo-ducca-b079011b2/">
    <img src="https://img.shields.io/badge/LinkedIn-Gonzalo%20Ducca-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn de Gonzalo Ducca">
  </a>
</p>
