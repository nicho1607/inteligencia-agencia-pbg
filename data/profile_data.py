"""
Perfilado de calidad de datos (Fase 1).

Lee conversations.csv y turns.csv y reporta, SIN modificar nada:
  - Esquema y tipos observados.
  - Nulos / vacíos por columna.
  - Duplicados por conversation_id.
  - Timestamps imposibles (ended < started, fechas futuras).
  - Duraciones negativas.
  - Contradicciones carrier="answered" sin turnos.
  - Turnos sin speaker.
  - Rangos de fechas y valores distintos de campos categóricos.

Solo usa librería estándar. Salida por consola, pensada para pegar en el resumen.
"""

import csv
import os
from collections import Counter, defaultdict
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
NOW = datetime(2026, 9, 29)  # "hoy" según el reto


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_dt(s):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    conv = load(os.path.join(DATA_DIR, "conversations.csv"))
    turns = load(os.path.join(DATA_DIR, "turns.csv"))

    section("ESQUEMA")
    print("conversations.csv columnas:", list(conv[0].keys()))
    print("turns.csv columnas:", list(turns[0].keys()))
    print(f"Filas conversations: {len(conv)}")
    print(f"Filas turns: {len(turns)}")

    section("NULOS / VACIOS por columna (conversations)")
    for col in conv[0].keys():
        empty = sum(1 for r in conv if r[col] is None or str(r[col]).strip() == "")
        print(f"  {col:18s}: {empty} vacíos")

    section("DUPLICADOS por conversation_id")
    ids = Counter(r["conversation_id"] for r in conv)
    dupe_ids = {k: v for k, v in ids.items() if v > 1}
    print(f"  conversation_id únicos: {len(ids)}")
    print(f"  ids con duplicados: {len(dupe_ids)} (filas extra: {sum(v-1 for v in dupe_ids.values())})")
    if dupe_ids:
        print("  ejemplos:", list(dupe_ids.items())[:5])

    section("TIMESTAMPS IMPOSIBLES")
    ended_before_started = 0
    future_rows = 0
    unparseable = 0
    for r in conv:
        s = parse_dt(r["started_at"])
        e = parse_dt(r["ended_at"])
        if s is None or e is None:
            unparseable += 1
            continue
        if e < s:
            ended_before_started += 1
        if s > NOW:
            future_rows += 1
    print(f"  ended_at < started_at : {ended_before_started}")
    print(f"  started_at en el futuro (> {NOW.date()}): {future_rows}")
    print(f"  fechas no parseables  : {unparseable}")

    section("DURACIONES NEGATIVAS")
    neg = sum(1 for r in conv if float(r["duration_seconds"]) < 0)
    print(f"  duration_seconds < 0: {neg}")

    section("VALORES CATEGORICOS")
    print("  carrier_status:", dict(Counter(r["carrier_status"] for r in conv)))
    print("  disposition (top):", dict(Counter((r["disposition"] or "<vacío>") for r in conv).most_common()))
    print("  agentes:", dict(Counter(r["agent"] for r in conv)))
    print("  campañas:", dict(Counter(r["campaign"] for r in conv)))

    section("TURNOS SIN SPEAKER")
    no_speaker = sum(1 for t in turns if str(t["speaker"]).strip() == "")
    print(f"  turnos con speaker vacío: {no_speaker}")

    section("CONTRADICCION: carrier='answered' SIN turnos")
    turns_by_conv = defaultdict(int)
    for t in turns:
        turns_by_conv[t["conversation_id"]] += 1
    answered = [r for r in conv if r["carrier_status"] == "answered"]
    answered_no_turns = [r for r in answered if turns_by_conv.get(r["conversation_id"], 0) == 0]
    answered_few_turns = [r for r in answered if 0 < turns_by_conv.get(r["conversation_id"], 0) < 4]
    print(f"  answered TOTAL: {len(answered)}")
    print(f"  answered con 0 turnos (contradicción dura): {len(answered_no_turns)}")
    print(f"  answered con 1-3 turnos (no prueban conversación): {len(answered_few_turns)}")

    section("RANGO DE FECHAS (started_at válidos)")
    dts = [parse_dt(r["started_at"]) for r in conv]
    dts = [d for d in dts if d is not None]
    print(f"  min: {min(dts)}")
    print(f"  max: {max(dts)}")


if __name__ == "__main__":
    main()
