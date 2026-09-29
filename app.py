"""
Dashboard "Inteligencia para el Dueño de la Agencia".

Responde en 10 segundos a: "¿qué está pasando realmente en mi negocio?"
  - KPIs arriba (con definición en tooltip).
  - Tendencia de conversaciones confirmadas.
  - Desglose por agente y por campaña.
  - Panel de Calidad de Datos: qué es confiable y qué se excluyó.

Correr con:  streamlit run app.py

Todos los datos son sintéticos.
"""

import streamlit as st

import metrics

st.set_page_config(
    page_title="Inteligencia para el Dueño de la Agencia",
    page_icon="📞",
    layout="wide",
)


@st.cache_data
def load():
    conv, turns = metrics.load_raw()
    df, exclusions = metrics.clean(conv, turns)
    kpis = metrics.compute_kpis(df, conv)
    return df, exclusions, kpis


df, exclusions, kpis = load()

st.title("📞 Inteligencia para el Dueño de la Agencia")
st.caption(
    "Datos **sintéticos**. Una conversación se cuenta solo si está **confirmada** "
    "(disposición humana apropiada **o** ≥ 4 turnos de speakers). "
    "Un estado de carrier *answered* no prueba una conversación."
)

# ---------------------------------------------------------------------------
# KPIs con tooltips (definición al pasar el cursor vía help=)
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Conversaciones confirmadas",
    f"{kpis['conversaciones_confirmadas']}",
    help="Conversaciones válidas que cumplen la regla: disposición humana apropiada "
         "O ≥ 4 turnos con speaker válido. Fuente: conversations + turns.",
)

c2.metric(
    "Tasa de contacto real",
    f"{kpis['tasa_contacto_real']*100:.1f}%",
    help="De las llamadas que el carrier marcó 'answered', qué proporción fueron "
         "conversación confirmada. Fórmula: confirmadas_entre_answered / answered_válidas. "
         f"({kpis['answered_confirmadas']} de {kpis['answered_total']} answered)",
)

c3.metric(
    "Tasa de conversión",
    f"{kpis['tasa_conversion']*100:.1f}%",
    help="Proporción de conversaciones confirmadas que terminaron en cita o venta. "
         "Fórmula: (appointment_set + sale_closed) / confirmadas. "
         f"({kpis['conversion_confirmadas']} de {kpis['conversaciones_confirmadas']})",
)

c4.metric(
    "Salud de los datos",
    f"{kpis['data_health']*100:.1f}%",
    help="Porcentaje de filas crudas que superan los filtros de confiabilidad "
         "(sin duplicados, sin timestamps imposibles, sin fechas futuras, sin duración negativa).",
)

# Alerta de la brecha answered vs real (el punto del reto)
gap = kpis["answered_total"] - kpis["answered_confirmadas"]
if kpis["answered_total"]:
    st.warning(
        f"⚠️ **{gap}** llamadas marcadas como *answered* NO son conversación confirmada "
        f"({gap / kpis['answered_total']*100:.0f}% del total 'answered'). "
        "Reportar 'answered' como conversaciones sobreestimaría la actividad real."
    )

st.divider()

# ---------------------------------------------------------------------------
# Tendencia + desgloses
# ---------------------------------------------------------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("Tendencia de conversaciones confirmadas")
    trend = metrics.trend_by_day(df).set_index("date")
    st.line_chart(trend, y="confirmadas", height=280)
    st.caption("Confirmadas por día. Las fechas futuras excluidas no aparecen aquí.")

with right:
    st.subheader("Por campaña")
    camp = metrics.by_campaign(df)
    st.dataframe(
        camp.rename(columns={"conversion_%": "conversión %"}),
        hide_index=True,
        use_container_width=True,
    )
    st.caption("Calidad de lead: confirmadas y conversión por campaña.")

st.subheader("Desempeño por agente")
agent = metrics.by_agent(df)
st.dataframe(
    agent.rename(columns={"conversion_%": "conversión %"}),
    hide_index=True,
    use_container_width=True,
)
st.bar_chart(agent.set_index("agent"), y="confirmadas", height=260)

st.divider()

# ---------------------------------------------------------------------------
# Panel de Calidad de Datos (qué es confiable y qué se excluyó)
# ---------------------------------------------------------------------------
st.subheader("🔎 Calidad de datos: qué es confiable y qué no")

total_raw = exclusions["_total_crudo"]
total_valid = exclusions["_total_valido"]
q1, q2, q3 = st.columns(3)
q1.metric("Filas crudas", total_raw)
q2.metric("Filas válidas (usadas)", total_valid)
q3.metric("Filas excluidas", total_raw - total_valid)

reason_labels = {
    "duplicados_conversation_id": "Duplicados (mismo conversation_id)",
    "fechas_no_parseables": "Fechas no interpretables",
    "ended_antes_de_started": "Fin anterior al inicio (imposible)",
    "fechas_futuras": "Fechas en el futuro",
    "duracion_negativa": "Duración negativa",
}
rows = [
    {"Motivo de exclusión": label, "Conteo": exclusions.get(key, 0)}
    for key, label in reason_labels.items()
]
st.table(rows)
st.caption(
    "Exclusiones aplicadas en cascada (no se doble-cuentan). Detalle en "
    "`docs/datos_no_confiables.md`. Además, las llamadas 'answered' que no cumplen la regla "
    "se conservan pero no se cuentan como conversación."
)
