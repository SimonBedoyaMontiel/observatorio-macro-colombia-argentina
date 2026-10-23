-- Crea la tabla principal del observatorio.
-- Formato largo: una fila por observación (fecha + país + indicador).
-- Se corre una sola vez en una base vacía.

CREATE TABLE IF NOT EXISTS observaciones (
    fecha      DATE         NOT NULL,  -- primer día del mes (ej. 2017-01-01)
    pais       VARCHAR(20)  NOT NULL,  -- 'Colombia' o 'Argentina'
    indicador  VARCHAR(50)  NOT NULL,  -- ej. 'tipo_cambio_oficial', 'ipc'
    valor      NUMERIC      NOT NULL,
    unidad     VARCHAR(30)  NOT NULL,  -- ej. 'COP por USD', 'indice', 'porcentaje'
    fuente     VARCHAR(100) NOT NULL,  -- ej. 'Banco de la República'
    serie_id   VARCHAR(100),           -- código de la serie en la fuente original
    PRIMARY KEY (fecha, pais, indicador)  -- evita cargar dos veces el mismo dato
);

SELECT pais, indicador, COUNT(*) AS meses, MIN(fecha) AS desde, MAX(fecha) AS hasta
FROM observaciones
GROUP BY pais, indicador
ORDER BY pais, indicador;

SELECT fecha, indicador, valor
FROM observaciones
WHERE pais = 'Argentina'
  AND fecha IN ('2023-11-01', '2023-12-01', '2024-01-01')
  AND indicador IN ('inflacion_mensual', 'tipo_cambio_oficial', 'tasa_mercado_monetario')
ORDER BY indicador, fecha;