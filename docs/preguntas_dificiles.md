# 5 preguntas difíciles (con respuestas sugeridas)

Para defender las decisiones en vivo. Respuestas cortas y directas.

---

### 1. ¿Por qué 4 turnos y no 3 o 6? ¿No es arbitrario?

El umbral viene del enunciado del reto, así que lo implementé literal. Pero no lo defiendo como
verdad absoluta: es un parámetro (`MIN_TURNS_FOR_CONFIRMATION`) en un solo lugar. Con datos reales
lo calibraría mirando la distribución de turnos de conversaciones que sí terminaron en disposición
humana, y buscaría el punto donde la señal se estabiliza. Es una decisión de producto, no de código.

### 2. Tu regla puede tener falsos negativos: una venta real y rápida con pocos turnos y sin disposición marcada. ¿No pierdes negocio ahí?

Sí, y es una decisión consciente. Preferí un sesgo **conservador**: es peor inflar la actividad que
subestimarla, porque el dueño toma decisiones sobre estos números. Además ese caso está cubierto por
la vía (a): si hubo venta y el agente marca `sale_closed`, cuenta aunque tenga un solo turno. El
falso negativo real es "venta sin disposición y sin diálogo registrado", que es justamente el dato en
el que no deberíamos confiar.

### 3. Excluyes filas por timestamps imposibles y duplicados. ¿No estás ocultando un problema del pipeline de origen en vez de arreglarlo?

No lo oculto: lo registro. El panel de calidad de datos y `docs/datos_no_confiables.md` muestran
exactamente cuántas filas caen y por qué. Excluir es la decisión correcta para no contaminar las
métricas hoy; el registro es la señal para que ingeniería de datos arregle el origen. Separo "reportar
confiable ahora" de "arreglar la fuente", que es un trabajo distinto.

### 4. ¿Por qué calculas conversión sobre confirmadas y no sobre el total de llamadas?

Porque mezclar no-contactos en el denominador mide dos cosas a la vez: capacidad de contactar y
capacidad de convertir. Sobre confirmadas, la conversión responde "cuando de verdad hablamos, ¿cuánto
cerramos?", que es lo accionable para coaching de agentes. La capacidad de contacto ya la mide el KPI
de contacto real por separado. Son dos preguntas distintas y las mantengo separadas.

### 5. Datos sintéticos: ¿cómo sé que esto sirve con datos reales?

La lógica no sabe que los datos son sintéticos; opera sobre el esquema, no sobre valores mágicos.
Cambiar a datos reales es reemplazar los CSV en `data/`. Generé el dataset con los mismos problemas
que esperaría en producción (duplicados, timestamps rotos, disposiciones vacías, "answered" sin
diálogo) precisamente para probar que el pipeline los detecta. Los tests fijan el comportamiento de la
regla, así que un cambio de datos no rompe silenciosamente la definición.
