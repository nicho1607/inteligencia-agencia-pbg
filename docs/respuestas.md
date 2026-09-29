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
Ver `docs/metricas.md`. Prioricé las que un dueño usa para decidir: cuántas conversaciones reales
hubo, qué tan confiable es el "answered", conversión sobre conversaciones reales, y desempeño por
agente y campaña. Cada una declara definición, fórmula, fuente, filtros y límites.

**¿Cómo manejaste los datos poco confiables?**
Definí filtros de confiabilidad (duplicados, timestamps imposibles, fechas futuras, duración
negativa) que se aplican en cascada y se registran en `docs/datos_no_confiables.md` y en el panel de
calidad del dashboard. "answered" se conserva pero no cuenta como conversación salvo que cumpla la
regla de confirmación.

**¿Qué asumiste?**
Que "disposición humana apropiada" son los resultados que implican contacto humano real
(cita, venta, callback, no-interesado, número equivocado). Que el umbral de 4 turnos aplica sobre
turnos con speaker válido. Que "hoy" es 2026-09-29 para detectar fechas futuras.

**¿Qué harías con más tiempo?**
Filtros interactivos, tiempo de primera respuesta, ROI por campaña con costos, validación de esquema
y CI. Ver README.
