"""
Generador de dataset SINTÉTICO para el reto "Inteligencia para el Dueño de la Agencia".

TODOS los datos son sintéticos: no hay información real de clientes.

El generador produce dos tablas relacionadas:
  - conversations.csv : una fila por conversación (metadatos, carrier, disposición, agente, campaña)
  - turns.csv         : una fila por turno de habla dentro de una conversación (speaker + timestamp)

A propósito inyecta problemas de calidad de datos para que el pipeline los detecte:
  - Filas duplicadas (mismo conversation_id).
  - Timestamps imposibles (ended_at antes de started_at; fechas en el futuro).
  - Estados contradictorios (carrier="answered" pero sin turnos humanos reales).
  - Disposiciones vacías / nulas.
  - Turnos sin speaker (speaker vacío).
  - Duración negativa.

La semilla fija hace el dataset reproducible.
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

AGENTS = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Falco"]
CAMPAIGNS = ["Google-Ads", "Meta-Leads", "Referidos", "Cold-Outbound", "Landing-Web"]
CARRIER_STATES = ["answered", "no-answer", "busy", "failed", "voicemail"]

# Disposiciones "humanas apropiadas": prueban que hubo una conversación real con resultado.
HUMAN_DISPOSITIONS = [
    "appointment_set",   # cita agendada
    "sale_closed",       # venta cerrada
    "callback_scheduled",# devolver llamada agendada
    "not_interested",    # no interesado (pero hubo conversación real)
    "wrong_number",      # número equivocado (contacto humano confirmado)
]
# Disposiciones NO concluyentes (no prueban conversación por sí solas).
NON_HUMAN_DISPOSITIONS = ["", None, "voicemail", "no_disposition"]

BASE_DATE = datetime(2026, 8, 1, 9, 0, 0)


def rand_agent():
    return random.choice(AGENTS)


def rand_campaign():
    return random.choice(CAMPAIGNS)


def make_turns(conversation_id, started_at, n_turns, inject_missing_speaker=False):
    """Genera n_turns turnos alternando entre 'agent' y 'customer'."""
    turns = []
    t = started_at
    for i in range(n_turns):
        speaker = "agent" if i % 2 == 0 else "customer"
        # Inyectar un turno sin speaker en algunas conversaciones
        if inject_missing_speaker and i == 1:
            speaker = ""  # turno sin speaker (problema de calidad)
        t = t + timedelta(seconds=random.randint(5, 45))
        turns.append({
            "conversation_id": conversation_id,
            "turn_index": i,
            "speaker": speaker,
            "timestamp": t.isoformat(),
            "text": f"turno sintético {i}",
        })
    return turns


def main():
    conversations = []
    turns = []

    n = 600  # número base de conversaciones "limpias"
    for i in range(n):
        conv_id = f"C{i:05d}"
        agent = rand_agent()
        campaign = rand_campaign()
        started = BASE_DATE + timedelta(
            days=random.randint(0, 45),
            minutes=random.randint(0, 600),
        )

        # Perfil de la conversación: decide carrier, turnos y disposición de forma correlacionada.
        roll = random.random()
        if roll < 0.45:
            # Conversación real y sólida: contestada, varios turnos, disposición humana
            carrier = "answered"
            n_turns = random.randint(4, 14)
            disposition = random.choice(HUMAN_DISPOSITIONS)
        elif roll < 0.60:
            # Contestada pero corta: answered con 1-3 turnos y sin disposición humana
            # (caso clave: "answered" NO prueba conversación)
            carrier = "answered"
            n_turns = random.randint(1, 3)
            disposition = random.choice(NON_HUMAN_DISPOSITIONS)
        elif roll < 0.72:
            # Buzón de voz: answered/voicemail, 0-1 turnos
            carrier = random.choice(["voicemail", "answered"])
            n_turns = random.randint(0, 1)
            disposition = "voicemail"
        else:
            # No contactada: no-answer/busy/failed, 0 turnos
            carrier = random.choice(["no-answer", "busy", "failed"])
            n_turns = 0
            disposition = random.choice(["", "no_disposition"])

        duration = sum(random.randint(5, 45) for _ in range(max(n_turns, 1)))
        ended = started + timedelta(seconds=duration)

        conversations.append({
            "conversation_id": conv_id,
            "agent": agent,
            "campaign": campaign,
            "carrier_status": carrier,
            "disposition": disposition if disposition is not None else "",
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "duration_seconds": duration,
        })

        inject_missing = (i % 97 == 0)  # ~1% de conversaciones con un turno sin speaker
        turns.extend(make_turns(conv_id, started, n_turns, inject_missing_speaker=inject_missing))

    # -------- INYECCIÓN DE PROBLEMAS DE CALIDAD DE DATOS --------

    # 1) Duplicados exactos: repetir 12 conversaciones (mismo conversation_id)
    dupes = random.sample(conversations, 12)
    for d in dupes:
        conversations.append(dict(d))

    # 2) Timestamps imposibles: ended_at antes de started_at (8 filas)
    for c in random.sample(conversations, 8):
        s = datetime.fromisoformat(c["started_at"])
        c["ended_at"] = (s - timedelta(minutes=random.randint(1, 30))).isoformat()
        c["duration_seconds"] = -abs(c["duration_seconds"])  # duración negativa

    # 3) Fechas en el futuro (5 filas) — imposible dado "hoy"
    for c in random.sample(conversations, 5):
        future = datetime(2027, 1, 1) + timedelta(days=random.randint(0, 200))
        c["started_at"] = future.isoformat()
        c["ended_at"] = (future + timedelta(minutes=5)).isoformat()

    # 4) Contradicción: carrier="answered" con 0 turnos (15 filas nuevas)
    for k in range(15):
        conv_id = f"X{k:05d}"
        s = BASE_DATE + timedelta(days=random.randint(0, 45))
        conversations.append({
            "conversation_id": conv_id,
            "agent": rand_agent(),
            "campaign": rand_campaign(),
            "carrier_status": "answered",     # dice contestada
            "disposition": "",                # pero sin disposición
            "started_at": s.isoformat(),
            "ended_at": (s + timedelta(minutes=2)).isoformat(),
            "duration_seconds": 120,
        })
        # No agregamos turnos: contradicción answered-sin-conversación

    # Mezclar filas para que los problemas no queden agrupados
    random.shuffle(conversations)
    random.shuffle(turns)

    conv_fields = [
        "conversation_id", "agent", "campaign", "carrier_status",
        "disposition", "started_at", "ended_at", "duration_seconds",
    ]
    with open(os.path.join(OUT_DIR, "conversations.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=conv_fields)
        w.writeheader()
        w.writerows(conversations)

    turn_fields = ["conversation_id", "turn_index", "speaker", "timestamp", "text"]
    with open(os.path.join(OUT_DIR, "turns.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=turn_fields)
        w.writeheader()
        w.writerows(turns)

    print(f"Escritas {len(conversations)} filas en conversations.csv")
    print(f"Escritas {len(turns)} filas en turns.csv")


if __name__ == "__main__":
    main()
