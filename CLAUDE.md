# Maisha — instrucciones para Claude

Juego en **Godot 4** (pixel art, vista cenital 3/4) de Iam. Todo el arte, la música, los sonidos, los mapas y las
ilustraciones **se generan con código**: los programas de `herramientas/` (Python). Así que aquí se puede seguir
creando jefes, enemigos, animaciones, mapas, música e ilustraciones igual que hasta ahora.

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

## Preparar el Mac (una vez)
```
pip3 install -r herramientas/requirements.txt   # incluye imageio-ffmpeg: el ffmpeg para guardar música y sonidos en .ogg
```
(No hace falta Homebrew: `sintetizador.py` usa el ffmpeg del sistema si lo hay y, si no, el de imageio-ffmpeg.)
Godot está en `/Applications/Godot.app/Contents/MacOS/Godot` (versión 4.7).

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
/Applications/Godot.app/Contents/MacOS/Godot --headless --import --path .
/Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_senda_surcos
```
Hay 31 pruebas (`pruebas/prueba_*.gd`); todas deben acabar en «RESULTADO: todo correcto».
Para capturas: un script temporal `pruebas/_algo.gd` lanzado igual pero sin `--headless`
(guarda `get_viewport().get_texture().get_image()`); bórralo después.

## Dónde estamos
Fase 6. Raíz es un mundo libre con caminos con nombre (Sendero del Puente, Las Pasarelas, Camino Cobrizo,
Senda de los Surcos, Cañada del Eco, Orilla de Juncos, Paso de Piedra y La Travesía hechos; el Sendero Olvidado) y el misterio de los 9 ecos perdidos (los 9 hechos).
El Embarcadero Junco está hecho (casa sellada de Bata, Mamba 2 contra 1, transbordador arreglado con poderes) y La Travesía es un viaje en barca con oleadas (cangrejos y anguilas) y la isla del 7.º eco. La Gruta de las Raíces está hecha (oscuridad, sigilo, escudo con J mantenida, espinos y el Guardián). El Paso de Piedra está hecho (el paso, la casa de Nungu, la llave de Corteza, la cueva de las setas con el 8.º eco y Kuvu, la seta que manda, con Nungu). El 9.º eco está en el reflejo del Lago Espejo y el Guardián abre el sendero con las nueve voces. El Sendero Olvidado tiene hecha la subida (nieve, escarcha de la quietud, braseros, estatuas); y los Quietos (estatuas que solo se mueven cuando no las miras); Las Ruinas del Primer Árbol están hechas: la pelea contra el miedo del árbol (despertar las nueve piedras del recuerdo y romper el corazón de Giza), Mauti libre, la Semilla del Primer Árbol y el final de Raíz. Raíz está completo; lo siguiente es Sigilia (mundo 2). Hay luz 2.5D (relieve, día y noche). Hay Bestiario con rangos (bronce/plata/oro) y enemigos hechiceros (Bundi, Buibui). El Lago Espejo está hecho (agua turbia, Kambare, quietud, puentes del reflejo, Kimya en la isla y su música). Detalles en `LEEME.md` y `documentacion/decisiones.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
