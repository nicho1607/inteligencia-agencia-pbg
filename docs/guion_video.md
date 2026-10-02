# Guion de video — "Inteligencia para el Dueño de la Agencia"
# Duración: máximo 2 minutos

> Formato: lo que DICES está en texto normal. Lo que HACES en pantalla está en [corchetes].
> Por qué lo dices está en > cursiva — esto no lo lees, es tu contexto mental.
> No leas el guion de corrido. Úsalo para ensayar hasta que fluya solo.

---

## [0:00 – 0:18] EL PROBLEMA

**Qué hacer:** [Cámara encendida, tú en pantalla. No compartas todavía. Habla directo.]

**Qué decir:**
"El reto es darle al dueño de una agencia una vista rápida de qué está pasando en su negocio.
Pero hay una trampa: el dataset tiene un campo que se llama `carrier_answered`, que dice cuántas
llamadas contestó el carrier. Y la tentación es usarlo directamente como métrica de conversaciones.
El problema es que eso está **mal**. Que la línea conteste no significa que alguien habló."

> Por qué dices esto primero: estableces que entendiste el reto a fondo, no solo que hiciste una
> pantalla bonita. El jurado escucha esto y sabe que pensaste antes de codear.

---

## [0:18 – 0:42] LA DECISIÓN MÁS IMPORTANTE

**Qué hacer:** [Sigue en cámara. Puedes mostrar el archivo `metrics.py` abierto en el editor
o simplemente hablar — lo que te salga más natural.]

**Qué decir:**
"Entonces lo primero que hice, antes de tocar la UI, fue **definir qué es una conversación
confirmada**. Mi regla: una franja de actividad cuenta como confirmada si tiene una disposición
humana apropiada — es decir, `conversation` o `appointment` — o si tiene al menos 4 turnos de
diálogo. El estado del carrier no entra para nada.

Y las reglas de negocio no las inventé: el propio paquete de datos trae un archivo llamado
`data_notes.json`. Ahí dice que `PBG Billing` no es una persona real, sino una cuenta interna.
Dice que Carlos y Diego comparten teléfono. Dice explícitamente: los callbacks no son citas.
Así que leí esas reglas del JSON y las apliqué en el código. Si el negocio las cambia mañana,
solo cambian el archivo, no el código."

> Por qué esto importa: separar la lógica de la UI y leer las reglas del JSON en vez de
> hardcodearlas es la decisión que demuestra criterio de ingeniería, no solo de scripting.
> Es lo que más van a preguntarte.

---

## [0:42 – 1:30] LA DEMO

**Qué hacer:** [Comparte pantalla. Abre el dashboard en http://localhost:8501.
Mueve el mouse despacio, deja que la cámara y la pantalla se vean juntas si puedes.]

**Qué decir y señalar:**

**— KPIs (señala cada uno mientras hablas) —**
"Arriba tengo los cuatro KPIs principales. Cada uno tiene su definición exacta si pasas el cursor.
No son números sueltos, cada uno tiene su fórmula y su fuente documentadas."

**— Alerta amarilla (señálala) —**
"Esta alerta es el hallazgo más importante: de todas las llamadas que el carrier marcó como
'answered', solo el **61%** caen en franjas que son conversación confirmada. Si yo hubiera
reportado 'answered' como conversaciones, le estaría mintiendo al dueño. Le estaría diciendo que
tiene un 39% más de actividad de la que realmente tuvo."

**— Aviso azul (señálalo) —**
"Y este aviso dice que el dato de citas es poco confiable. Bajo mi definición estricta — que
`disposition` sea appointment Y que `appointment_type` también sea appointment — solo hay
**7 citas reales** en todo el dataset. El campo `appointment_type` contradice a `disposition` en
decenas de filas. En vez de esconder ese problema, lo muestro. No puedes fijar metas de citas
sobre un campo roto."

**— Tendencia (señala el gráfico) —**
"Acá la tendencia de confirmadas, ventas y citas por día, ya convertida a la zona horaria
correcta: America/New_York."

**— Tabla de agentes (señala) —**
"Desglose por agente. Nótese que `PBG Billing` no aparece aquí — lo excluí porque el
`data_notes.json` dice que es una cuenta interna, no una persona real. Si lo dejara, contaminaría
los rankings."

**— Panel de calidad (señala la parte de abajo) —**
"Y abajo, el panel de calidad de datos. 210 filas crudas, 196 de agentes reales. 66 franjas con
el carrier contestado pero cero turnos de diálogo. 12 callbacks marcados como cita que no lo son.
Todo visible, nada escondido."

> Por qué recorres en este orden: primero el número que sorprende (la brecha del 61%), luego
> el dato roto (citas), luego el contexto (tendencia, agentes), luego la transparencia (calidad).
> Es el orden de mayor a menor impacto para el dueño.

---

## [1:30 – 1:48] LA LÓGICA ESTÁ PROBADA

**Qué hacer:** [Abre una terminal. Corre el comando.]

```powershell
python -m pytest tests\ -q
```

**Qué decir:**
"La lógica de las métricas está separada de la interfaz en un módulo independiente llamado
`metrics.py`. Eso me permite testearlo sin arrancar el dashboard. Tengo 5 tests: uno para cada
camino de la regla de confirmación, uno que prueba que el callback no cuenta como cita, y uno
que verifica que la cuenta no-persona se excluye. Todos pasan."

> Por qué muestras los tests: es la prueba de que tu definición no es suposición, es código
> verificable. Eso separa un junior con criterio de uno que solo hace pantallas.

---

## [1:48 – 2:00] QUÉ SIGUE

**Qué hacer:** [Vuelve a la cámara o quédate en la terminal.]

**Qué decir:**
"Con más tiempo, lo primero sería reconciliar `disposition` contra `appointment_type` con el
equipo de datos para arreglar el origen del problema de las citas, no solo marcarlo. Después,
filtros interactivos y validación de esquema para que esto no se rompa si cambian el CSV.
El core ya funciona y responde la pregunta del dueño con números en los que puede confiar."

> Terminas con qué harías después porque demuestra que ves más allá del reto, que piensas
> en producción, no solo en entregar.

---

## NOTAS PARA GRABAR

- **Ensaya 2 veces** antes de grabar. La primera vez siempre sale larga (2:30+). La segunda
  ya sabes dónde acortar.
- Si pasas de 2 minutos, **corta el bloque de tests** y solo di "la lógica está cubierta con
  tests" sin mostrar la terminal. Recuperas 18 segundos.
- Habla **despacio en las partes técnicas** (la regla de confirmación, la brecha del 61%),
  rápido en las transiciones.
- No digas "básicamente" ni "simplemente". Cada cosa que muestras tiene peso, no la minimices.
- Si te travas, la frase de rescate es: **"La idea central es que answered no prueba
  conversación, y el dashboard lo hace visible."** Funciona en cualquier punto del video.
