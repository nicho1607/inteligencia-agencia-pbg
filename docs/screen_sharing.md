# Reto universal de screen sharing

> Pega aquí el enunciado exacto cuando lo tengas. Abajo dejo una respuesta base lista para ajustar.

## Enunciado

_(pegar aquí)_

## Respuesta base

Durante el screen sharing puedo recorrer el proyecto en vivo y explicar cada decisión mientras la
muestro:

1. **Arranco por la pregunta del negocio**, no por el código: abro el dashboard y en 10 segundos
   muestro los KPIs, la alerta de la brecha "answered vs. conversación real" y el panel de calidad
   de datos.
2. **Muestro la regla de confirmación** en `metrics.py::is_confirmed_conversation` y la conecto con
   `docs/metricas.md`, donde está su definición y sus límites.
3. **Corro los tests** (`python -m pytest tests\ -q`) para evidenciar que la lógica está fijada:
   disposición humana confirma, 4 turnos confirman, "answered" sin diálogo no confirma.
4. **Corro el perfilado** (`python data\profile_data.py`) para mostrar de dónde salen los conteos de
   calidad de datos.
5. **Explico trade-offs** con honestidad: dataset sintético, umbral de turnos calibrable, sin base de
   datos. Y qué haría con más tiempo.

La idea que quiero transmitir: sé separar la señal confiable del ruido, documento mis definiciones
antes de mostrarlas, y puedo defender cada número con su fórmula y su test.
