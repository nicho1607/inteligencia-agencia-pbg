"""
Dashboard "Inteligencia para el Dueño de la Agencia".

Responde en 10 segundos: "¿qué está pasando realmente en mi negocio?"
  - KPIs arriba (definición en tooltip).
  - Tendencia en el tiempo.
  - Desglose por agente y por disposición.
  - Panel de Calidad de Datos: qué es confiable, qué se excluyó y qué se marcó.

Datos: data/activity.csv (agregado por hora/agente). Reglas de negocio: data/data_notes.json.
Correr:  python -m streamlit run app.py
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
    raw = metrics.load_raw()
    notes = metrics.load_notes()
    df, exclusions, flags = metrics.clean(raw, notes)
    kpis = metrics.compute_kpis(df)
    return df, exclusions, flags, kpis


df, exclusions, flags, kpis = load()

st.title("📞 Inteligencia para el Dueño de la Agencia")
st.caption(
    "Datos **sintéticos** agregados por hora y agente. Una franja se cuenta como actividad "
    "**confirmada** solo si su disposición es humana (conversation/appointment) **o** tiene "
    "≥ 4 turnos de speakers. Un carrier *answered* no prueba una conversación."
)

# ---------------------------------------------------------------------------
# KPIs con tooltips
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Tasa de contacto real",
    f"{kpis['tasa_contacto_real']*100:.1f}%",
    help="Del volumen que el carrier marcó 'answered', qué parte ocurre en franjas que además "
         "son conversación confirmada. Fórmula: answered_en_confirmadas / total_answered. "
         f"({kpis['answered_en_confirmadas']} de {kpis['total_answered']}).",
)
c2.metric(
    "Ventas",
    f"{kpis['ventas']}",
    help="Suma de la columna 'sales' de agentes reales. Costo por venta: "
         f"${kpis['costo_por_venta']} (gasto total / ventas).",
)
c3.metric(
    "Citas reales",
    f"{kpis['citas_reales']}",
    help="Solo cuando disposition='appointment' Y appointment_type='appointment'. "
         "Un callback NO es una cita (regla de data_notes.json). "
         f"Costo por cita real: ${kpis['costo_por_cita_real']}.",
)
c4.metric(
    "Franjas confirmadas",
    f"{kpis['franjas_confirmadas']} / {kpis['franjas_totales']}",
    help="Franjas hora-agente que cumplen la regla de confirmación, sobre el total de "
         "franjas de agentes reales.",
)

# Brecha answered vs. real (el punto del reto)
gap = kpis["total_answered"] - kpis["answered_en_confirmadas"]
if kpis["total_answered"]:
    st.warning(
        f"⚠️ **{gap}** llamadas 'answered' ocurren fuera de conversaciones confirmadas "
        f"({gap / kpis['total_answered']*100:.0f}% del total 'answered'). "
        "Tratar 'answered' como conversación sobreestimaría la actividad real."
    )

# Aviso sobre citas si el dato es escaso/inconsistente
if kpis["citas_reales"] <= kpis["ventas"] / 5:
    st.info(
        f"ℹ️ Solo **{kpis['citas_reales']}** citas cumplen la definición estricta (appointment + "
        "appointment_type=appointment). El campo `appointment_type` es inconsistente con "
        "`disposition`, así que el dato de citas es **poco confiable** y no se debe usar para metas."
    )

st.divider()

# ---------------------------------------------------------------------------
# Tendencia + disposición
# ---------------------------------------------------------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("Tendencia por día (hora local)")
    trend = metrics.trend_by_day(df).set_index("date")
    st.line_chart(trend, height=280)
    st.caption("Franjas confirmadas, ventas y citas reales por día (America/New_York).")

with right:
    st.subheader("Resultados por disposición")
    st.dataframe(metrics.by_disposition(df), hide_index=True, use_container_width=True)
    st.caption("Distribución de la columna disposition en franjas de agentes reales.")

st.subheader("Desempeño por agente")
agent = metrics.by_agent(df)
st.dataframe(agent, hide_index=True, use_container_width=True)
st.bar_chart(agent.set_index("agent"), y="ventas", height=260)

# Aviso de teléfono compartido
pair = flags.get("telefono_compartido")
if pair:
    st.caption(
        f"⚠️ {pair[0]} y {pair[1]} comparten línea telefónica: sus métricas de contacto "
        "(dials/answered) pueden estar mezcladas y no son directamente comparables."
    )

st.divider()

# ---------------------------------------------------------------------------
# Panel de Calidad de Datos
# ---------------------------------------------------------------------------
st.subheader("🔎 Calidad de datos: qué es confiable y qué no")

q1, q2, q3 = st.columns(3)
q1.metric("Filas crudas", exclusions["_total_crudo"])
q2.metric("Agentes reales (filas)", exclusions["_filas_analizadas"])
q3.metric("Cuentas no-persona excluidas", exclusions["cuentas_no_persona"])

rows = [
    {"Señal de calidad": "carrier 'answered' sin diálogo (turns=0)",
     "Conteo": exclusions["answered_sin_dialogo"],
     "Efecto": "No cuenta como conversación"},
    {"Señal de calidad": "callback marcado como cita",
     "Conteo": exclusions["callback_marcado_como_cita"],
     "Efecto": "Excluido de citas reales"},
    {"Señal de calidad": "ventas > solicitudes (imposible)",
     "Conteo": exclusions["ventas_mayores_que_solicitudes"],
     "Efecto": "Marcado para revisión"},
    {"Señal de calidad": "cuentas no-persona (PBG Billing)",
     "Conteo": exclusions["cuentas_no_persona"],
     "Efecto": "Excluido de rankings de agentes"},
]
st.table(rows)
st.caption(
    "Reglas de negocio tomadas de `data/data_notes.json` (no hardcodeadas). Detalle en "
    "`docs/datos_no_confiables.md`. Nota del dataset: "
    f"\"{flags.get('nota', '')}\""
)
