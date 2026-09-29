# Reto universal: Screen Sharing sin app

**Enunciado (resumen):** enviar a un cliente un enlace que abra desde su teléfono sin instalar una
app; tras dar permiso, poder ver su pantalla mientras navega por otros sitios o apps para guiarlo
remotamente.

> Investigación, razonamiento y recomendación técnica. No se implementa. Fuentes al final.
> Nota de licencia: el contenido fue parafraseado para cumplir con las restricciones de las fuentes.

## Respuesta corta

Lo exacto que se pide —**ver toda la pantalla del teléfono, incluidas otras apps, solo con un enlace
web y sin instalar nada**— **no es posible hoy**, sobre todo en iPhone. La web solo puede capturar
pantalla dentro del propio navegador y con límites fuertes en móvil. Para "ver todo el dispositivo"
se necesita código nativo (una app o extensión), que es justo lo que se quiere evitar.

## 1) Qué es técnicamente posible

- En **escritorio** (Chrome, Edge, Firefox, Safari 13+), una web puede pedir capturar pantalla,
  ventana o pestaña con la API estándar **`getDisplayMedia()`** del *Screen Capture API*, y enviar
  ese video por **WebRTC** en tiempo real. Es la única vía soportada para que una página capture
  pantalla, y siempre requiere permiso explícito del usuario. [MDN, liveapi]
- En **Android**, Chrome soporta `getDisplayMedia()`; el usuario puede compartir una pestaña o la
  pantalla de la app. La cuota de captura de nivel sistema en apps nativas usa **MediaProjection**.
  [Chrome/Android docs]
- El flujo "abrir un enlace y compartir" funciona bien en desktop y, con matices, en Android.

## 2) Qué NO es posible

- En **iOS/iPadOS**, Safari (y todos los navegadores del iPhone, que por política de Apple usan el
  mismo motor WebKit) **no exponen `getDisplayMedia()`**: una web no puede capturar la pantalla. Un
  enlace web no puede ver la pantalla del iPhone. [MDN compat, videosdk]
- **Ninguna** plataforma permite que una **página web** vea la pantalla **fuera del navegador**
  (otras apps, pantalla de inicio). La captura web se limita al contenido del navegador y a lo que el
  usuario elige compartir.
- Ver "todo el dispositivo, incluidas otras apps" solo se logra con **código nativo**: en iOS con
  **ReplayKit + Broadcast Upload Extension** (el usuario inicia el broadcast desde el Centro de
  Control), y en Android con **MediaProjection**. Ambos exigen una app instalada. [Apple/ReplayKit,
  Android MediaProjection]

## 3) Diferencias por plataforma

| | Ver pantalla desde la **web** | Ver **todo el dispositivo** |
|---|---|---|
| **Desktop** (Chrome/Edge/Firefox/Safari) | Sí, `getDisplayMedia()` (pantalla/ventana/pestaña) | Sí, eligiendo "pantalla completa" |
| **Android** (Chrome) | Sí, pestaña o pantalla vía `getDisplayMedia()` | Solo con app nativa (MediaProjection) |
| **iPhone/iPad** (Safari/WebKit) | **No** hay captura de pantalla web | Solo con app nativa (ReplayKit Broadcast Extension) |

## 4) Qué construiría para acercarme al máximo (sin app)

Como el requisito real es **"guiar al cliente remotamente"**, no necesariamente "ver el sistema
operativo entero", propongo dos capas:

**A) Co-browsing como opción principal (recomendada).**
En vez de transmitir píxeles, se comparte el **DOM** de la página: la web del cliente incrusta un
pequeño script que transmite la estructura y los eventos por WebSocket, y el agente ve y guía sobre
la misma página. Funciona en iPhone, Android y desktop **sin instalar nada**, consume muy poco ancho
de banda y es más privado (no expone otras apps ni datos fuera de la sesión). Limitación: solo cubre
**tu propio sitio/app web**, no otras apps del teléfono. [cobrowse.io, forasoft, zoho]

**B) Screen share web donde sí se puede, con degradación elegante.**
- Desktop y Android: botón "Compartir pantalla" con `getDisplayMedia()` + WebRTC.
- iPhone: detectar que no hay soporte y ofrecer el co-browsing (A) o, si de verdad se necesita ver el
  dispositivo completo, guiar al usuario a la grabación/broadcast nativa. Si esto último fuera un
  requisito duro, la única salida real es una **app o extensión de broadcast** (rompe el "sin app").

**Recomendación:** empezar con **co-browsing** para el caso "guiar en el sitio web", que cumple "sin
instalar nada" en las tres plataformas, y añadir `getDisplayMedia()` en desktop/Android como bonus.
Dejar claro al negocio que "ver toda la pantalla del iPhone con solo un enlace" no es alcanzable sin
app, por diseño de Apple.

## Fuentes principales

- MDN — Screen Capture API / `getDisplayMedia()`:
  https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getDisplayMedia
- MDN — Using the Screen Capture API:
  https://developer.mozilla.org/en-US/docs/Web/API/Screen_Capture_API/Using_Screen_Capture
- liveapi — WebRTC screen sharing (getDisplayMedia como única vía web):
  https://liveapi.com/blog/webrtc-screen-sharing/
- videosdk — WebRTC en Safari (soporte y límites en iOS):
  https://www.videosdk.live/developer-hub/webrtc/webrtc-safari
- Apple — ReplayKit / Broadcast (captura de todo el dispositivo, nativo):
  https://developer.apple.com/videos/play/wwdc2020/10633/
- Android Developers — MediaProjection:
  https://developer.android.com/media/grow/media-projection
- cobrowse.io — Co-browsing vs screen sharing:
  https://cobrowse.io/articles/co-browsing-versus-screen-sharing
- forasoft — Co-browsing comparte el DOM, no los píxeles:
  https://www.forasoft.com/blog/article/cobrowsing-software-development
