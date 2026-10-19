# Optimización de Maisha

Cuaderno de trabajo para que el juego vaya más ligero. Qué se ha medido, qué se ha hecho y qué queda por mirar,
ordenado por lo que más se espera ganar. **Objetivo** (del prompt maestro): 60 FPS en el mapa más grande y en una
pelea con muchos enemigos, en un Mac Intel con gráficos integrados (presupuesto: 16,6 ms por fotograma).

## Cómo medir

```
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento                     # 2D, 8 mapas
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento hd2d                # con el espejo HD-2D
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento noche la_travesia   # de noche (luces) y un mapa
godot --headless --path . res://pruebas/ejecutar.tscn -- medir_rendimiento          # solo el coste de los scripts
```

`pruebas/medir_rendimiento.gd` no es una prueba (no empieza por `prueba_`): carga cada mapa, espera 2 s y mide 4 s
sin vsync. Saca una tabla en Markdown:

| Columna | Qué es |
| --- | --- |
| ms/fotograma, 1 % peor, FPS | Tiempo real entre fotogramas (media y la media del 1 % más lento: los tirones) |
| scripts ms | `_process` de **todos** los nodos (un cronómetro va el primero y otro el último) |
| física ms | Lo mismo con `_physics_process` |
| dibujo, objetos | Llamadas de dibujo y objetos que pinta la tarjeta gráfica por fotograma |
| nodos | Nodos que hay en el árbol |

**Ojo en macOS**: si la ventana de Godot no está delante (o se lanza con `--headless`), el sistema la frena a
~145 FPS (6,90 ms clavados). Entonces los ms/fotograma no valen, pero la columna «scripts ms» sí.
Para medir el dibujo, dejar la ventana delante y no tocar nada mientras mide.

## Cuántos objetos tiene cada mapa

Cada árbol o roca (`FIJOS` en `region.gd`) es un `StaticBody2D` con su dibujo, su colisión y su sombra
(`sombra.gd`). Todos van en `Entidades`, que ordena por altura (y-sort).

| Mapa | Tamaño | Árboles | Otros fijos | Agua (casillas) | Nodos |
| --- | --- | --- | --- | --- | --- |
| la_travesia | 48×170 | 1613 | 297 | 3133 | 7928 |
| bosque_cobrizo | 112×72 | 1229 | 59 | 320 | 5915 |
| sendero_del_puente | 140×46 | 829 | 35 | 553 | — |
| prados_del_eco | 120×68 | 818 | 52 | 329 | 4089 |
| camino_cobrizo | 64×100 | 710 | 27 | 185 | — |
| lago_espejo | 96×64 | 564 | 26 | 1697 | 2889 |
| embarcadero_junco | 96×72 | 559 | 38 | 1798 | — |

## Hecho

### 1. Las sombras ya no miran el reloj en cada fotograma

| | |
| --- | --- |
| Qué era | Cada `sombra.gd` (una por árbol, roca, casa y personaje) tenía `_process`: preguntaba a `Reloj` la luz en cada fotograma para ver si el sol se había movido. En La Travesía eran **1912 nodos** procesando, y casi todo el coste de los scripts del juego |
| Qué es ahora | `Reloj` emite `luz_cambiada` cuando `luz_dia()` o `calidez()` cambian más de 0,01 (o la luz cruza el 0,25 de día/noche). Las sombras escuchan esa señal y hacen la misma comprobación de antes; no tienen `_process` |
| Se ve igual | Sí: el redibujo sigue saliendo de la misma regla (`desp` cambia más de 0,02); solo se mira menos veces |

Medido con `--headless` en un Mac M4 (columna «scripts ms»):

| Mapa | Antes | Después |
| --- | --- | --- |
| la_travesia | 4,32 ms | 0,38 ms |
| bosque_cobrizo | 3,57 ms | 0,50 ms |
| lago_espejo | 2,75 ms | 0,46 ms |
| cienaga_quieta | 2,31 ms | 0,53 ms |
| cuna_de_musgo | 2,17 ms | 0,55 ms |
| prados_del_eco | 2,12 ms | 0,46 ms |
| sendero_olvidado | 1,61 ms | 0,64 ms |
| maandiko | 0,90 ms | 0,69 ms |

En un Mac Intel el ahorro será mayor en milisegundos (el GDScript va más lento allí).

### Antes (rama `revision/rendimiento`)
Aldeanos con `tiene_novedad` en caché, ambiente sin `filter()` por fotograma, nubes fuera de cámara descartadas,
`luz_sol.gd` con los grupos en caché, textura radial de luz compartida (`Relieve.textura_luz`). Ver
`decisiones.md` → «Optimización y rendimiento».

## Medida de partida del dibujo (2D, de día, Mac M4, ventana delante)

| Mapa | ms/fotograma | 1 % peor | Dibujo | Objetos |
| --- | --- | --- | --- | --- |
| prados_del_eco | 3,14 | 4,86 | 284 | 973 |
| cuna_de_musgo | 2,39 | 3,81 | 252 | 834 |
| bosque_cobrizo | 4,20 | 5,62 | 378 | 1057 |
| la_travesia | 4,92 | 13,85 | 391 | 857 |

(Antes del arreglo de las sombras. Falta repetirla con la ventana delante para el resto de mapas, de noche y en HD-2D.)

## Por mirar (ideas, sin medir aún)

| # | Dónde | Sospecha | Idea |
| --- | --- | --- | --- |
| 1 | `Entidades` (y-sort) | Miles de nodos fijos en un solo nodo con y-sort; Godot ordena todos los hijos cada fotograma, se vean o no | Trocear el mapa en bloques (p. ej. 16×16 casillas) y apagar los que están fuera de cámara (`visible = false` o `VisibleOnScreenEnabler2D`). Medir antes |
| 2 | Lotes de dibujo (batching) | ~250-400 llamadas de dibujo. Cada árbol alterna su sombra (polígono sin textura) con su dibujo (CanvasTexture con relieve): eso rompe los lotes | Dibujar las sombras de los fijos todas juntas en un nodo por mapa (debajo, z más bajo), o pintarlas en el suelo con `pintar_suelo.py` |
| 3 | Picos de La Travesía | El 1 % peor es 13,85 ms (casi 3 veces la media): hay tirones | Mirar con el perfilador de Godot qué pasa en esos fotogramas (oleadas, enemigos que aparecen, `queue_free`) |
| 4 | `zona_corrupta.gd` | Se redibuja en cada fotograma aunque esté fuera de cámara | Redibujar solo si se ve (`VisibleOnScreenNotifier2D`) |
| 5 | Luces de noche (`relieve.gd`) | Cada ventana, farol y fuego es un `PointLight2D`; con relieve (normales) cada luz encarece lo que toca | Medir `medir_rendimiento noche`; si pesa, apagar las luces fuera de cámara o bajar `rendering/2d/...` |
| 6 | Carga de los mapas | `region.gd` crea miles de nodos en `_ready` y `relieve.gd` le cambia la textura a cada dibujo después | Medir el tiempo de carga; si es largo, crear los fijos por trozos o compartir las CanvasTexture (ya hay caché por ruta) |
| 7 | HD-2D (`espejo_hd2d.gd`) | `_process` recorre **todos** los gemelos en cada fotograma (y crea `_gemelos.keys()` cada vez); la capa de suelo (SubViewport de 1024×1024) y hasta 10 ventanitas vuelven a pintar la escena 2D | **Es de Gemini** (`coordinacion.md`: Claude no toca el subsistema 3D). Medir con `medir_rendimiento hd2d` y dejar el aviso en el tablón |

## Reglas

- Medir antes y después; apuntar los números aquí y en `decisiones.md`.
- Que se vea **igual** (o mejor): si algo cambia a la vista, enseñar capturas a Iam antes.
- Pasar las pruebas (`RESULTADO: todo correcto` en todas).
