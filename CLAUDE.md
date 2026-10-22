# Maisha — instrucciones para Claude

Juego en **Godot 4** (pixel art, vista cenital 3/4) de Iam. Todo el arte, la música, los sonidos, los mapas y las
ilustraciones **se generan con código**: los programas de `herramientas/` (Python). Así que aquí se puede seguir
creando jefes, enemigos, animaciones, mapas, música e ilustraciones igual que hasta ahora.

## Nuevo Rumbo del Proyecto y Coexistencia de Agentes (IMPORTANTE)
1. **Evolución HD-2D y Arquitectura 3D Sólida**:
   - El proyecto evoluciona hacia una estética **HD-2D de alta calidad** (*Octopath Traveler*, *Triangle Strategy*): cámara en perspectiva, sombras dinámicas, agua translúcida con profundidad y estructuras clave modeladas en **3D sólido en Blender (.glb)** para eliminar el efecto "plano de papel" al rodearlas, conservando texturas pixel art puras (paleta oficial).
   - **Compatibilidad 2D absoluta**: Con la tecla **H** apagada, el juego 2D tradicional sigue funcionando al 100% idéntico. La lógica narrativa, colisiones 2D, misiones y diálogos no se alteran.
2. **Reparto de roles entre agentes**:
   - **Claude (Constructora - tú)**: Trabaja en `C:\Users\iamin\Proyectos\maisha` (rama `main`). Te encargas del **contenido 2D**: Sigilia, mapas, diálogos naturales, misiones, combate y NPCs.
   - **Gemini (Arquitecto Visual / Revisora)**: Trabaja en `C:\Users\iamin\Proyectos\maisha-revision` (rama `hd2d/calidad-blender`). Se encarga de los modelos 3D sólidos en Blender (`herramientas/blender/generador_3d_maisha.py`), los `.glb`, shaders y motor `scripts/mundo/hd2d/espejo_hd2d.gd`.
   - **Canal de comunicación**: `documentacion/coordinacion.md` contiene avisos cruzados en `[Avisos de Claude para Gemini]` y `[Avisos de Gemini para Claude]`.
3. **Entorno en Windows**:
   - **Godot 4.7.2**: `C:\Users\iamin\Godot\extraido\Godot_v4.7.2-stable_win64_console.exe`
   - **Blender 5.2.3 LTS**: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`
   - **Python 3.14**: `python` (con requirements instalados: numpy, pillow, opencv, scipy, imageio-ffmpeg)
   - **Bocetos**: `documentacion/boceto_bibliotecario.png` y `herramientas/boceto_bibliotecario.py` ya están integrados en ambos repositorios tras el traslado.

## Cómo trabajar con Iam (reglas del prompt maestro)
- Escribe siempre en **español**, claro y sin tecnicismos innecesarios. Las fichas y especificaciones, en **tablas**.
- **Paso a paso**: una cosa cada vez. La calidad es lo primero. Sé honesto con lo que queda mal o falta.
- Como mucho **3 preguntas** por mensaje, cada una con opciones y una recomendada con ⭐.
- **Enseña imágenes antes de decidir** (capturas o bocetos).
- Lenguaje **sin género** para Maisha, Mauti y Kimya.
- Le gustan las animaciones detalladas; se puede crear música nueva.
- Termina cada mensaje con «📍 **Fase X, paso Y** (…). **Siguiente:** …».
- Apunta las decisiones en el GDD (sección «Registro de decisiones»). El GDD vive en claude.ai; si no hay acceso,
  apúntalas en `documentacion/decisiones.md`.
- Al acabar un cambio: actualiza `LEEME.md`, pasa las pruebas y haz **commit** (y push si Iam lo pide).

## Herramientas (en `herramientas/`)
| Qué | Programa |
| --- | --- |
| El pintor (lienzo con luz, volumen, ruido, sprites) | `pintor.py` |
| Suelo pintado de un mapa | `pintar_suelo.py` (lo llama `construir_mapa.py`) |
| Mapas (texto → JSON + suelo + zonas) | `construir_mapa.py <mapa> [--crear]` (con `--crear` se rehace el mapa y **se sobrescribe**) |
| Aldeanos (24×32, frente) | `dibujar_aldeanos.py` |
| Enemigos hechiceros (búho-mago, araña-bruja) | `pintar_hechiceros.py` |
| Objetos y enemigos de cada camino | `pintar_olvidado.py`, `pintar_sendero.py`, `pintar_pasarelas.py`, `pintar_camino.py`, `pintar_senda.py`, `pintar_canada.py`, `pintar_orilla.py`, `pintar_lago.py`, `pintar_embarcadero.py`, `pintar_travesia.py`, `pintar_gruta.py`, `pintar_paso.py` |
| Ilustraciones de la historia (600×256) | `cinematicas.py <nombre>` (y `cinematicas_*.py`) |
| El Primer Árbol y Mauti | `pintar_primer_arbol.py` |
| Sigilia: Paso de la Escarcha (estelas) | `pintar_escarcha.py` |
| Sigilia: Maandiko (casas, Archivo, puestos, fuente, charcos) | `pintar_maandiko.py` |
| Sigilia: tienda de Wino | `pintar_tienda_wino.py` |
| Sigilia: Las Estanterías (escalera, tintero, atril) | `pintar_estanterias.py` |
| Efectos y ambientes | `crear_sonidos.py [nombres]` |
| Música | `componer_musica.py [nombres]` |
| Interfaz de diario | `pintar_interfaz.py`, `pintar_inicio_mesa.py` |
| Relieve de los dibujos (luz 2.5D) | `relieve.py --todo` (relanzar al repintar un dibujo del mundo) |

Para comprobar el arte, mira los PNG que salen (abrirlos con la herramienta de leer imágenes).

## Mapas
Cada mapa es `datos/mapas/<mapa>.txt` (una letra por casilla de 16 px) + `.puertas` + `.zonas`.
Letras nuevas de los caminos: `0` peña, `"` obstáculo que se abre (pasarela rota / derrumbe / foso / escala de cuerda, según el
`viajero` del nodo Region), `\` puente del reflejo (Lago Espejo), `@` eco perdido, `` ` `` objeto del encargo, `{` casa del viajero, `}` viajero,
`-` `|` `'` puente de piedra, pretil y vado. Puertas: `letra = id, destino, puerta_llegada, salida[, cerrada:marca]`.
El grafo de caminos para la flecha de misiones está en `datos/misiones.json` → `caminos`.

## Pruebas
```
& "C:\Users\iamin\Godot\extraido\Godot_v4.7.2-stable_win64_console.exe" --headless --import --path .
& "C:\Users\iamin\Godot\extraido\Godot_v4.7.2-stable_win64_console.exe" --headless --path . res://pruebas/ejecutar.tscn -- prueba_senda_surcos
```
Hay 35 pruebas (`pruebas/prueba_*.gd`); todas deben acabar en «RESULTADO: todo correcto».

## Dónde estamos
Fase 6. Raíz es un mundo libre con caminos con nombre (Sendero del Puente, Las Pasarelas, Camino Cobrizo,
Senda de los Surcos, Cañada del Eco, Orilla de Juncos, Paso de Piedra y La Travesía hechos; el Sendero Olvidado) y el misterio de los 9 ecos perdidos (los 9 hechos).
El Embarcadero Junco está hecho (casa sellada de Bata, Mamba 2 contra 1, transbordador arreglado con poderes) y La Travesía es un viaje en barca con oleadas (cangrejos y anguilas) y la isla del 7.º eco. La Gruta de las Raíces está hecha (oscuridad, sigilo, escudo con J mantenida, espinos y el Guardián). El Paso de Piedra está hecho (el paso, la casa de Nungu, la llave de Corteza, la cueva de las setas con el 8.º eco y Kuvu, la seta que manda, con Nungu). El 9.º eco está en el reflejo del Lago Espejo y el Guardián abre el sendero con las nueve voces. El Sendero Olvidado tiene hecha la subida (nieve, escarcha de la quietud, braseros, estatuas); y los Quietos (estatuas que solo se mueven cuando no las miras); Las Ruinas del Primer Árbol están hechas: la pelea contra el miedo del árbol (despertar las nueve piedras del recuerdo y romper el corazón de Giza), Mauti libre, la Semilla del Primer Árbol y el final de Raíz. Raíz está completo. Fase 7: Sigilia (mundo 2, armiños escribas y el miedo a olvidar; arte en `arte/mundos/sigilia/`); hecho el Paso de la Escarcha entero (nieve honda, ventisca de páginas, Taa el farolero en blanco, la primera ficha del Índice, el sigilo de fuego con U, los faroles rúnicos, las páginas sueltas, la Puerta Sellada, su misión y su música «La nieve que escribe»). Maandiko hecho (partes 1 y 2: con la tienda de Wino y los faroles de Taa); Las Estanterías Colgantes, parte 1 (escaleras rodantes, tinteros, la ficha de Daftari). Maandiko, la ciudad, parte 1 (la ciudad, Kalamu con el trozo del mapa, Mauti, Wino, Taa, los escribas en blanco, los charcos de Tinta Quieta y su música). Hay luz 2.5D (relieve, día y noche). **HD-2D en marcha**: el espejo `scripts/mundo/hd2d/espejo_hd2d.gd` dibuja cualquier escena en 3D sin cambiar el juego (tecla H). Hay Bestiario con rangos (bronce/plata/oro) y enemigos hechiceros (Bundi, Buibui). El Lago Espejo está hecho (agua turbia, Kambare, quietud, puentes del reflejo, Kimya en la isla y su música). Detalles en `LEEME.md` y `documentacion/decisiones.md`.

## graphify
This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
