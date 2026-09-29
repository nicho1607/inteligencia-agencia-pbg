# Definición de métricas

> **Principio rector:** no confiamos ciegamente en los datos. Cada métrica declara su
> definición, fórmula, fuente, filtros de confiabilidad y limitaciones **antes** de mostrarse.
> Los datos que no son confiables se excluyen y se registran (ver `docs/datos_no_confiables.md`,
> generado por `metrics.py`).

## Concepto central: Conversación CONFIRMADA

Una conversación se considera **confirmada** solo si cumple **al menos una** de estas condiciones:

- **(a) Disposición humana apropiada:** `disposition` ∈ {`appointment_set`, `sale_closed`,
  `callback_scheduled`, `not_interested`, `wrong_number`}. Estas marcan que un humano habló y
  registró un resultado.
- **(b) Densidad de diálogo:** la conversación tiene **≥ 4 turnos con speaker válido** (speaker no
  vacío) en `turns.csv`.

Un `carrier_status = "answered"` **NO** prueba una conversación por sí solo: el carrier solo dice
que la línea se conectó, no que hubo diálogo. Esta es la decisión más importante del reto.

Regla implementada en `metrics.py::is_confirmed_conversation`.

---

## Filtros base de confiabilidad (se aplican antes de cualquier métrica)

Una conversación entra al análisis solo si es **válida**:

1. `conversation_id` no duplicado (nos quedamos con la primera aparición).
2. `started_at` y `ended_at` parseables.
3. `ended_at >= started_at` (sin timestamps imposibles).
4. `started_at <= hoy` (2026-09-29) — sin fechas futuras.
5. `duration_seconds >= 0`.

Las filas que fallan estos filtros se **excluyen** y quedan contabilizadas en el registro de datos
no confiables. Los turnos con `speaker` vacío no cuentan para la regla (b).

---

## Métricas para el dueño de la agencia

### 1. Conversaciones confirmadas
- **Definición:** número de conversaciones válidas que cumplen la regla de confirmación.
- **Fórmula:** `COUNT(conversaciones válidas donde is_confirmed = true)`
- **Fuente:** `conversations.csv` + `turns.csv`.
- **Filtros:** filtros base + regla de confirmación.
- **Limitaciones:** depende de la calidad de `disposition` y del conteo de turnos; una conversación
  real muy corta sin disposición no se cuenta (falso negativo consciente y conservador).

### 2. Tasa de contacto real vs. "answered"
- **Definición:** qué proporción de las llamadas que el carrier marcó como `answered` fueron en
  realidad una conversación confirmada.
- **Fórmula:** `confirmadas_entre_answered / total_answered_válidas`
- **Fuente:** `carrier_status` + regla de confirmación.
- **Filtros:** filtros base; denominador = answered válidas.
- **Limitaciones:** mide la brecha entre la señal técnica y la realidad; no juzga la calidad del
  agente, solo la fiabilidad del estado del carrier.

### 3. Tasa de conversión (citas + ventas)
- **Definición:** proporción de conversaciones confirmadas que terminaron en cita o venta.
- **Fórmula:** `COUNT(disposition ∈ {appointment_set, sale_closed}) / conversaciones_confirmadas`
- **Fuente:** `disposition`.
- **Filtros:** solo sobre confirmadas (no sobre el total, para no diluir con no-contactos).
- **Limitaciones:** `appointment_set` no garantiza asistencia; `sale_closed` no incluye monto.

### 4. Citas y ventas por agente
- **Definición:** volumen de resultados de negocio (citas, ventas) por agente.
- **Fórmula:** `GROUP BY agent → COUNT(appointment_set), COUNT(sale_closed)` sobre confirmadas.
- **Fuente:** `agent` + `disposition`.
- **Limitaciones:** no normaliza por número de leads asignados; comparar con volumen, no solo total.

### 5. Rendimiento por campaña (calidad de lead)
- **Definición:** para cada campaña, conversaciones confirmadas y tasa de conversión.
- **Fórmula:** `GROUP BY campaign → confirmadas, conversión`
- **Fuente:** `campaign` + regla de confirmación + `disposition`.
- **Limitaciones:** no incluye costo por campaña, así que mide calidad de lead, no ROI.

### 6. Tendencia de conversaciones confirmadas en el tiempo
- **Definición:** conversaciones confirmadas por día.
- **Fórmula:** `GROUP BY date(started_at) → COUNT(confirmadas)`
- **Fuente:** `started_at` (válido) + regla de confirmación.
- **Limitaciones:** días con poco volumen son ruidosos; las fechas futuras excluidas ya no aparecen.

### 7. Duración media de conversaciones confirmadas
- **Definición:** duración promedio de las conversaciones confirmadas (proxy de profundidad).
- **Fórmula:** `AVG(duration_seconds)` sobre confirmadas con duración válida.
- **Fuente:** `duration_seconds`.
- **Limitaciones:** duración larga no siempre es mejor; excluye duraciones negativas.

### 8. Puntaje de calidad de datos (Data Health)
- **Definición:** porcentaje de filas del dataset crudo que superan los filtros base.
- **Fórmula:** `filas_válidas / filas_totales_crudas`
- **Fuente:** todo `conversations.csv`.
- **Limitaciones:** es un indicador de higiene del dato, no de negocio; sirve para saber cuánto
  podemos confiar en el resto del tablero.
