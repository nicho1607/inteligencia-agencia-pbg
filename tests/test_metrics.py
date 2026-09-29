"""
Tests de la lógica de métricas, con foco en la regla de "conversación confirmada".

Se prueban los tres caminos que más se defienden en vivo:
  1. Disposición humana apropiada -> confirmada (aunque tenga pocos turnos).
  2. >= 4 turnos con speaker válido -> confirmada (aunque no haya disposición).
  3. carrier "answered" sin turnos ni disposición -> NO confirmada.
Más un test de que la limpieza excluye y contabiliza los datos no confiables.
"""

import os
import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import metrics  # noqa: E402


# --- 1. Regla de confirmación: disposición humana ---

def test_disposicion_humana_confirma_con_pocos_turnos():
    # 1 turno, pero disposición humana apropiada -> confirmada
    assert metrics.is_confirmed_conversation("sale_closed", valid_turns=1) is True
    assert metrics.is_confirmed_conversation("appointment_set", valid_turns=0) is True
    # también acepta mayúsculas / espacios
    assert metrics.is_confirmed_conversation(" Wrong_Number ", valid_turns=0) is True


# --- 2. Regla de confirmación: densidad de diálogo ---

def test_cuatro_turnos_confirman_sin_disposicion():
    assert metrics.is_confirmed_conversation("", valid_turns=4) is True
    assert metrics.is_confirmed_conversation(None, valid_turns=10) is True
    # 3 turnos NO alcanzan el umbral
    assert metrics.is_confirmed_conversation("", valid_turns=3) is False


# --- 3. "answered" no prueba conversación ---

def test_answered_sin_turnos_ni_disposicion_no_confirma():
    # Simula una llamada answered con 0 turnos válidos y sin disposición
    assert metrics.is_confirmed_conversation("", valid_turns=0) is False
    assert metrics.is_confirmed_conversation("no_disposition", valid_turns=0) is False
    assert metrics.is_confirmed_conversation("voicemail", valid_turns=2) is False


# --- 4. Limpieza registra y excluye datos no confiables ---

def test_clean_excluye_duplicados_y_timestamps_imposibles():
    conv = pd.DataFrame([
        # válida
        {"conversation_id": "A", "agent": "Ana", "campaign": "X", "carrier_status": "answered",
         "disposition": "sale_closed", "started_at": "2026-08-01T10:00:00",
         "ended_at": "2026-08-01T10:05:00", "duration_seconds": "300"},
        # duplicado de A
        {"conversation_id": "A", "agent": "Ana", "campaign": "X", "carrier_status": "answered",
         "disposition": "sale_closed", "started_at": "2026-08-01T10:00:00",
         "ended_at": "2026-08-01T10:05:00", "duration_seconds": "300"},
        # ended antes de started
        {"conversation_id": "B", "agent": "Bruno", "campaign": "Y", "carrier_status": "answered",
         "disposition": "", "started_at": "2026-08-02T10:00:00",
         "ended_at": "2026-08-02T09:00:00", "duration_seconds": "3600"},
        # fecha futura
        {"conversation_id": "C", "agent": "Carla", "campaign": "Z", "carrier_status": "answered",
         "disposition": "appointment_set", "started_at": "2027-01-01T10:00:00",
         "ended_at": "2027-01-01T10:05:00", "duration_seconds": "300"},
    ])
    turns = pd.DataFrame([
        {"conversation_id": "A", "turn_index": "0", "speaker": "agent", "timestamp": "", "text": ""},
    ])

    df, exclusions = metrics.clean(conv, turns, now=datetime(2026, 9, 29))

    assert exclusions["duplicados_conversation_id"] == 1
    assert exclusions["ended_antes_de_started"] == 1
    assert exclusions["fechas_futuras"] == 1
    # Solo queda la conversación A válida
    assert list(df["conversation_id"]) == ["A"]
    assert bool(df.iloc[0]["is_confirmed"]) is True
