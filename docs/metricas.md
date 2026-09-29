# Definición de métricas

> **Principio rector:** no confiamos ciegamente en los datos. Cada métrica declara su
> definición, fórmula, fuente, filtros de confiabilidad y limitaciones **antes** de mostrarse.
> Lo no confiable se excluye o se marca y se registra (ver `docs/datos_no_confiables.md`).
> Las reglas de negocio salen de `data/data_notes.json`, **no** están hardcodeadas.

## El dato

`data/activity.csv` está **agregado por franja horaria + agente** (no una fila por conversación).
Cada fila resume una hora de un agente:

| Columna | Descripción |
|---|---|
| `timestamp_utc` | Inicio de la franja (UTC; la zona real es America/New_York) |
| `agent` | Agente (incluye la cuenta no-persona `PBG Billing`) |
| `dials` | Llamadas marcadas |
| `carrier_answered` | Llamadas que el carrier reportó como contestadas |
| `speaker_turns` | Turnos de habla en la franja |
| `disposition` | Resultado: conversation, appointment, callback, voicemail, no_answer |
| `appointment_type` | appointment / callback / none |
| `premium_screen` | Prima de la pantalla |
| `applications` | Solicitudes |
| `sales` | Ventas |
| `ad_spend` | Gasto publicitario |

## Concepto central: actividad CONFIRMADA

Como el dato es agregado, aplicamos la regla del reto a nivel de franja. Una franja cuenta como
**confirmada** si:

- **(a)** su `disposition` es una **disposición humana apropiada**: `conversation` o `appointment`, **o**
- **(b)** tiene **≥ 4 `speaker_turns`**.

`carrier_answered` **no** entra en la regla: contestar no prueba que hubo conversación.
Implementado en `metrics.py::is_confirmed_row`.

## Reglas de negocio aplicadas (de `data_notes.json`)

- **`PBG Billing` es `non_person_account`** → se excluye de los rankings de agentes.
- **"Callbacks are not appointments"** → una `disposition=callback` **nunca** cuenta como cita,
  aunque `appointment_type` diga `appointment`.
- **Teléfono compartido `[Carlos, Diego]`** → se advierte: sus métricas de contacto pueden mezclarse.
- **Override de premium para Maria** → documentado; no altera los conteos de negocio.

## Filtros / marcas de confiabilidad

| Señal | Tratamiento |
|---|---|
| `carrier_answered > 0` y `speaker_turns = 0` | No cuenta como conversación; se registra |
| `disposition = callback` con `appointment_type = appointment` | Excluido de citas reales; se registra |
| `sales > applications` (imposible) | Se marca para revisión |
| Cuenta no-persona | Excluida de agentes |

---

## Métricas para el dueño de la agencia

### 1. Tasa de contacto real vs. "answered"
- **Definición:** qué parte del volumen `answered` ocurre en franjas que además son conversación confirmada.
- **Fórmula:** `sum(carrier_answered en confirmadas) / sum(carrier_answered)`
- **Fuente:** `carrier_answered` + regla de confirmación.
- **Limitaciones:** es agregado; no distingue conversación por llamada individual. Mide la brecha señal-realidad.

### 2. Ventas y costo por venta
- **Definición:** ventas totales y gasto publicitario por venta.
- **Fórmula:** `sum(sales)`; `sum(ad_spend) / sum(sales)`
- **Fuente:** `sales`, `ad_spend`.
- **Limitaciones:** no atribuye el gasto a la venta específica; es promedio agregado.

### 3. Citas reales y costo por cita
- **Definición:** franjas con cita genuina (disposition=appointment **y** appointment_type=appointment).
- **Fórmula:** `count(is_real_appointment)`; `sum(ad_spend)/citas_reales`
- **Fuente:** `disposition`, `appointment_type`.
- **Limitaciones:** el campo `appointment_type` es inconsistente con `disposition`, así que el conteo
  estricto es bajo y **poco confiable** para fijar metas (se advierte en el dashboard).

### 4. Franjas confirmadas
- **Definición:** franjas hora-agente que cumplen la regla de confirmación.
- **Fórmula:** `count(is_confirmed)` sobre agentes reales.
- **Limitaciones:** unidad = franja, no conversación individual.

### 5. Desempeño por agente
- **Definición:** por agente: dials, answered, franjas confirmadas, citas reales, ventas, gasto, costo por venta.
- **Fuente:** agregaciones por `agent` (sin cuentas no-persona).
- **Limitaciones:** no normaliza por leads asignados; Carlos/Diego comparten línea (contacto no comparable).

### 6. Distribución por disposición
- **Definición:** conteo de franjas por `disposition`.
- **Limitaciones:** describe el mix de resultados, no su calidad.

### 7. Tendencia por día (hora local)
- **Definición:** confirmadas, ventas y citas reales por día en America/New_York.
- **Fórmula:** `GROUP BY date(ts_local)`.
- **Limitaciones:** solo 14 días de datos; tendencias cortas son ruidosas.

### 8. Salud de datos
- **Definición:** filas de agentes reales analizadas vs. crudas, y conteo de cada señal de calidad.
- **Fuente:** el registro de exclusiones/marcas.
- **Limitaciones:** indicador de higiene del dato, no de negocio.
