"""Perfilado del dataset REAL (activity.csv). Solo lectura, no modifica nada."""
import pandas as pd
import os

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "activity.csv"), dtype=str)

print("== SHAPE =="); print(df.shape)
print("\n== COLUMNAS / DTYPES (crudo) =="); print(list(df.columns))
print("\n== NULOS / VACIOS por columna ==")
for c in df.columns:
    empty = df[c].isna().sum() + (df[c].fillna("").astype(str).str.strip() == "").sum()
    print(f"  {c:20s}: {empty}")

print("\n== DUPLICADOS de filas completas ==")
print("  ", df.duplicated().sum())
print("== DUPLICADOS (timestamp_utc+agent) ==")
print("  ", df.duplicated(subset=["timestamp_utc", "agent"]).sum())

print("\n== VALORES CATEGORICOS ==")
for c in ["agent", "disposition", "appointment_type"]:
    print(f"  {c}:", dict(df[c].fillna("<NA>").value_counts()))

print("\n== RANGOS NUMERICOS ==")
for c in ["dials", "carrier_answered", "speaker_turns", "premium_screen", "applications", "sales", "ad_spend"]:
    n = pd.to_numeric(df[c], errors="coerce")
    print(f"  {c:18s}: min={n.min()}, max={n.max()}, nulos_no_num={n.isna().sum()}, negativos={(n<0).sum()}")

print("\n== TIMESTAMPS ==")
ts = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
print("  no parseables:", ts.isna().sum())
print("  min:", ts.min(), " max:", ts.max())
NOW = pd.Timestamp("2026-09-29", tz="UTC")
print("  en el futuro (>2026-09-29):", (ts > NOW).sum())

print("\n== CONTRADICCIONES / RAREZAS ==")
ca = pd.to_numeric(df["carrier_answered"], errors="coerce")
st = pd.to_numeric(df["speaker_turns"], errors="coerce")
dials = pd.to_numeric(df["dials"], errors="coerce")
print("  carrier_answered>0 pero speaker_turns=0:", ((ca > 0) & (st == 0)).sum())
print("  carrier_answered > dials (imposible):", (ca > dials).sum())
appt = pd.to_numeric(df["applications"], errors="coerce")
sales = pd.to_numeric(df["sales"], errors="coerce")
print("  sales > applications (venta sin solicitud?):", (sales > appt).sum())
print("  disposition=='appointment' vs appointment_type:")
print("   ", dict(df[df["disposition"]=="appointment"]["appointment_type"].fillna("<NA>").value_counts()))
print("  disposition=='callback' con appointment_type=='appointment':",
      ((df["disposition"]=="callback") & (df["appointment_type"]=="appointment")).sum())
