# Registro de datos no confiables

> Generado automáticamente por `metrics.py::write_unreliable_report`.
> Las exclusiones se aplican **en cascada** (en el orden listado), por eso un conteo
> puede ser menor que en el perfilado crudo: una fila ya retirada por un filtro previo
> no se vuelve a contar. El objetivo es no doble-contar exclusiones.

- Filas crudas: **627**
- Filas válidas para análisis: **605**
- Filas excluidas: **22** (3.5%)

| Motivo de exclusión | Conteo | Descripción |
|---|---|---|
| `duplicados_conversation_id` | 12 | Filas duplicadas por conversation_id; se conserva la primera. |
| `fechas_no_parseables` | 0 | started_at o ended_at no se pudieron interpretar como fecha. |
| `ended_antes_de_started` | 6 | ended_at anterior a started_at (timestamp imposible). |
| `fechas_futuras` | 4 | started_at posterior a la fecha de análisis (2026-09-29). |
| `duracion_negativa` | 0 | duration_seconds menor que cero (valor imposible). |

## Nota sobre `answered`

Las llamadas con `carrier_status = answered` NO se excluyen del dataset, pero **no se cuentan como conversación** salvo que cumplan la regla de confirmación. La brecha entre 'answered' y 'confirmadas' se muestra explícitamente en el dashboard (KPI de contacto real).
