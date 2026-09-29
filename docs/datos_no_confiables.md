# Registro de datos no confiables

> Generado por `metrics.py::write_unreliable_report`. Las reglas de negocio salen de
> `data/data_notes.json`, no están hardcodeadas.

- Filas crudas: **210**
- Filas de agentes reales analizadas: **196**

| Motivo | Conteo | Descripción |
|---|---|---|
| `cuentas_no_persona` | 14 | Filas de cuentas que no son personas reales (p. ej. 'PBG Billing'), excluidas de los rankings de agentes. |
| `fechas_no_parseables` | 0 | timestamp_utc no interpretable como fecha. |
| `answered_sin_dialogo` | 66 | carrier_answered > 0 pero speaker_turns = 0: el carrier dice 'contestada' sin diálogo. No cuenta como conversación. |
| `callback_marcado_como_cita` | 12 | disposition = callback pero appointment_type = appointment. Un callback NO es una cita (data_notes.json). |
| `ventas_mayores_que_solicitudes` | 48 | sales > applications: dato de negocio inconsistente, se marca para revisión. |

## Avisos de calidad (no retiran filas, pero afectan la interpretación)

- **Teléfono compartido:** ['Carlos', 'Diego'] comparten línea; sus métricas de contacto pueden estar mezcladas.
- **Nota del dataset:** Callbacks are not appointments.
- **Overrides de premium:** [{'agent': 'Maria', 'document_premium': 65, 'screen_premium': 89}]