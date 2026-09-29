# Inteligencia para el Dueño de la Agencia

Dashboard que responde en 10 segundos a **"¿qué está pasando realmente en mi negocio?"**,
sin confiar ciegamente en los datos: cada métrica se define antes de mostrarse, las reglas de
negocio vienen del propio paquete de datos, y lo que no es confiable se excluye o se marca.

> Datos sintéticos provistos por el reto (`data/activity.csv`, `data/data_notes.json`).
> El enunciado original está en `docs/reto_enunciado.md`.

## Idea central (la decisión más importante)

`carrier_answered` **no prueba** que hubo una conversación: solo dice que la línea se conectó. Por eso
definimos **actividad confirmada** con una regla explícita, aplicada a cada franja hora-agente:

> Una franja está **confirmada** si su `disposition` es humana apropiada (`conversation` o
> `appointment`) **o** tiene **≥ 4 `speaker_turns`**.

En este dataset, solo el **61%** del volumen `answered` cae en franjas confirmadas. Y hay un segundo
hallazgo fuerte: bajo la definición estricta, solo hay **7 citas reales** porque `appointment_type`
contradice a `disposition` en decenas de filas — el dato de citas **no es confiable** para metas.

## Reglas de negocio (desde `data/data_notes.json`, no hardcodeadas)

- `PBG Billing` es una cuenta **no-persona** → excluida de los rankings de agentes.
- **"Callbacks are not appointments"** → un callback nunca cuenta como cita.
- `Carlos` y `Diego` **comparten teléfono** → se advierte que su contacto puede estar mezclado.
- Override de premium para `Maria` → documentado.

## Cómo correrlo (un comando)

Requisitos: Python 3.10+.

```powershell
pip install -r requirements.txt

# levantar el dashboard
python -m streamlit run app.py
```

Abre http://localhost:8501

> En este entorno `streamlit` no está en el PATH, por eso se invoca con `python -m streamlit`.

Tests y perfilado de datos:

```powershell
python -m pytest tests\ -q      # 5 tests de la lógica de métricas
python data\profile_real.py     # perfilado de calidad (Fase 1)
python metrics.py               # imprime KPIs y regenera docs/datos_no_confiables.md
```

## Qué muestra el dashboard

- **KPIs** con definición en tooltip: tasa de contacto real, ventas y costo por venta, citas reales
  y costo por cita, franjas confirmadas.
- **Alerta** de la brecha entre "answered" y conversaciones reales, y aviso de baja confiabilidad de
  las citas.
- **Tendencia** por día (hora local America/New_York).
- **Desglose** por agente y por disposición.
- **Panel de calidad de datos**: filas crudas vs. analizadas y cada señal de calidad detectada.

## Estructura

```
app.py                     # Dashboard Streamlit (presentación)
metrics.py                 # Lógica pura: limpieza, reglas de negocio, regla de confirmación, métricas
data/
  activity.csv             # Dataset real del reto (agregado por hora/agente)
  data_notes.json          # Reglas de negocio y notas de calidad
  profile_real.py          # Perfilado de calidad (Fase 1)
tests/
  test_metrics.py          # Tests: regla de confirmación + reglas de data_notes
docs/
  reto_enunciado.md        # Enunciado original del reto
  metricas.md              # Definición, fórmula, fuente, filtros y límites de cada métrica
  datos_no_confiables.md   # Registro autogenerado
  fase1_calidad_datos.md   # Resumen de exploración
  guion_video.md           # Guion del video de 2 min
  preguntas_dificiles.md   # 5 preguntas difíciles con respuestas
  respuestas.md            # Plantilla para las respuestas escritas
  screen_sharing.md        # Respuesta al reto universal (con fuentes)
```

## Stack y por qué

**Streamlit + pandas.** Un solo comando para correr, despliegue gratis en Streamlit Community Cloud.
Deja invertir el tiempo en la lógica de datos, que es lo que evalúa el reto.

## Decisiones clave

1. **Lógica (`metrics.py`) separada de la UI (`app.py`).** La lógica es pura y testeable.
2. **Reglas de negocio leídas de `data_notes.json`**, no incrustadas en el código: si el negocio
   cambia una regla, se cambia el JSON.
3. **La regla de confirmación se aplica a la franja** (el dato es agregado), usando disposición o
   turnos; el carrier no cuenta.
4. **Cita real = `appointment` + `appointment_type=appointment`.** Callbacks fuera. Esto expone que
   el dato de citas es escaso y poco confiable, en vez de inflarlo.
5. **Exclusiones y marcas registradas** en un doc autogenerado y en el panel de calidad.

## Trade-offs

- El dato es **agregado por hora**, así que hablamos de "franjas confirmadas", no de conversaciones
  individuales. Es lo correcto con este esquema, pero pierde granularidad por llamada.
- Umbral de 4 turnos fijo (viene del enunciado); calibrable con más datos.
- Sin base de datos: se lee el CSV en memoria (volumen pequeño, suficiente).

## Qué haría con más tiempo

- Filtros interactivos por fecha, agente y disposición.
- Reconciliar `disposition` vs `appointment_type` con el equipo de datos para arreglar el origen.
- Normalizar desempeño por agente por leads asignados.
- Separar el contacto de Carlos/Diego (línea compartida) si el origen lo permite.
- Validación de esquema (pandera) y CI que corra los tests en cada push.

## Despliegue (Streamlit Community Cloud)

1. Subir el repo a GitHub.
2. En share.streamlit.io conectar el repo y elegir `app.py`.
3. Usa `requirements.txt` automáticamente. Sin secretos.
