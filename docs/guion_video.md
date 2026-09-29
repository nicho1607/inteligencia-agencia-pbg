# Guion de video (máximo 2 minutos)

Objetivo: problema → decisiones → demo → qué sigue. Ritmo ágil, sin leer de corrido.

---

**[0:00–0:20] Problema**

"El dueño de una agencia quiere saber en 10 segundos qué está pasando en su negocio. El reto:
no podemos confiar ciegamente en los datos. El caso más claro: el carrier marca una llamada como
'answered', pero eso solo dice que la línea se conectó, no que hubo una conversación real."

**[0:20–0:45] Decisión central**

"Así que definí una regla explícita de **conversación confirmada**: cuenta solo si tiene una
disposición humana apropiada, o al menos 4 turnos de diálogo. Todo lo que no es confiable
—duplicados, fechas imposibles, duraciones negativas— se excluye y se registra. Nada se esconde."

**[0:45–1:30] Demo (pantalla)**

- "Arriba, los KPIs. Cada uno tiene su definición en el tooltip." (pasar el cursor)
- "Mira esta alerta: de 420 llamadas 'answered', 136 NO son conversación real. Reportar 'answered'
  como conversaciones infla la actividad un 32%."
- "Tendencia de confirmadas por día, desglose por campaña y por agente con citas y ventas."
- "Y aquí abajo, el panel de calidad de datos: 627 filas crudas, 605 válidas, con el detalle de
  qué excluí y por qué."

**[1:30–1:50] Confianza / tests**

"La lógica está separada de la interfaz y cubierta con tests: la regla de confirmación y las
exclusiones. Corre con un solo comando y se despliega gratis en Streamlit Cloud."

**[1:50–2:00] Qué sigue**

"Con más tiempo: filtros por fecha y agente, tiempo de primera respuesta, y ROI por campaña
sumando costos. Pero lo esencial ya responde la pregunta del dueño con datos en los que puede
confiar."
