"""
Lógica de métricas para "Inteligencia para el Dueño de la Agencia".

Responsabilidades:
  - Cargar conversations + turns.
  - Aplicar filtros base de confiabilidad y registrar TODO lo que se excluye (datos no confiables).
  - Implementar la regla de "conversación confirmada".
  - Calcular las métricas definidas en docs/metricas.md.

Todo el módulo trabaja sobre DataFrames de pandas y es puro (sin efectos de UI), para poder testearlo.
Definiciones y fórmulas viven en docs/metricas.md; aquí están implementadas 1:1.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd

# --- Constantes de dominio (deben coincidir con docs/metricas.md) ---

HUMAN_DISPOSITIONS = {
    "appointment_set",
    "sale_closed",
    "callback_scheduled",
    "not_interested",
    "wrong_number",
}
CONVERSION_DISPOSITIONS = {"appointment_set", "sale_closed"}
MIN_TURNS_FOR_CONFIRMATION = 4

# "Hoy" según el reto. Configurable para tests.
DEFAULT_NOW = datetime(2026, 9, 29)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def load_raw(data_dir: str = DATA_DIR):
    """Carga los CSV crudos sin ninguna limpieza."""
    conv = pd.read_csv(os.path.join(data_dir, "conversations.csv"), dtype=str)
    turns = pd.read_csv(os.path.join(data_dir, "turns.csv"), dtype=str)
    return conv, turns


# ---------------------------------------------------------------------------
# Regla central: conversación confirmada
# ---------------------------------------------------------------------------

def valid_turn_counts(turns: pd.DataFrame) -> pd.Series:
    """Cuenta turnos con speaker válido (no vacío) por conversation_id."""
    speaker = turns["speaker"].fillna("").astype(str).str.strip()
    valid = turns[speaker != ""]
    return valid.groupby("conversation_id").size()


def is_confirmed_conversation(disposition, valid_turns: int) -> bool:
    """
    Regla del reto. Una conversación está CONFIRMADA si:
      (a) tiene una disposición humana apropiada, O
      (b) tiene >= 4 turnos con speaker válido.
    Un carrier_status "answered" NO se considera aquí: no prueba conversación.
    """
    disp = (disposition or "")
    disp = str(disp).strip().lower()
    if disp in HUMAN_DISPOSITIONS:
        return True
    if valid_turns is not None and valid_turns >= MIN_TURNS_FOR_CONFIRMATION:
        return True
    return False


# ---------------------------------------------------------------------------
# Limpieza + registro de datos no confiables
# ---------------------------------------------------------------------------

def clean(conv: pd.DataFrame, turns: pd.DataFrame, now: datetime = DEFAULT_NOW):
    """
    Aplica filtros base de confiabilidad y devuelve:
      - df: DataFrame de conversaciones VÁLIDAS, enriquecido (valid_turns, is_confirmed).
      - exclusions: dict {motivo: conteo} de lo que se excluyó (datos no confiables).
    Las razones NO son mutuamente excluyentes salvo el orden en que se aplican.
    """
    exclusions: dict[str, int] = {}
    df = conv.copy()
    total_raw = len(df)

    # 1) Duplicados por conversation_id: quedarnos con la primera aparición.
    dup_mask = df.duplicated(subset=["conversation_id"], keep="first")
    exclusions["duplicados_conversation_id"] = int(dup_mask.sum())
    df = df[~dup_mask]

    # Parseo de tipos.
    df["started_at_dt"] = pd.to_datetime(df["started_at"], errors="coerce")
    df["ended_at_dt"] = pd.to_datetime(df["ended_at"], errors="coerce")
    df["duration_seconds_num"] = pd.to_numeric(df["duration_seconds"], errors="coerce")

    # 2) Fechas no parseables.
    unparseable = df["started_at_dt"].isna() | df["ended_at_dt"].isna()
    exclusions["fechas_no_parseables"] = int(unparseable.sum())
    df = df[~unparseable]

    # 3) ended < started (timestamps imposibles).
    ended_before = df["ended_at_dt"] < df["started_at_dt"]
    exclusions["ended_antes_de_started"] = int(ended_before.sum())
    df = df[~ended_before]

    # 4) Fechas futuras.
    future = df["started_at_dt"] > now
    exclusions["fechas_futuras"] = int(future.sum())
    df = df[~future]

    # 5) Duración negativa.
    neg = df["duration_seconds_num"] < 0
    exclusions["duracion_negativa"] = int(neg.sum())
    df = df[~neg]

    # Enriquecer con turnos válidos y regla de confirmación.
    vtc = valid_turn_counts(turns)
    df["valid_turns"] = df["conversation_id"].map(vtc).fillna(0).astype(int)
    df["is_confirmed"] = df.apply(
        lambda r: is_confirmed_conversation(r["disposition"], r["valid_turns"]), axis=1
    )
    df["date"] = df["started_at_dt"].dt.date

    exclusions["_total_crudo"] = total_raw
    exclusions["_total_valido"] = len(df)
    return df, exclusions


# ---------------------------------------------------------------------------
# Métricas (sobre el DataFrame limpio)
# ---------------------------------------------------------------------------

def _disp_norm(df: pd.DataFrame) -> pd.Series:
    return df["disposition"].fillna("").astype(str).str.strip().str.lower()


def compute_kpis(df: pd.DataFrame, conv_raw: pd.DataFrame) -> dict:
    """Calcula los KPIs de cabecera. conv_raw es el crudo, para el Data Health."""
    disp = _disp_norm(df)
    confirmed = df[df["is_confirmed"]]
    n_confirmed = len(confirmed)

    # Métrica 2: contacto real vs answered.
    answered = df[df["carrier_status"] == "answered"]
    n_answered = len(answered)
    answered_confirmed = int(answered["is_confirmed"].sum())
    real_contact_rate = (answered_confirmed / n_answered) if n_answered else 0.0

    # Métrica 3: conversión sobre confirmadas.
    conf_disp = _disp_norm(confirmed)
    n_conversion = int(conf_disp.isin(CONVERSION_DISPOSITIONS).sum())
    conversion_rate = (n_conversion / n_confirmed) if n_confirmed else 0.0

    # Métrica 7: duración media de confirmadas (con duración válida).
    dur = confirmed["duration_seconds_num"]
    avg_duration = float(dur[dur >= 0].mean()) if n_confirmed else 0.0

    # Métrica 8: data health.
    data_health = (len(df) / len(conv_raw)) if len(conv_raw) else 0.0

    return {
        "conversaciones_confirmadas": n_confirmed,
        "answered_total": n_answered,
        "answered_confirmadas": answered_confirmed,
        "tasa_contacto_real": real_contact_rate,
        "conversion_confirmadas": n_conversion,
        "tasa_conversion": conversion_rate,
        "duracion_media_confirmadas_seg": round(avg_duration, 1),
        "data_health": data_health,
    }


def by_agent(df: pd.DataFrame) -> pd.DataFrame:
    """Métrica 4: citas y ventas por agente (sobre confirmadas)."""
    confirmed = df[df["is_confirmed"]].copy()
    confirmed["disp"] = _disp_norm(confirmed)
    g = confirmed.groupby("agent")
    out = pd.DataFrame({
        "confirmadas": g.size(),
        "citas": g["disp"].apply(lambda s: (s == "appointment_set").sum()),
        "ventas": g["disp"].apply(lambda s: (s == "sale_closed").sum()),
    }).reset_index()
    out["conversion_%"] = ((out["citas"] + out["ventas"]) / out["confirmadas"] * 100).round(1)
    return out.sort_values("confirmadas", ascending=False)


def by_campaign(df: pd.DataFrame) -> pd.DataFrame:
    """Métrica 5: rendimiento por campaña (calidad de lead)."""
    confirmed = df[df["is_confirmed"]].copy()
    confirmed["disp"] = _disp_norm(confirmed)
    g = confirmed.groupby("campaign")
    out = pd.DataFrame({
        "confirmadas": g.size(),
        "conversion": g["disp"].apply(lambda s: s.isin(CONVERSION_DISPOSITIONS).sum()),
    }).reset_index()
    out["conversion_%"] = (out["conversion"] / out["confirmadas"] * 100).round(1)
    return out.sort_values("confirmadas", ascending=False)


def trend_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Métrica 6: tendencia de conversaciones confirmadas por día."""
    confirmed = df[df["is_confirmed"]]
    out = confirmed.groupby("date").size().reset_index(name="confirmadas")
    return out.sort_values("date")


def write_unreliable_report(exclusions: dict, path: str) -> None:
    """Escribe docs/datos_no_confiables.md con los conteos de lo excluido y por qué."""
    reasons = {
        "duplicados_conversation_id": "Filas duplicadas por conversation_id; se conserva la primera.",
        "fechas_no_parseables": "started_at o ended_at no se pudieron interpretar como fecha.",
        "ended_antes_de_started": "ended_at anterior a started_at (timestamp imposible).",
        "fechas_futuras": "started_at posterior a la fecha de análisis (2026-09-29).",
        "duracion_negativa": "duration_seconds menor que cero (valor imposible).",
    }
    total_raw = exclusions.get("_total_crudo", 0)
    total_valid = exclusions.get("_total_valido", 0)
    excluded = total_raw - total_valid

    lines = [
        "# Registro de datos no confiables",
        "",
        "> Generado automáticamente por `metrics.py::write_unreliable_report`.",
        "> Las exclusiones se aplican **en cascada** (en el orden listado), por eso un conteo",
        "> puede ser menor que en el perfilado crudo: una fila ya retirada por un filtro previo",
        "> no se vuelve a contar. El objetivo es no doble-contar exclusiones.",
        "",
        f"- Filas crudas: **{total_raw}**",
        f"- Filas válidas para análisis: **{total_valid}**",
        f"- Filas excluidas: **{excluded}** ({excluded / total_raw * 100:.1f}%)" if total_raw else "",
        "",
        "| Motivo de exclusión | Conteo | Descripción |",
        "|---|---|---|",
    ]
    for key, desc in reasons.items():
        lines.append(f"| `{key}` | {exclusions.get(key, 0)} | {desc} |")
    lines.append("")
    lines.append("## Nota sobre `answered`")
    lines.append("")
    lines.append(
        "Las llamadas con `carrier_status = answered` NO se excluyen del dataset, pero **no se "
        "cuentan como conversación** salvo que cumplan la regla de confirmación. La brecha entre "
        "'answered' y 'confirmadas' se muestra explícitamente en el dashboard (KPI de contacto real)."
    )
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    conv, turns = load_raw()
    df, exclusions = clean(conv, turns)
    kpis = compute_kpis(df, conv)
    print("Exclusiones:", exclusions)
    print("KPIs:", kpis)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "datos_no_confiables.md")
    write_unreliable_report(exclusions, out)
    print("Escrito", out)
