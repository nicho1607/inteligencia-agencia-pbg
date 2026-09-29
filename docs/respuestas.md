# Respuestas escritas solicitadas (plantilla)

> Pega aquí el enunciado exacto de cada pregunta cuando lo tengas y completa la respuesta.
> Dejo abajo borradores para las preguntas típicas de este tipo de reto; ajústalos al enunciado real.

---

## Pregunta 1: [pegar enunciado]

**Respuesta:**
_(pendiente)_

---

## Pregunta 2: [pegar enunciado]

**Respuesta:**
_(pendiente)_

---

## Pregunta 3: [pegar enunciado]

**Respuesta:**
_(pendiente)_

---

## Borradores reutilizables (por si aplican)

**¿Qué métricas definiste y por qué?**
Ver `docs/metricas.md`. Prioricé las que un dueño usa para decidir: tasa de contacto real vs.
"answered", ventas y costo por venta, citas reales y su costo, franjas confirmadas, desempeño por
agente y distribución por disposición. Cada una declara definición, fórmula, fuente, filtros y
límites.

**¿Cómo manejaste los datos poco confiables?**
Las reglas de negocio salen de `data/data_notes.json` (cuenta no-persona, callback no es cita,
teléfono compartido). Marco/excluyo: 'answered' sin diálogo (no cuenta como conversación), callbacks
marcados como cita (fuera de citas reales), ventas>solicitudes (revisión), y la cuenta 'PBG Billing'
(fuera de rankings). Todo queda en `docs/datos_no_confiables.md` y en el panel de calidad.

**¿Qué asumiste?**
Que "disposición humana apropiada" son `conversation` y `appointment`. Que la regla de 4 turnos
aplica sobre `speaker_turns` de la franja (el dato es agregado por hora/agente, no por conversación).
Que una cita solo es real si `disposition=appointment` y `appointment_type=appointment`.

**¿Qué harías con más tiempo?**
Reconciliar `disposition` vs `appointment_type` con el equipo de datos, filtros interactivos,
normalizar por leads asignados, validación de esquema y CI. Ver README.
