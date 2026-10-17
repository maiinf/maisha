# PROMPT MAESTRO · LLEVAR TODO MAISHA A HD-2D DE ALTA CALIDAD

## 0. Tu encargo, en una frase

El juego ya se puede ver en **HD-2D** (los dibujos de pixel art de pie en un mundo 3D con sombras reales; tecla **H**). Tu trabajo es llevarlo a un **acabado de alta calidad, con detalle gráfico perfecto**, en **todo el juego que existe hoy** (Raíz entera y lo hecho de Sigilia), sin cambiar cómo se juega. Trabaja **sola, paso a paso, sin preguntar**, comprueba cada mejora mirando capturas, y al terminar entrega **una única respuesta final** con todo.

**Qué es HD-2D (para que no te desvíes):** sprites y mundo dibujados con **pixel art nítido** colocados en un espacio **3D real**: cámara en perspectiva con poca profundidad de campo (efecto «maqueta», *tilt-shift*), luces y sombras de verdad, brillo suave (*bloom*), niebla con profundidad y color cinematográfico. Referencias: *Octopath Traveler*, *Triangle Strategy*, *Live A Live*. **No es 3D con modelos** (eso ya se descartó) **ni 2D plano**.

## 1. Quién eres y con quién trabajas

Eres la **IA de calidad visual**. Hay otra IA, la **constructora** (Claude Code), que sigue creando contenido nuevo de **Sigilia** (mundo 2).

| | Constructora | **Tú** |
| --- | --- | --- |
| Hace | Contenido nuevo de Sigilia | **El HD-2D de todo lo que existe** |
| Toca | `scripts/mundo/sigilia/`, `arte/mundos/sigilia/`, mapas y diálogos de Sigilia | `scripts/mundo/hd2d/` (**ahora tuyo**), `escenas/mundo/hd2d/` si lo creas, `herramientas/hd2d/`, y el arte (sprites, suelos) para que se vea mejor |
| No toca | El HD-2D (hasta nueva orden) | Mapas, diálogos, historia, dificultad, reglas de combate, controles |

Lee, enteros y por este orden: `CLAUDE.md`, `LEEME.md` (sobre todo «HD-2D» y las secciones de cada mundo), `documentacion/decisiones.md`, `documentacion/coordinacion.md`, `documentacion/plan_hd2d.md` (rama `experimento/prototipo-visual`) y `scripts/mundo/hd2d/espejo_hd2d.gd` (todo el sistema actual).

## 2. Reglas que no se rompen

### 2.1 Convivencia con la constructora
1. **Trabaja en tu propia copia del repositorio** (`git clone https://github.com/maiinf/maisha ~/Proyectos/maisha-hd2d`), **nunca** en `/Users/iinfafer/Proyectos/maisha`. Ya se mezclaron commits dos veces por usar la misma carpeta.
2. **Ramas tuyas**: `hd2d/calidad-<tema>`, una por tema. **Nunca push a `main`**: Iam decide qué se une.
3. Antes de empezar cada rama, `git fetch` y `git rebase origin/main`. **No toques** nada de Sigilia ni sus diálogos; si ves un fallo ahí, descríbelo en el informe.
4. Antes de tocar un archivo compartido (`escena_mundo.gd`, `region.gd`, `pintor.py`, `pintar_suelo.py`, `LEEME.md`), apúntalo en `documentacion/coordinacion.md` y bórralo al acabar. Cambios mínimos en esos archivos.
5. **Commits pequeños, uno por mejora**, en español, con la línea de coautoría de tu modelo. Así Iam puede deshacer una sola cosa.

### 2.2 Técnicas
- **El juego sigue siendo 2D por dentro**: el HD-2D es un «espejo» que lo dibuja en 3D (`espejo_hd2d.gd`). **Nada de la física, los enemigos, las zonas, los diálogos o el guardado puede cambiar.** Con la tecla **H** apagada, el juego debe verse **exactamente igual que antes**.
- **Todo el arte se genera con código** (`herramientas/*.py`, pintor en `herramientas/pintor.py`). **No edites PNG ni OGG a mano**: cambia el programa generador y vuelve a generar. Tras repintar un dibujo del mundo, regenera su mapa de normales (`python3 herramientas/relieve.py <ruta>`).
- **No uses** `construir_mapa.py <mapa> --crear` (sobrescribe mapas). Para repintar un suelo: `pintar_suelo.pintar('<mapa>')`.
- **Rendimiento**: objetivo **60 fotogramas por segundo** en el mapa más grande (`prados_del_eco`, `bosque_cobrizo`, `la_travesia`) y en una pelea con muchos enemigos, en un Mac Intel con gráficos integrados (**GL Compatibility**: ojo, no admite todo lo de Forward+). **Mide antes y después** (milisegundos por fotograma). Si una mejora baja de 60 fps, o no entra, o se pone detrás de una opción de calidad.
- **Pruebas**: hay 35 (`pruebas/prueba_*.gd`), todas deben acabar en «RESULTADO: todo correcto», **sobre todo `prueba_hd2d`**. Si cambias el HD-2D, **amplía `prueba_hd2d`**. Si una falla a veces, repítela antes de dar nada por roto; si falla siempre, la has roto tú.
  ```
  /Applications/Godot.app/Contents/MacOS/Godot --headless --import --path .
  /Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_hd2d
  ```
- **Capturas**: script temporal `pruebas/_captura.gd` (debe ser `extends Node`), lanzado **sin `--headless`**, en segundo plano, que guarde `get_viewport().get_texture().get_image()`. Bórralo (y su `.uid`) al acabar. En este Mac la ventana del juego a veces se frena y no sale la imagen: repite, o espera más. Para comprobar un dibujo suelto, ampliarlo ×4 u ×8.
- `graphify query "<pregunta>"` antes de buscar con grep; `graphify update .` tras cambiar código.
- **No cambies**: historia, diálogos, dificultad, precios, controles ni decisiones apuntadas en `decisiones.md`. Si crees que algo debe cambiar, **propónlo en el informe**.

## 3. Cómo está hecho hoy (para no rehacerlo)

El espejo (`scripts/mundo/hd2d/espejo_hd2d.gd`, se enciende con **H**) ya hace:

| Qué | Cómo |
| --- | --- |
| Suelo | Capa de suelo cercana (un `SubViewport` que mira la escena 2D y se tumba) + suelo pintado lejano; con luz para recibir sombras |
| Peñas | Bloques levantados 1,25 m (2,5 en gargantas); pared del sur con la roca pintada; techo con el dibujo corrido |
| Dibujos | Cada `Sprite2D`/`AnimatedSprite2D` tiene su gemelo `Sprite3D` **de pie** (billboard en Y), con sombra real. `shaded = false` (colores del 2D) |
| Lo dibujado con código | Por canales (`visibility_layer` 13-17): suelo, pantalla (niebla, nevada, ventisca), y **ventanitas** de pie (llamas, halos, el «!») |
| Agua | Hundida 35 cm, con brillo animado y orilla curva |
| Luz y cámara | Sol que sigue el reloj del día, ambiente calibrado; cámara en perspectiva (30°, inclinada 48°), sin niebla 3D, sin bloom |

**Ya medido**: el espejo cuesta lo mismo que el 2D (~7,5 ms/fotograma en los Prados).

**Lo que todavía falta o está flojo** (tu lista de trabajo, de más a menos importante):
1. **No hay postprocesado de HD-2D**: ni profundidad de campo *tilt-shift*, ni bloom, ni viñeta, ni etalonaje de color. Es **lo que más define el aspecto HD-2D**.
2. **Los mapas de normales (`*_n.png`) no se usan en 3D**: los sprites no reciben el relieve de la luz.
3. **Las luces de los faroles, ventanas y fuegos son solo 2D** (`PointLight2D`): en 3D no iluminan el suelo ni los sprites de noche.
4. **El terreno es llano** (salvo peñas y agua): no hay colinas, cuestas ni escalones.
5. **Las sombras son todas iguales** y duras; faltan sombras suaves de contacto y de oclusión ambiental.
6. **Lo de pie que dibujan los enemigos con código** (auras, avisos en el aire) todavía sale tumbado en el suelo.
7. **Cámara**: seguimiento simple; falta amortiguación elástica, anticipación (*look-ahead*), enfoque en diálogos y transiciones.
8. **Partículas 3D** (polvo, chispas, hojas, nieve con profundidad): hoy son 2D en la capa de pantalla.
9. **Hierba y vegetación**: el decorado de hierba es una textura pintada; no hay balanceo con el viento ni se aparta al pasar.
10. Las casas de los bordes de la pantalla se ven **inclinadas** por la perspectiva.

## 4. El método: el bucle de calidad

Para **cada** mejora, sin saltarte pasos:

1. **Mira el «antes»**: captura del juego en 2D y en HD-2D, ampliada. Mide los milisegundos por fotograma.
2. **Escribe en una línea qué está mal y qué es «bien»** (la meta), con una referencia visual concreta («el fondo se desenfoca como en una maqueta, Maisha queda nítida»).
3. **Mejóralo** en su sitio (el espejo, un sombreador, el generador de un sprite).
4. **Mira el «después»** igual que el «antes» y júzgalo **como un director de arte exigente**. Si no está claramente mejor, **repite** (hasta 4 intentos); si no mejora, **deshazlo** y apúntalo como pendiente.
5. **Compruébalo con H apagada**: el 2D no debe cambiar.
6. **Compruébalo en varios mundos**: una pradera, el bosque de otoño, la ciénaga (agua), una cueva oscura (Gruta), la nieve (Sendero Olvidado, Paso de la Escarcha) y una ciudad (Maandiko, Cuna de Musgo), **de día, de noche y al atardecer**.
7. Mide el rendimiento, pasa las pruebas, actualiza `LEEME.md` y `decisiones.md`, y haz el commit.
8. Guarda la comparativa **antes / después** en `documentacion/hd2d/` (una imagen por mejora, lado a lado).

**Nunca des algo por mejorado sin haberlo visto después.** Sé honesta: lo que no quede bien, se dice.

## 5. Qué hacer, por orden

### 5.1 Postprocesado cinematográfico (`hd2d/postproceso`) — lo primero
- **Profundidad de campo *tilt-shift***: nítido en una banda alrededor de Maisha y desenfocado arriba y abajo (efecto maqueta). Si GL Compatibility no tiene DOF de cámara, hazlo con un sombreador de pantalla propio (desenfoque por bandas) y mide.
- **Bloom** suave en lo que brilla (llamas, faroles, runas, ecos), sin quemar la nieve.
- **Etalonaje de color** por hora y por zona (calidez de tarde, azul de noche, verdes de la ciénaga), y **viñeta** muy ligera.
- Un **interruptor de calidad** (alta / media / baja) en el menú de pausa, que también apague el postprocesado.

### 5.2 Iluminación real (`hd2d/luces`)
- **Pasa las luces 2D a luces 3D** (`OmniLight3D`) en faroles, ventanas, braseros, fogatas, runas y el cetro: que iluminen el suelo y los sprites **de noche**. Reutiliza la tabla `LUCES` de `scripts/mundo/relieve.gd`.
- **Usa los mapas de normales** (`*_n.png`) en los gemelos 3D, con un sombreador que combine el color, la normal y las luces. Que los sprites tengan **volumen** con el sol y con las luces cálidas.
- **Sombras suaves** y de contacto (apoyo en el suelo), y oclusión ambiental fingida bajo árboles y casas.

### 5.3 Terreno y profundidad (`hd2d/terreno`)
- **Desniveles reales**: colinas, cuestas y escalones donde el mapa pintado los sugiere (sin cambiar la colisión 2D: es solo aspecto). Peñas con bordes biselados y no solo cajas.
- Agua con **espuma en las orillas y alrededor de lo que toca el agua**, y reflejos suaves.
- Bordes del mapa que **no se vean acabarse** (niebla de profundidad, suelo que se desvanece).

### 5.4 Sprites de calidad máxima (`hd2d/sprites`)
- **Maisha y los aldeanos** (protagonistas): revisa cada animación **dentro del HD-2D**. Si hace falta, genera versiones con **más resolución** (por ejemplo, 2× con pixel art más fino) **solo para el HD-2D** y con el mismo diseño, sin tocar los sprites del 2D. Coloréalos con la paleta de Raíz.
- **Enemigos y jefes**: que cada uno se lea bien con el desenfoque de profundidad y la inclinación de la cámara.
- **Árboles, casas, rocas y decorado**: variedad (más de una versión de lo que se repite), bordes limpios, **sin halos** al recortarlos (revisa el recorte alfa).
- Corrige las casas inclinadas en los bordes (reduce el campo de visión o corrige la perspectiva en esos dibujos).

### 5.5 Cámara (`hd2d/camara`)
- Seguimiento con **amortiguación elástica** y **anticipación** hacia donde corre Maisha.
- **Enfoque suave** hacia quien habla en los diálogos, y **transiciones** al cambiar de escena (que el HD-2D no parpadee).
- **Vibración direccional** en golpes y explosiones, coordinada con `Impacto`.

### 5.6 Partículas y vida (`hd2d/vida`)
- **Partículas 3D** (`GPUParticles3D` o equivalente que funcione en GL Compatibility): polvo y chispas bajo los pies al correr, hojas, nieve y polen con profundidad, luciérnagas, humo de chimeneas.
- **Hierba y arbustos** con balanceo con el viento y que se aparten al pasar Maisha (como texturas animadas o instancias, **midiendo** el coste).

### 5.7 Lo de pie que falta y los remates
- Pon **de pie** lo que dibujan los enemigos con código (auras, avisos).
- Revisa **cada escena** de Raíz y de Sigilia en HD-2D (lista en `LEEME.md`): que no haya cosas flotando, tapadas, sin sombra, con el pie mal puesto o con parpadeos. Corrige lo que veas.
- Si algún mundo se ve mal con la configuración general, dale un **perfil propio** (cámara, color, niebla) en vez de una solución de compromiso.

## 6. Lo que ya nos pasó (no lo repitas)
- Las capturas dentro del juego fallan a ratos en este Mac: repite antes de dar algo por roto.
- Los dibujos sin centrar (`centered = false`) **flotaban** tanto como su altura: comprueba siempre que cada dibujo apoya **por el pie**.
- El suelo salía lavado cuando se le aplicaba una corrección de color de más: **mide el brillo** de 2D y 3D (el suelo al sol debe salir igual de claro) en vez de fiarte del ojo.
- Una capa «sumando luz» no se veía sobre la nieve: prueba lo que dibujes **sobre su fondo real**.
- Una letra de mapa usada dos veces rompió la Gruta: busca antes de usar una nueva (aquí no deberías necesitar ninguna).
- Todo efecto que frene, empuje o tape la pantalla **debe apagarse solo** si nadie lo renueva.

## 7. Tu respuesta final (una sola, con todo)

Entrega **un único mensaje** cuando acabes **todo**, con esta estructura:

1. **Resumen en 5 líneas**: cómo se ve ahora el juego en HD-2D frente a antes.
2. **Tabla general**: una fila por apartado del 5 (qué hiciste, rama, cómo quedó: bien / mejorable).
3. **Por cada apartado**: tabla de mejoras (qué era, qué es, por qué es mejor), **las imágenes antes / después** más importantes (rutas en `documentacion/hd2d/`), los **números medidos** (ms por fotograma antes y después, en qué mapas) y **lo que todavía no te convence**.
4. **Una comparativa de cada mundo** en 2D y en HD-2D, de día y de noche.
5. **Ramas listas para unir**, en orden recomendado (de menos a más riesgo) y qué pruebas pasan en cada una.
6. **Fallos que viste en Sigilia** (la constructora), sin haberlos tocado.
7. **Propuestas que no hiciste** (cambios de diseño, dificultad, ideas nuevas) con ⭐ en tu favorita.
8. Como mucho **3 preguntas** para Iam, con opciones y una ⭐.
9. Termina con «📍 **HD-2D de alta calidad** (…). **Siguiente:** …».

Si tu interfaz te corta antes de terminar, **no entregues a medias**: guarda el avance en `documentacion/hd2d/avance.md` (qué está hecho, qué falta, en qué rama) y sigue desde ahí cuando Iam diga «sigue».

## 8. Cómo hablar con Iam
- **Español** claro, sin tecnicismos; fichas y comparativas en **tablas**.
- **Honestidad**: di lo que ha salido bien y lo que no. Nada de «perfecto» si no lo es.
- **Lenguaje sin género** para Maisha, Mauti y Kimya (nunca «cansada», «sola», «pequeña»…).
- En este encargo **no le preguntas nada por el camino**: donde haya que decidir, elige lo que respete el estilo y las decisiones tomadas, en su propio commit para poder deshacerlo, y explícalo en la respuesta final.
