"""
Lógica de métricas para "Inteligencia para el Dueño de la Agencia".

Dataset REAL: data/activity.csv es agregado por FRANJA HORARIA + AGENTE
(no una fila por conversación). Cada fila resume una ventana de una hora para un agente:
  timestamp_utc, agent, dials, carrier_answered, speaker_turns, disposition,
  appointment_type, premium_screen, applications, sales, ad_spend

Reglas de negocio vienen de data/data_notes.json y NO se hardcodean:
  - "PBG Billing" es non_person_account -> se excluye de rankings de agentes.
  - shared_phone_pair [Carlos, Diego] -> se advierte (métricas de contacto mezcladas).
  - "Callbacks are not appointments" -> un callback NUNCA cuenta como cita.
  - override de premium para Maria (se documenta; no cambia los conteos de negocio).

Módulo puro (sin UI) para poder testearlo. Definiciones 1:1 con docs/metricas.md.
"""

from __future__ import annotations

import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

# --- Constantes de dominio (coinciden con docs/metricas.md) ---

# Disposiciones que implican una conversación humana real con resultado.
HUMAN_DISPOSITIONS = {"conversation", "appointment"}
# Disposiciones que NO prueban conversación por sí solas.
NON_CONVERSATION_DISPOSITIONS = {"voicemail", "no_answer", "callback"}
MIN_TURNS_FOR_CONFIRMATION = 4

NUMERIC_COLS = [
    "dials", "carrier_answered", "speaker_turns",
    "premium_screen", "applications", "sales", "ad_spend",
]


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def load_notes(data_dir: str = DATA_DIR) -> dict:
    """Reglas de negocio externas (data_notes.json)."""
    with open(os.path.join(data_dir, "data_notes.json"), encoding="utf-8") as f:
        return json.load(f)


def load_raw(data_dir: str = DATA_DIR) -> pd.DataFrame:
    """Carga activity.csv sin limpiar."""
    return pd.read_csv(os.path.join(data_dir, "activity.csv"), dtype=str)


# ---------------------------------------------------------------------------
# Regla central: conversación confirmada (a nivel de fila agregada)
# ---------------------------------------------------------------------------

def is_confirmed_row(disposition, speaker_turns) -> bool:
    """
    Regla del reto adaptada al dato agregado. Una fila representa actividad confirmada si:
      (a) su disposition es una disposición humana apropiada (conversation / appointment), O
      (b) tiene >= 4 turnos de speakers.
    El estado del carrier (carrier_answered) NO se usa aquí: no prueba conversación.
    """
    disp = str(disposition or "").strip().lower()
    if disp in HUMAN_DISPOSITIONS:
        return True
    try:
        turns = float(speaker_turns)
    except (TypeError, ValueError):
        turns = 0
    return turns >= MIN_TURNS_FOR_CONFIRMATION


# ---------------------------------------------------------------------------
# Limpieza + registro de datos no confiables
# ---------------------------------------------------------------------------

def clean(raw: pd.DataFrame, notes: dict | None = None):
    """
    Prepara el dataset para análisis y devuelve (df, exclusions, flags).

    - df: filas de agentes REALES (sin cuentas no-persona), tipado y enriquecido con:
          ts (datetime local), date, is_confirmed, is_real_appointment.
    - exclusions: dict {motivo: conteo} de filas retiradas o marcadas no confiables.
    - flags: dict con avisos de calidad que NO retiran filas pero deben mostrarse.
    """
    notes = notes or load_notes()
    exclusions: dict[str, int] = {}
    flags: dict[str, object] = {}

    df = raw.copy()
    total_raw = len(df)

    # Tipado.
    df["ts"] = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
    tz = notes.get("timezone")
    if tz:
        df["ts_local"] = df["ts"].dt.tz_convert(tz)
    else:
        df["ts_local"] = df["ts"]
    for c in NUMERIC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 1) Excluir cuentas que no son personas reales (p. ej. "PBG Billing").
    non_person = {
        name for name, kind in notes.get("known_entities", {}).items()
        if kind == "non_person_account"
    }
    non_person_mask = df["agent"].isin(non_person)
    exclusions["cuentas_no_persona"] = int(non_person_mask.sum())
    df = df[~non_person_mask].copy()

    # 2) Fechas no parseables.
    unparseable = df["ts"].isna()
    exclusions["fechas_no_parseables"] = int(unparseable.sum())
    df = df[~unparseable].copy()

    # Enriquecer con la regla de confirmación.
    df["is_confirmed"] = df.apply(
        lambda r: is_confirmed_row(r["disposition"], r["speaker_turns"]), axis=1
    )

    # Cita REAL: solo si la disposición es appointment Y el appointment_type es appointment.
    # Un callback nunca cuenta como cita (regla de data_notes.json).
    disp = df["disposition"].str.strip().str.lower()
    atype = df["appointment_type"].str.strip().str.lower()
    df["is_real_appointment"] = (disp == "appointment") & (atype == "appointment")

    df["date"] = df["ts_local"].dt.date

    # --- Datos no confiables que se MARCAN (no se borran, pero se reportan) ---

    # a) Carrier dice "answered" pero no hubo diálogo (speaker_turns == 0).
    answered_no_talk = (df["carrier_answered"] > 0) & (df["speaker_turns"] == 0)
    exclusions["answered_sin_dialogo"] = int(answered_no_talk.sum())

    # b) Contradicción: disposition=callback pero marcado como appointment_type=appointment.
    callback_as_appt = (disp == "callback") & (atype == "appointment")
    exclusions["callback_marcado_como_cita"] = int(callback_as_appt.sum())

    # c) Dato imposible de negocio: ventas > solicitudes.
    sales_gt_apps = df["sales"] > df["applications"]
    exclusions["ventas_mayores_que_solicitudes"] = int(sales_gt_apps.sum())

    exclusions["_total_crudo"] = total_raw
    exclusions["_filas_analizadas"] = len(df)

    # --- Flags informativos ---
    pair = notes.get("shared_phone_pair", [])
    if pair:
        flags["telefono_compartido"] = pair
    if notes.get("warning"):
        flags["nota"] = notes["warning"]
    overrides = notes.get("carrier_document_premium_overrides", [])
    if overrides:
        flags["overrides_premium"] = overrides

    return df, exclusions, flags


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def compute_kpis(df: pd.DataFrame) -> dict:
    """KPIs de cabecera sobre el df ya limpio (agentes reales)."""
    total_dials = int(df["dials"].sum())
    total_answered = int(df["carrier_answered"].sum())

    confirmed = df[df["is_confirmed"]]
    # Proxy de "conversaciones reales": turnos de habla en filas confirmadas.
    real_conversations_turns = int(confirmed["speaker_turns"].sum())

    # Tasa de contacto real vs answered: qué parte del volumen "answered" ocurre
    # en filas que además son conversación confirmada.
    answered_in_confirmed = int(confirmed["carrier_answered"].sum())
    real_contact_rate = (answered_in_confirmed / total_answered) if total_answered else 0.0

    real_appointments = int(df["is_real_appointment"].sum())
    total_sales = int(df["sales"].sum())
    total_apps = int(df["applications"].sum())
    total_spend = float(df["ad_spend"].sum())

    # Conversión: ventas por conversación confirmada.
    n_confirmed = len(confirmed)
    sales_per_confirmed = (confirmed["sales"].sum() / n_confirmed) if n_confirmed else 0.0

    # Costo por venta y por cita real (calidad del gasto).
    cost_per_sale = (total_spend / total_sales) if total_sales else None
    cost_per_appt = (total_spend / real_appointments) if real_appointments else None

    return {
        "franjas_confirmadas": n_confirmed,
        "franjas_totales": len(df),
        "total_dials": total_dials,
        "total_answered": total_answered,
        "answered_en_confirmadas": answered_in_confirmed,
        "tasa_contacto_real": real_contact_rate,
        "turnos_en_confirmadas": real_conversations_turns,
        "citas_reales": real_appointments,
        "ventas": total_sales,
        "solicitudes": total_apps,
        "ventas_por_franja_confirmada": round(float(sales_per_confirmed), 3),
        "gasto_total": round(total_spend, 2),
        "costo_por_venta": round(cost_per_sale, 2) if cost_per_sale is not None else None,
        "costo_por_cita_real": round(cost_per_appt, 2) if cost_per_appt is not None else None,
    }


def by_agent(df: pd.DataFrame) -> pd.DataFrame:
    """Desempeño por agente real: contacto, confirmadas, citas reales, ventas, gasto."""
    g = df.groupby("agent")
    out = pd.DataFrame({
        "dials": g["dials"].sum(),
        "answered": g["carrier_answered"].sum(),
        "franjas_confirmadas": g["is_confirmed"].sum(),
        "citas_reales": g["is_real_appointment"].sum(),
        "ventas": g["sales"].sum(),
        "gasto": g["ad_spend"].sum().round(2),
    }).reset_index()
    out["costo_por_venta"] = out.apply(
        lambda r: round(r["gasto"] / r["ventas"], 2) if r["ventas"] else None, axis=1
    )
    return out.sort_values("ventas", ascending=False)


def by_disposition(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de resultados (disposition)."""
    out = df.groupby("disposition").size().reset_index(name="franjas")
    return out.sort_values("franjas", ascending=False)


def trend_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Tendencia por día (hora local): confirmadas, ventas y citas reales."""
    g = df.groupby("date")
    out = pd.DataFrame({
        "franjas_confirmadas": g["is_confirmed"].sum(),
        "ventas": g["sales"].sum(),
        "citas_reales": g["is_real_appointment"].sum(),
    }).reset_index()
    return out.sort_values("date")


def write_unreliable_report(exclusions: dict, flags: dict, path: str) -> None:
    """Escribe docs/datos_no_confiables.md con conteos y avisos."""
    reasons = {
        "cuentas_no_persona": "Filas de cuentas que no son personas reales (p. ej. 'PBG Billing'), excluidas de los rankings de agentes.",
        "fechas_no_parseables": "timestamp_utc no interpretable como fecha.",
        "answered_sin_dialogo": "carrier_answered > 0 pero speaker_turns = 0: el carrier dice 'contestada' sin diálogo. No cuenta como conversación.",
        "callback_marcado_como_cita": "disposition = callback pero appointment_type = appointment. Un callback NO es una cita (data_notes.json).",
        "ventas_mayores_que_solicitudes": "sales > applications: dato de negocio inconsistente, se marca para revisión.",
    }
    total_raw = exclusions.get("_total_crudo", 0)
    analizadas = exclusions.get("_filas_analizadas", 0)
    lines = [
        "# Registro de datos no confiables",
        "",
        "> Generado por `metrics.py::write_unreliable_report`. Las reglas de negocio salen de",
        "> `data/data_notes.json`, no están hardcodeadas.",
        "",
        f"- Filas crudas: **{total_raw}**",
        f"- Filas de agentes reales analizadas: **{analizadas}**",
        "",
        "| Motivo | Conteo | Descripción |",
        "|---|---|---|",
    ]
    for key, desc in reasons.items():
        lines.append(f"| `{key}` | {exclusions.get(key, 0)} | {desc} |")
    lines += [
        "",
        "## Avisos de calidad (no retiran filas, pero afectan la interpretación)",
        "",
        f"- **Teléfono compartido:** {flags.get('telefono_compartido')} comparten línea; "
        "sus métricas de contacto pueden estar mezcladas.",
        f"- **Nota del dataset:** {flags.get('nota')}",
        f"- **Overrides de premium:** {flags.get('overrides_premium')}",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    raw = load_raw()
    notes = load_notes()
    df, exclusions, flags = clean(raw, notes)
    kpis = compute_kpis(df)
    print("Exclusiones:", exclusions)
    print("Flags:", flags)
    print("KPIs:", kpis)
    out = os.path.join(HERE, "docs", "datos_no_confiables.md")
    write_unreliable_report(exclusions, flags, out)
    print("Escrito", out)
