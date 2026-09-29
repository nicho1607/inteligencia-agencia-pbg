"""
Tests de la lógica de métricas sobre el dataset real (esquema agregado por hora/agente).

Foco:
  1. Regla de "confirmada" a nivel fila (disposición humana o >=4 turnos; carrier no cuenta).
  2. Reglas de negocio de data_notes.json: excluir cuenta no-persona, callback != cita.
  3. Marcado de datos no confiables.
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import metrics  # noqa: E402


NOTES = {
    "timezone": "America/New_York",
    "known_entities": {"PBG Billing": "non_person_account"},
    "shared_phone_pair": ["Carlos", "Diego"],
    "warning": "Callbacks are not appointments.",
}


def _row(**kw):
    base = {
        "timestamp_utc": "2026-09-15T14:30:00Z", "agent": "Ana", "dials": "10",
        "carrier_answered": "5", "speaker_turns": "0", "disposition": "no_answer",
        "appointment_type": "none", "premium_screen": "0", "applications": "0",
        "sales": "0", "ad_spend": "1.0",
    }
    base.update(kw)
    return base


# --- 1. Regla de confirmación ---

def test_disposicion_humana_confirma():
    assert metrics.is_confirmed_row("conversation", 0) is True
    assert metrics.is_confirmed_row("appointment", 1) is True


def test_cuatro_turnos_confirman_sin_disposicion_humana():
    assert metrics.is_confirmed_row("voicemail", 4) is True
    assert metrics.is_confirmed_row("no_answer", 3) is False


def test_answered_no_prueba_conversacion():
    # carrier "answered" no entra en la regla; una fila answered sin diálogo no confirma
    assert metrics.is_confirmed_row("no_answer", 0) is False
    assert metrics.is_confirmed_row("callback", 0) is False


# --- 2. Reglas de negocio de data_notes.json ---

def test_excluye_cuenta_no_persona_y_callback_no_es_cita():
    raw = pd.DataFrame([
        _row(agent="PBG Billing", disposition="conversation", speaker_turns="6"),  # se excluye
        _row(agent="Ana", disposition="appointment", appointment_type="appointment",
             sales="1", applications="1"),                                          # cita real
        _row(agent="Luis", disposition="callback", appointment_type="appointment"),  # callback != cita
    ])
    df, exclusions, flags = metrics.clean(raw, NOTES)

    # PBG Billing fuera
    assert "PBG Billing" not in set(df["agent"])
    assert exclusions["cuentas_no_persona"] == 1
    # Solo 1 cita real (la de Ana); el callback de Luis no cuenta
    assert int(df["is_real_appointment"].sum()) == 1
    assert exclusions["callback_marcado_como_cita"] == 1
    # Flag del teléfono compartido presente
    assert flags["telefono_compartido"] == ["Carlos", "Diego"]


# --- 3. Marcado de datos no confiables ---

def test_marca_answered_sin_dialogo_y_ventas_imposibles():
    raw = pd.DataFrame([
        _row(agent="Ana", carrier_answered="8", speaker_turns="0"),          # answered sin diálogo
        _row(agent="Luis", sales="2", applications="1", disposition="conversation", speaker_turns="5"),  # sales>apps
    ])
    df, exclusions, flags = metrics.clean(raw, NOTES)
    assert exclusions["answered_sin_dialogo"] == 1
    assert exclusions["ventas_mayores_que_solicitudes"] == 1
