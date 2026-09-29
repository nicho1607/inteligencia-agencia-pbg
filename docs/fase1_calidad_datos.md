# Fase 1 — Exploración y calidad de datos

> **Todos los datos son sintéticos.** No hay información real de clientes. El dataset se genera
> con `data/generate_data.py` (semilla fija = reproducible) e inyecta problemas de calidad a
> propósito para poner a prueba el pipeline. El perfilado se produce con `data/profile_data.py`.

## Qué hay en el paquete

Dos tablas relacionadas por `conversation_id`:

**`conversations.csv`** (627 filas) — una fila por conversación:

| Columna | Tipo observado | Descripción |
|---|---|---|
| `conversation_id` | texto | ID de la conversación (clave) |
| `agent` | texto | Agente asignado (6 valores) |
| `campaign` | texto | Campaña de origen (5 valores) |
| `carrier_status` | texto | Estado técnico de la telefonía: answered, no-answer, busy, failed, voicemail |
| `disposition` | texto (nullable) | Resultado marcado por el humano (puede estar vacío) |
| `started_at` | ISO datetime | Inicio |
| `ended_at` | ISO datetime | Fin |
| `duration_seconds` | número | Duración reportada |

**`turns.csv`** (2825 filas) — una fila por turno de habla:

| Columna | Tipo | Descripción |
|---|---|---|
| `conversation_id` | texto | FK a conversations |
| `turn_index` | entero | Orden del turno |
| `speaker` | texto | agent / customer (puede estar vacío) |
| `timestamp` | ISO datetime | Momento del turno |
| `text` | texto | Contenido (placeholder sintético) |

## Problemas de calidad detectados

| Problema | Conteo | Impacto en métricas |
|---|---|---|
| **Disposiciones vacías** | 146 (23%) | No se puede confiar en la disposición como única prueba de conversación |
| **Duplicados** por `conversation_id` | 12 ids (12 filas extra) | Inflan conteos y conversión si no se deduplican |
| **`ended_at` < `started_at`** | 7 | Timestamps imposibles; duración/tiempos no confiables en esas filas |
| **`started_at` en el futuro** (> 2026-09-29) | 5 | Fechas imposibles; contaminan tendencias |
| **Duración negativa** | 8 | Valor imposible; se excluye del cálculo de duración |
| **Turnos sin speaker** | 5 | No cuentan como turno válido para la regla de confirmación |
| **`answered` con 0 turnos** (contradicción dura) | 33 | "answered" NO prueba conversación |
| **`answered` con 1–3 turnos** (no concluyente) | 107 | Contactó pero no alcanza el umbral de ≥4 turnos |

Rango de fechas válidas: **2026-08-01** a la práctica; hay outliers hasta 2027-07 (los 5 futuros).

## Conclusión clave para el negocio

De **436** llamadas marcadas como `answered` por el carrier, **140** (33 con 0 turnos + 107 con 1–3
turnos) **no representan una conversación real** según la regla del reto. Reportar "answered" como
"conversaciones" sobreestimaría la actividad real en ~32%. Por eso definimos **conversación
confirmada** con una regla explícita (ver `docs/metricas.md`) y separamos siempre lo confiable de
lo no confiable en un panel de Calidad de Datos.
