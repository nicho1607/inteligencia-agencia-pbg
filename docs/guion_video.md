# Guion de video (máximo 2 minutos)

Problema → decisiones → demo → qué sigue. Ritmo ágil.

---

**[0:00–0:20] Problema**

"El dueño de una agencia quiere saber en 10 segundos qué pasa en su negocio, pero no todos los datos
son confiables. El caso más claro: el carrier marca llamadas como 'answered', pero eso solo dice que
la línea se conectó, no que hubo conversación."

**[0:20–0:45] Decisiones**

"Definí actividad **confirmada** con una regla explícita: disposición humana, o al menos 4 turnos de
diálogo. El carrier no cuenta. Y las reglas de negocio no las inventé: las leí del propio paquete,
del `data_notes.json` — por ejemplo, 'PBG Billing' no es una persona, así que lo saco de los
rankings, y un callback nunca cuenta como cita."

**[0:45–1:35] Demo (pantalla)**

- "Arriba los KPIs, cada uno con su definición en el tooltip."
- "Mira esta alerta: solo el 61% de las llamadas 'answered' son conversación confirmada. Tratar
  'answered' como conversaciones infla la actividad."
- "Y este aviso: bajo la definición estricta solo hay 7 citas reales, porque el campo
  appointment_type contradice a disposition. Así que el dato de citas lo marco como no confiable en
  vez de esconderlo."
- "Tendencia por día, desglose por agente y por disposición, y abajo el panel de calidad de datos:
  210 filas crudas, 196 de agentes reales, y cada problema detectado con su conteo."

**[1:35–1:50] Confianza / tests**

"La lógica está separada de la interfaz y cubierta con 5 tests: la regla de confirmación, la
exclusión de la cuenta no-persona y que un callback no es cita. Corre con un solo comando."

**[1:50–2:00] Qué sigue**

"Con más tiempo reconciliaría disposition contra appointment_type con el equipo de datos, y añadiría
filtros por fecha y agente. Pero lo esencial ya responde la pregunta del dueño con datos en los que
puede confiar, y dice claramente en cuáles no."
