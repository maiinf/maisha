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
| Objetos y enemigos de cada camino | `pintar_sendero.py`, `pintar_pasarelas.py`, `pintar_camino.py`, `pintar_senda.py`, `pintar_canada.py` |
| Ilustraciones de la historia (600×256) | `cinematicas.py <nombre>` (y `cinematicas_*.py`) |
| Efectos y ambientes | `crear_sonidos.py [nombres]` |
| Música | `componer_musica.py [nombres]` |
| Interfaz de diario | `pintar_interfaz.py`, `pintar_inicio_mesa.py` |

Para comprobar el arte, mira los PNG que salen (abrirlos con la herramienta de leer imágenes).

## Mapas
Cada mapa es `datos/mapas/<mapa>.txt` (una letra por casilla de 16 px) + `.puertas` + `.zonas`.
Letras nuevas de los caminos: `0` peña, `"` obstáculo que se abre (pasarela rota / derrumbe / foso / escala de cuerda, según el
`viajero` del nodo Region), `@` eco perdido, `` ` `` objeto del encargo, `{` casa del viajero, `}` viajero,
`-` `|` `'` puente de piedra, pretil y vado. Puertas: `letra = id, destino, puerta_llegada, salida[, cerrada:marca]`.
El grafo de caminos para la flecha de misiones está en `datos/misiones.json` → `caminos`.

## Pruebas
```
/Applications/Godot.app/Contents/MacOS/Godot --headless --import --path .
/Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_senda_surcos
```
Hay 20 pruebas (`pruebas/prueba_*.gd`); todas deben acabar en «RESULTADO: todo correcto».
Para capturas: un script temporal `pruebas/_algo.gd` lanzado igual pero sin `--headless`
(guarda `get_viewport().get_texture().get_image()`); bórralo después.

## Dónde estamos
Fase 6. Raíz es un mundo libre con caminos con nombre (Sendero del Puente, Las Pasarelas, Camino Cobrizo,
Senda de los Surcos y Cañada del Eco hechos; faltan 4) y el misterio de los 9 ecos perdidos (5 hechos).
Siguiente: el Lago Espejo (su gancho: el reflejo; el paso desde la Cañada está cerrado con la marca `camino_lago`). Detalles en `LEEME.md` y `documentacion/decisiones.md`.
