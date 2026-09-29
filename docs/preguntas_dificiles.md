# 5 preguntas difíciles (con respuestas sugeridas)

Para defender las decisiones en vivo. Respuestas cortas y directas.

---

### 1. Los datos vienen agregados por hora, no por conversación. ¿Cómo aplicas una regla que habla de "turnos de una conversación"?

La adapto al grano del dato y lo digo explícitamente: la unidad de análisis es la **franja
hora-agente**, no la conversación individual. Una franja cuenta como confirmada si su `disposition`
es humana o si tiene ≥4 `speaker_turns`. No pretendo tener conversaciones individuales que el dataset
no contiene; sería inventar granularidad. Con datos por llamada, la misma regla aplicaría por
conversación sin cambiar el concepto.

### 2. Reportas solo 7 citas reales pero hay 178 ventas. ¿No está roto tu cálculo?

No, está capturando un problema real del dato. Definí cita real como `disposition=appointment` **y**
`appointment_type=appointment`. Pero `appointment_type` contradice a `disposition` en decenas de
filas (callbacks marcados como appointment, appointments con tipo 'none'). Preferí una definición
estricta que **expone la inconsistencia** en vez de una laxa que la esconda. Por eso el dashboard
marca las citas como dato no confiable y recomienda no fijar metas sobre él hasta arreglar el origen.
Las ventas vienen de otra columna (`sales`) que no depende de ese campo roto.

### 3. Excluyes a "PBG Billing" y adviertes de Carlos/Diego. ¿No estás manipulando los datos a tu gusto?

Al contrario: no es criterio mío, viene del `data_notes.json` que acompaña al dataset. Ahí dice que
'PBG Billing' es `non_person_account` y que Carlos y Diego comparten teléfono. Leo esas reglas del
JSON en vez de hardcodearlas, así que si el negocio las cambia, cambia el archivo y no el código.
Todo lo que excluyo queda contado en el registro de datos no confiables; transparencia total.

### 4. ¿Por qué "answered" no cuenta como conversación si el carrier dice que contestaron?

Porque "answered" es una señal del carrier a nivel de línea telefónica, no evidencia de diálogo. En
los datos hay 66 franjas con `carrier_answered > 0` y `speaker_turns = 0`: contestaron pero nadie
habló (buzón, cuelgue, IVR). Contar eso como conversación sobreestima la actividad. Por eso la regla
usa disposición humana o densidad de turnos, y muestro la brecha (61%) en vez de ocultarla.

### 5. ¿Cómo sé que tu pipeline sirve si mañana cambian el formato de los datos?

Dos defensas. Una, la lógica está separada de la UI y cubierta con tests que fijan el
comportamiento: si alguien rompe la regla de confirmación o la exclusión de la cuenta no-persona, los
tests fallan. Dos, hice un perfilado explícito (`profile_real.py`) que valida esquema, nulos, rangos
y contradicciones; es lo primero que correría con un dataset nuevo para ver si las suposiciones
siguen siendo válidas antes de confiar en los números.
