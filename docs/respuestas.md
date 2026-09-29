# Respuestas escritas solicitadas

## ¿Qué construiste?

Un dashboard que responde en 10 segundos a "¿qué está pasando realmente en mi negocio?" para el
dueño de una agencia, con foco en **no confiar ciegamente en los datos**. Sobre el dataset real
(`activity.csv`, agregado por hora y agente) monté:

- Un pipeline de métricas (`metrics.py`) que limpia, aplica las reglas de negocio del propio paquete
  (`data_notes.json`) e implementa la regla de "actividad confirmada".
- Un dashboard Streamlit con KPIs (cada uno con su definición en tooltip), tendencia por día,
  desglose por agente y por disposición, y un **panel de calidad de datos** que muestra qué es
  confiable y qué se excluyó.
- 5 tests que fijan la lógica, un perfilado de datos y documentación completa (métricas, calidad,
  guion de video, screen sharing).

Decisión de producto central: `carrier_answered` no prueba una conversación. Solo el 61% del volumen
"answered" resultó ser conversación confirmada, y ese dato se muestra explícitamente en vez de
esconderse.

## ¿Cuál fue tu decisión técnica más importante y por qué?

**Separar la lógica pura (`metrics.py`) de la interfaz (`app.py`), y leer las reglas de negocio desde
`data_notes.json` en vez de hardcodearlas.**

La lógica queda testeable sin arrancar Streamlit (los 5 tests corren en <1s), y las definiciones de
negocio (qué cuenta como cita, qué cuenta es no-persona, quién comparte teléfono) viven en un archivo
que el negocio puede cambiar sin tocar el código. Eso hace las métricas defendibles y auditables:
cada número tiene una función, un test y una fuente. En un reto sobre confianza en los datos, esa
trazabilidad sostiene todo lo demás.

## ¿Qué podría romperse si esto entrara mañana a producción?

- **El esquema del CSV es un contrato implícito.** Si cambian un nombre de columna o el formato de
  `timestamp_utc`, el pipeline falla o calcula mal en silencio. Aún no hay validación de esquema.
- **Todo se lee en memoria.** Con 210 filas va perfecto; con millones no escala sin base de datos o
  Parquet/DuckDB.
- **La regla de "cita real" depende de un campo roto.** `appointment_type` contradice a `disposition`
  en decenas de filas; hoy lo marco como no confiable, pero si alguien lo usa para metas, decide mal.
- **El dato es agregado por hora**, así que hablo de "franjas confirmadas", no de conversaciones
  individuales; si se interpreta franja = conversación, se malentiende.
- **Zona horaria y solo 14 días de datos:** cualquier tendencia es ruidosa y sensible a la
  conversión UTC → America/New_York.

## Si tuvieras una semana adicional, ¿qué construirías después?

1. **Validación de esquema** (pandera) + CI que corra los tests en cada push: la red de seguridad
   contra el fallo silencioso en producción.
2. **Reconciliar `disposition` vs `appointment_type`** con el equipo de datos para arreglar el dato
   de citas en el origen, no solo marcarlo.
3. **Filtros interactivos** por fecha, agente y disposición, con drill-down por agente.
4. **Normalizar el desempeño por agente** por leads asignados y resolver el caso de línea compartida
   (Carlos/Diego).
5. **Persistencia** en DuckDB/Parquet con ingesta incremental.
6. **Alertas** cuando la salud de datos o la tasa de contacto real caen bajo un umbral.

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
