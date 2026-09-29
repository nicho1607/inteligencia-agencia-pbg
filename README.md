# Inteligencia para el Dueño de la Agencia

Dashboard que responde en 10 segundos a **"¿qué está pasando realmente en mi negocio?"**,
sin confiar ciegamente en los datos: cada métrica se define antes de mostrarse y lo que no es
confiable se excluye y se registra.

> **Todos los datos son sintéticos.** No hay información real de clientes.

## Idea central (la decisión más importante)

Un `carrier_status = "answered"` **no prueba** que hubo una conversación. Solo dice que la línea
se conectó. Por eso definimos **conversación confirmada** con una regla explícita:

> Una conversación está **confirmada** si tiene **(a)** una disposición humana apropiada
> (`appointment_set`, `sale_closed`, `callback_scheduled`, `not_interested`, `wrong_number`)
> **o (b)** al menos **4 turnos** con speaker válido.

En este dataset, de **420** llamadas `answered`, solo **284** son conversación confirmada: reportar
"answered" como conversaciones sobreestimaría la actividad real en ~32%. Esa brecha es visible en el
dashboard.

## Cómo correrlo (un comando)

Requisitos: Python 3.10+.

```powershell
pip install -r requirements.txt

# (opcional) regenerar datos sintéticos
python data\generate_data.py

# levantar el dashboard
python -m streamlit run app.py
```

Abre http://localhost:8501

> Nota: en este entorno `streamlit` no está en el PATH, por eso se invoca con `python -m streamlit`.

Tests:

```powershell
python -m pytest tests\ -q
```

Perfilado de calidad de datos (Fase 1):

```powershell
python data\profile_data.py
```

## Qué muestra el dashboard

- **KPIs** con definición en tooltip: conversaciones confirmadas, tasa de contacto real
  (confirmadas / answered), tasa de conversión (citas+ventas / confirmadas), salud de los datos.
- **Alerta** de la brecha entre "answered" y conversaciones reales.
- **Tendencia** de confirmadas por día.
- **Desglose** por campaña (calidad de lead) y por agente (citas, ventas, conversión).
- **Panel de calidad de datos**: filas crudas vs. válidas y el detalle de exclusiones.

## Estructura

```
app.py                     # Dashboard Streamlit (capa de presentación)
metrics.py                 # Lógica pura: limpieza, regla de confirmación, métricas (testeable)
data/
  generate_data.py         # Generador sintético con problemas de calidad inyectados
  profile_data.py          # Perfilado de calidad (Fase 1)
  conversations.csv        # Datos sintéticos generados
  turns.csv
tests/
  test_metrics.py          # Tests de la regla de confirmación y de las exclusiones
docs/
  metricas.md              # Definición, fórmula, fuente, filtros y límites de cada métrica
  datos_no_confiables.md   # Registro autogenerado de exclusiones
  fase1_calidad_datos.md   # Resumen de exploración de datos
  guion_video.md           # Guion del video de 2 minutos
  preguntas_dificiles.md   # 5 preguntas difíciles con respuestas
  respuestas.md            # Plantilla para las respuestas escritas solicitadas
  screen_sharing.md        # Respuesta al reto universal de screen sharing
```

## Stack y por qué

**Streamlit + pandas.** Un solo comando para correr y despliegue gratis en Streamlit Community
Cloud. Permite invertir el tiempo en la lógica de datos (que es lo que evalúa el reto) y no en
plomería de frontend/backend.

## Decisiones clave

1. **Separé lógica (`metrics.py`) de presentación (`app.py`).** La lógica es pura y testeable; la UI
   solo llama funciones. Así los tests defienden las métricas sin depender de Streamlit.
2. **Regla de confirmación literal al enunciado** y con normalización (mayúsculas/espacios) para no
   perder disposiciones por formato.
3. **Exclusiones en cascada y registradas.** No se doble-cuentan y quedan en un documento
   autogenerado; la transparencia es parte del entregable.
4. **"answered" se conserva pero no se cuenta** como conversación; la brecha se muestra en vez de
   esconderse.
5. **Conversión sobre confirmadas, no sobre el total**, para no diluir el numerador con no-contactos.

## Trade-offs

- **Dataset sintético** en vez de datos reales (no había datos en el paquete). Estructura y problemas
  de calidad son realistas; el pipeline funciona igual con datos reales cambiando los CSV.
- **Umbral de 4 turnos fijo** (viene del enunciado); podría calibrarse con datos reales.
- **Sin base de datos**: leemos CSV en memoria. Suficiente para el volumen del reto; no escala a
  millones de filas sin cambiar el almacenamiento.
- **Conversión no incluye monto ni asistencia real a la cita** (no está en los datos).

## Qué haría con más tiempo

- Filtros interactivos por rango de fechas, agente y campaña.
- Normalizar desempeño por agente por número de leads asignados (no solo volumen).
- Métrica de tiempo de primera respuesta usando `turns` (primer turno de agente).
- ROI por campaña incorporando costo.
- Validación de esquema con `pandera` y un CI que corra los tests en cada push.
- Persistencia en DuckDB/Parquet para volúmenes grandes.

## Despliegue (Streamlit Community Cloud)

1. Subir el repo a GitHub.
2. En share.streamlit.io, conectar el repo y elegir `app.py`.
3. Usa `requirements.txt` automáticamente. Sin secretos ni variables de entorno.
