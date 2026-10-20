# 📋 Documento de decisiones

Registro de las decisiones del proyecto y su motivo. Cuando cambie algo, se agrega aquí.

## 🎯 Alcance

- **Países:** Colombia (Simón) y Argentina (Gonzalo).
- **Período:** desde enero de 2017. INDEC no tiene IPC nacional confiable entre fines de 2015 y 2016; la serie actual arranca en 2017.
- **Frecuencia:** mensual.

## 🛠️ Herramientas

- **Python** (pandas, requests) para descargar y limpiar los datos.
- **PostgreSQL** como base de datos. Cada uno lo instala en su computador y crea la tabla con `sql/crear_tablas.sql`.
- **Power BI** (Simon) y **Streamlit** (Gonzalo) para los dashboards.
- **Idioma:** todo el proyecto en español.

## 🗂️ Esquema común

Una fila por observación, en la tabla `observaciones`:

| Columna | Descripción |
|---|---|
| `fecha` | Primer día del mes |
| `pais` | `Colombia` o `Argentina` |
| `indicador` | Nombre del indicador |
| `valor` | Valor numérico |
| `unidad` | Unidad del valor |
| `fuente` | Institución que publica el dato |
| `serie_id` | Código de la serie en la fuente original |

- Las series diarias se llevan a mensual con el **promedio del mes**.
- **TRM:** el promedio se calcula sobre **todos los días del mes**, no solo los días hábiles. La TRM de un viernes sigue vigente el fin de semana, así que esos días toman el último valor publicado.
- **IPC:** se guarda el índice y, a partir de él, se calculan las dos inflaciones. Las variaciones se calculan con todo el histórico y después se filtra desde 2017; así la inflación anual de enero de 2017 sí tiene contra qué compararse (enero de 2016).
- **Redondeo del IPC:** el DANE calcula sus variaciones con más decimales que los que publica. Por eso las nuestras pueden diferir en ±0,01 puntos de las oficiales (por ejemplo, enero de 2017: 1,03 % frente a 1,02 %).
- **Meses incompletos:** el mes en curso no se incluye hasta que termina, para no comparar un promedio parcial con meses completos.
- **Recarga sin duplicados:** al cargar un indicador a PostgreSQL, primero se borran sus filas anteriores. El script de carga se puede ejecutar varias veces.

## 📊 Indicadores

| Indicador | 🇨🇴 Colombia | 🇦🇷 Argentina |
|---|---|---|
| Inflación (IPC) | DANE | INDEC |
| Tipo de cambio oficial | TRM (datos.gov.co) | BCRA |
| Tipo de cambio paralelo | No aplica | A definir (blue, MEP o CCL) |
| Tasa de interés | Tasa de política del Banco de la República | BADLAR o TAMAR (la tasa de política del BCRA cambió varias veces de instrumento) |
| Reservas internacionales | Banco de la República | BCRA |
| Agregado monetario | Banco de la República | BCRA |

### Nombres de los indicadores

Ambos países usan **exactamente los mismos nombres** en la columna `indicador`, para poder compararlos con un simple filtro:

| `indicador` | Qué es | `unidad` |
|---|---|---|
| `ipc` | Índice de precios al consumidor | índice (base propia de cada país) |
| `inflacion_mensual` | Variación % frente al mes anterior | porcentaje |
| `inflacion_anual` | Variación % frente al mismo mes del año anterior | porcentaje |
| `tipo_cambio_oficial` | Moneda local por dólar, promedio mensual | ej. COP por USD |

## 🔄 Flujo de trabajo

- Se trabaja en la rama `develop`. Cuando algo queda confirmado, se pasa a `main`.
- Daily de 15 minutos: qué hice, qué voy a hacer, qué me bloquea.

## ⏸️ Fuera del alcance (por ahora)

dbt, Docker, automatizaciones y modelo de proyección (VAR/ARIMA). Quedan como próximos pasos.
