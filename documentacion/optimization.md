# Optimización de Maisha

Cuaderno de trabajo para que el juego vaya más ligero: qué se ha medido, qué se ha hecho y qué queda, ordenado por lo
que se espera ganar. **Objetivo** (del prompt maestro): 60 FPS en el mapa más grande y en una pelea con muchos
enemigos, en un Mac Intel con gráficos integrados (presupuesto: 16,6 ms por fotograma).
**Reglas**: no cambiar el estilo visual ni el juego; nada sin medir antes y después; pasar las 35 pruebas.

## Cómo medir

```
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento                     # 2D, 8 mapas
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento hd2d                # con el espejo HD-2D
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento noche la_travesia   # de noche (luces) y un mapa
godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento pelea               # zona cerrada, ~10 enemigos
godot --headless --path . res://pruebas/ejecutar.tscn -- medir_rendimiento          # solo carga y scripts
```

`pruebas/medir_rendimiento.gd` no es una prueba (no empieza por `prueba_`): carga cada mapa, espera 2 s y mide 4 s
sin vsync. Saca una tabla en Markdown:

| Columna | Qué es | ¿Vale con `--headless`? |
| --- | --- | --- |
| carga ms | Instanciar el mapa y sus 3 primeros fotogramas | Sí |
| ms/fotograma, 1 % peor, FPS | Tiempo real entre fotogramas (media y media del 1 % más lento: los tirones) | No |
| scripts ms | `_process` de **todos** los nodos (un cronómetro va el primero y otro el último) | Sí |
| _draw ms | De ahí a que empieza a pintar: los `_draw` pedidos con `queue_redraw` y lo diferido | No (sin pantalla no se dibuja: sale 0) |
| física ms | `_physics_process` de todos los nodos | Sí |
| dibujo, objetos | Llamadas de dibujo y objetos que pinta la tarjeta gráfica por fotograma | No |
| nodos | Nodos en el árbol | Sí |

**Ojo en macOS**: una ventana tapada, o con la pantalla bloqueada o apagada, **no se pinta** y va frenada a ~145 FPS
(6,90 ms clavados; «dibujo» y «objetos» se quedan congelados en el mismo número en todos los mapas). El medidor pone
la ventana siempre delante, pero hace falta la pantalla encendida y desbloqueada mientras mide.
En la pelea, Maisha no puede caer y golpea cada 20 fotogramas; la zona no invoca más por su cuenta.

## Cuántos objetos tiene cada mapa

Cada árbol o roca (`FIJOS` en `region.gd`) va en `Entidades`, que ordena por altura (y-sort).

| Mapa | Tamaño | Árboles | Otros fijos | Agua (casillas) | Nodos antes | Nodos ahora |
| --- | --- | --- | --- | --- | --- | --- |
| la_travesia | 48×170 | 1613 | 297 | 3133 | 7928 | 4113 |
| bosque_cobrizo | 112×72 | 1229 | 59 | 320 | 5915 | 3350 |
| prados_del_eco | 120×68 | 818 | 52 | 329 | 4089 | 2354 |
| lago_espejo | 96×64 | 564 | 26 | 1697 | 2889 | 1718 |
| cienaga_quieta | 100×68 | 363 | 7 | 1866 | 2499 | 1764 |
| cuna_de_musgo | 64×44 | 312 | 3 | 84 | 1503 | 866 |

## Hecho

### 1. Las sombras ya no miran el reloj en cada fotograma (commit `929dc49`)

| | |
| --- | --- |
| Qué era | Cada `sombra.gd` (una por árbol, roca, casa y personaje) tenía `_process`: preguntaba a `Reloj` la luz en cada fotograma. En La Travesía, **1912 nodos** procesando: casi todo el coste de los scripts |
| Qué es ahora | `Reloj` emite `luz_cambiada` cuando `luz_dia()` o `calidez()` cambian más de 0,01 (o la luz cruza el 0,25 de día/noche). Las sombras hacen la misma comprobación de antes al oír la señal; no tienen `_process` |
| Se ve igual | Sí: la regla de redibujo es la misma (`desp` cambia más de 0,02); solo se mira menos veces |

| Mapa (scripts ms, `--headless`, Mac M4) | Antes | Después |
| --- | --- | --- |
| la_travesia | 4,32 | 0,38 |
| bosque_cobrizo | 3,57 | 0,50 |
| lago_espejo | 2,75 | 0,46 |
| cienaga_quieta | 2,31 | 0,53 |
| cuna_de_musgo | 2,17 | 0,55 |
| prados_del_eco | 2,12 | 0,46 |
| sendero_olvidado | 1,61 | 0,64 |
| maandiko | 0,90 | 0,69 |

En un Mac Intel el ahorro en milisegundos será mayor (allí el GDScript va más lento).

### 2. Medidor completo: carga, `_draw`, pelea (`pruebas/medir_rendimiento.gd`)

### 3. Árboles y rocas: 1 nodo en vez de 4

| | |
| --- | --- |
| Qué era | Cada árbol o roca sencillo era `StaticBody2D` + sombra + `Sprite2D` + `CollisionShape2D` |
| Qué es ahora | `region.gd._fijo_sencillo`: el `Sprite2D` va directo a `Entidades`, con la sombra de hija y `show_behind_parent` (se pinta justo antes del dibujo, en el mismo sitio del orden: **igual que antes**). Las cajas de colisión van todas en un solo `StaticBody2D` («Fijos») con `create_shape_owner` (sin nodos), y las cajas del mismo tamaño comparten la forma |
| Qué no cambia | Los fijos con algo que contar (`COSA`), los postes que muerde Mamba (`ł`), los campamentos y edificios siguen como antes. El grupo `arboles` (Pembe lo usa por la posición) va en el dibujo |
| Medido | Nodos: La Travesía 7928 → 4113, Bosque 5915 → 3350, Prados 4089 → 2354. Carga casi igual (110-125 ms): crear nodos no era lo caro |

## Medidas de partida (Mac M4)

Dibujo, de día, con la ventana delante (antes de los cambios 1 y 3):

| Mapa | ms/fotograma | 1 % peor | Llamadas de dibujo | Objetos |
| --- | --- | --- | --- | --- |
| prados_del_eco | 3,14 | 4,86 | 284 | 973 |
| cuna_de_musgo | 2,39 | 3,81 | 252 | 834 |
| bosque_cobrizo | 4,20 | 5,62 | 378 | 1057 |
| la_travesia | 4,92 | 13,85 | 391 | 857 |

Carga (`--headless`): el **primer** mapa de la partida tarda ~400-600 ms (se cargan por primera vez Maisha, la
interfaz, los sombreadores...); los siguientes, **60-125 ms**, detrás del fundido a negro de 0,3 s de `Estado`.

Pelea (`--headless`, zona cerrada con 10-14 enemigos): scripts 0,43-0,68 ms; física 0,11-0,18 ms.

## Por hacer (en orden)

Lo que falta necesita **la ventana a la vista** (llamadas de dibujo, ms/fotograma, `_draw` y capturas).

| # | Qué | Dónde | Cómo se mide | Estado |
| --- | --- | --- | --- | --- |
| 4 | **Sombras de los fijos fuera del orden por altura**: cada sombra (polígono sin textura) va entre dos dibujos con textura y corta los lotes de dibujo. Pintarlas todas en un nodo por mapa a ras de suelo. Cambia un poco cómo se ve (la sombra de un árbol dejaría de pisar los pies de quien pasa justo detrás): **capturas antes/después para Iam** | `region.gd._fijo_sencillo`, nuevo `scripts/mundo/sombras_fijas.gd` | «dibujo» y ms/fotograma en bosque_cobrizo, la_travesia, prados_del_eco | Falta medir el dibujo con la ventana a la vista |
| 5 | **Trozos fuera de cámara ocultos**: primero un experimento (ocultar los fijos lejanos y comparar ms/fotograma). Si se gana: trozos de 16×16 casillas con `y_sort_enabled` (el orden no cambia) y `visible` según la cámara; apagado con HD-2D | `region.gd`, `escena_mundo.gd` | ms/fotograma con la ventana delante | Sin empezar |
| 6 | **Redibujar solo lo que se ve**: `zona_corrupta.gd` (cada fotograma mientras no esté purgada) y `registro_brotes.gd` | esos dos | `_draw ms` cerca y lejos de una zona (Prados); o Depurador → Perfilador del editor | Sin empezar |
| 7 | **Luces de noche**: si de noche cuesta más de 1 ms que de día, apagar los `PointLight2D` de `relieve.gd` fuera de cámara (cada 0,25 s) | `relieve.gd` | `medir_rendimiento noche` frente al de día | Sin empezar |
| 8 | **Tirones** (1 % peor de La Travesía: 13,85 ms; en pelea hasta 13,7 ms) | — | Perfilador del editor durante las oleadas de La Travesía y en una pelea; solo después, reciclar efectos de combate (`golpe_efecto`, `semilla`, `explosion`, `CHISPA` de `Impacto`) si son ellos | Sin empezar |
| 9 | **HD-2D** (es de Gemini: aquí solo recomendaciones; ver abajo) | `espejo_hd2d.gd` | `medir_rendimiento hd2d` | Sin medir |

**Descartado por ahora** (medido o comprobado):

| Qué | Por qué no |
| --- | --- |
| Carga en hilos o por trozos | 60-125 ms detrás de un fundido de 300 ms: no se nota |
| GDScript sin tipos en lo que va cada fotograma | Todos los scripts juntos ya cuestan menos de 0,8 ms |
| Ajustes de importación de texturas | Bien para pixel art en 2D: sin pérdida, sin mipmaps, filtro «nearest». (Opcional: `detect_3d/compress_to=0` para que el editor no las comprima solo si las ve en 3D) |
| Sobredibujo (transparencias, niebla, rayos de sol) | Todo se pinta a 640×360: casi no cuesta |
| Física en vez de cuadrícula | La física de los fijos ya es un solo cuerpo y cuesta <0,2 ms en pelea; Maisha se mueve libre (no por casillas) |

## Recomendaciones para el HD-2D (para Gemini)

`espejo_hd2d.gd` es de Gemini (`coordinacion.md`). Antes de tocar nada, medir con `medir_rendimiento hd2d`. Ideas:

| Qué | Por qué |
| --- | --- |
| `_process` recorre **todos** los gemelos cada fotograma (y crea `_gemelos.keys()` cada vez) | Con una rejilla por zonas solo se mirarían los cercanos |
| Árboles y rocas como `MultiMeshInstance3D` (un sombreador lee la variante con los datos de cada instancia) | Cientos de `Sprite3D` → unas pocas llamadas de dibujo |
| `visibility_range_end` (con fundido) en vez de comprobar los 30 m a mano | Sin script |
| La capa de suelo (SubViewport de 1024×1024) y hasta 10 ventanitas con `UPDATE_ALWAYS` vuelven a pintar la escena 2D cada una | Probar a refrescar las ventanitas a menos ritmo, o solo si cambian |
| `directional_shadow_max_distance = 60` | La cámara ve ~30 m: con menos distancia, la sombra tiene más detalle y cuesta menos |
| Sin mipmaps, a lo lejos el pixel art tiembla | Niebla suave o un plano lejano más corto lo esconde |

## Fallos encontrados de paso (no son de rendimiento: sin tocar)

| Qué | Dónde | Efecto |
| --- | --- | --- |
| `quieto.gd` no tiene `variante`, y `zona_corrupta._invocar_petrino` se la pone a todo enemigo | Zonas del Sendero Olvidado (`tipos_enemigo` = quieto, petrino, bundi) | Cada tercer enemigo que invoca una zona da error y **no aparece** (el Quieto). Arreglarlo cambia el juego: que lo decida Iam |
