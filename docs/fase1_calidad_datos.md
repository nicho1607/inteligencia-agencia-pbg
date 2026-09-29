# Fase 1 — Exploración y calidad de datos (dataset real)

> Datos sintéticos provistos por el reto. Perfilado con `data/profile_real.py` (solo lectura).

## Qué hay en el paquete

- **`data/activity.csv`** — 210 filas, **agregado por franja horaria + agente**
  (15 agentes × 14 franjas). Columnas: `timestamp_utc, agent, dials, carrier_answered,
  speaker_turns, disposition, appointment_type, premium_screen, applications, sales, ad_spend`.
- **`data/data_notes.json`** — reglas de negocio y notas de calidad (zona horaria, cuenta
  no-persona, teléfono compartido, overrides de premium, "callbacks no son citas").

Rango de fechas: **2026-09-15 a 2026-09-28** (hora UTC). Zona real: America/New_York.

## Estado "limpio" del dato base

Sorprendentemente **no hay** nulos, duplicados de filas, timestamps imposibles ni valores
negativos. Los problemas no están en el formato: están en la **semántica** (contradicciones entre
columnas y con las reglas de negocio).

## Problemas de calidad detectados

| Problema | Conteo | Por qué importa |
|---|---|---|
| **`carrier_answered > 0` con `speaker_turns = 0`** | 71 (66 sin PBG Billing) | El carrier dice "contestada" sin diálogo: no es conversación |
| **`PBG Billing` tratado como agente** | 14 filas | Es `non_person_account`: contamina rankings de agentes |
| **`disposition=callback` marcado `appointment_type=appointment`** | 13 (12 sin PBG) | Un callback no es una cita (regla explícita) |
| **`disposition=appointment` con `appointment_type` inconsistente** | 23 (callback 12, none 11) | Solo 10 appointments son internamente consistentes |
| **`sales > applications`** | 51 (48 sin PBG) | Venta sin solicitud: dato imposible, se marca |
| **Teléfono compartido Carlos/Diego** | — | Métricas de contacto potencialmente mezcladas |

## Conclusión clave para el negocio

Dos señales que el dueño no debería usar tal cual:

1. **"answered" no es contacto real.** Solo el **61%** del volumen `answered` cae en franjas
   confirmadas como conversación. Reportar "answered" como conversaciones infla la actividad.
2. **El dato de citas es poco confiable.** Bajo la definición estricta (appointment +
   appointment_type=appointment) solo hay **7 citas reales**, porque `appointment_type` contradice a
   `disposition` en decenas de filas. No se debe fijar metas de citas sobre este campo hasta
   corregir el origen.

Ambas se muestran explícitamente en el panel de Calidad de Datos del dashboard, no se esconden.
