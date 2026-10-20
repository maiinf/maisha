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

### 4. Las sombras de los árboles y rocas, juntas en una malla por trozo

| | |
| --- | --- |
| Qué era | Cada sombra era un polígono suelto entre el dibujo de su árbol y el del vecino. En el renderizador de compatibilidad **cada polígono es una llamada de dibujo**, y además partía los lotes de los árboles |
| Qué es ahora | `region.gd._sombra_fija` las reparte en trozos de 256 px (`Region/SombrasFijas`, z −1: sobre el suelo, las zonas y las marcas; bajo todo lo que va de pie). Cada trozo (`scripts/mundo/trozo_sombra.gd`) junta sus elipses en **una malla** (una llamada de dibujo) y la rehace solo cuando el sol se mueve. Godot salta los trozos que no se ven. Las elipses son las mismas (`sombra.gd` → `puntos()` y `color()`) |
| Se ve igual | Capturas de Bosque, Travesía y Prados comparadas píxel a píxel: solo cambia lo animado (Maisha respirando, la barca, hojas). Ver `documentacion/revision/sombras_fijas_antes_despues.png`. (En teoría, la sombra de un árbol ya no pisa los pies de quien está justo detrás; en las capturas de Maisha detrás de un tronco no se nota) |
| HD-2D | El nombre acaba en «sombra.gd» a propósito: el espejo esconde esas sombras pintadas igual que las de `sombra.gd`. `prueba_hd2d` pasa |

Con la ventana delante (Mac M4, de día):

| Mapa | ms/fotograma antes → después | Llamadas de dibujo antes → después |
| --- | --- | --- |
| la_travesia | 2,38 → **1,45** | 392 → **157** |
| bosque_cobrizo | 2,85 → **2,11** | 378 → **183** |
| prados_del_eco | 2,67 → **2,06** | 284 → **148** |
| cuna_de_musgo | 1,92 → **1,52** | 252 → **119** |
| lago_espejo | 2,44 → **2,11** | 332 → **285** |
| sendero_olvidado | 1,90 → **1,72** | 131 → **94** |
| cienaga_quieta | 2,63 → **2,44** | 195 → **142** |
| Pelea en bosque_cobrizo | 2,78 → **2,38** | 318 → **227** |

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
| 6 | **Redibujar solo lo que se ve**: `_draw` cuesta 0,14-0,77 ms por fotograma (lo más alto, la Ciénaga). Primero averiguar qué script lo gasta | `zona_corrupta.gd`, `registro_brotes.gd`, `ambiente.gd`, `decorado.gd`, `luz_sol.gd` | `_draw ms` apagando el redibujo de cada uno | En marcha |
| 8 | **Tirones** en pelea (1 % peor hasta 4,7 ms) | — | Perfilador del editor; solo si salen, reciclar efectos de combate (`golpe_efecto`, `semilla`, `explosion`, `CHISPA` de `Impacto`) | Ya no hay tirones claros: ver abajo |
| 9 | **HD-2D** (es de Gemini: aquí solo recomendaciones; ver abajo) | `espejo_hd2d.gd` | `medir_rendimiento hd2d` | Medido; aviso en `coordinacion.md` |

**Medido y descartado:**

| Qué | Experimento | Resultado |
| --- | --- | --- |
| 5. Ocultar los árboles fuera de cámara | Ocultar los fijos a más de 400×260 px de Maisha | Travesía 2,40 → 2,09 ms, Bosque 2,83 → 2,71, Prados 2,75 → 2,65: poco (Godot ya salta lo que no se ve). Con las sombras en trozos, aún menos. No compensa el riesgo con el HD-2D |
| 7. Luces de noche | `medir_rendimiento noche` frente al de día | Igual que de día (±0,1 ms; Maandiko dio un pico suelto). No hace falta |
| Tirones de La Travesía | El 1 % peor era 13,85 ms | Tras el cambio 1 (sombras sin `_process`) es 3,2-3,9 ms: los tirones eran las 1912 sombras |

**Descartado por ahora** (medido o comprobado):

| Qué | Por qué no |
| --- | --- |
| Carga en hilos o por trozos | 60-125 ms detrás de un fundido de 300 ms: no se nota |
| GDScript sin tipos en lo que va cada fotograma | Todos los scripts juntos ya cuestan menos de 0,8 ms |
| Ajustes de importación de texturas | Bien para pixel art en 2D: sin pérdida, sin mipmaps, filtro «nearest». (Opcional: `detect_3d/compress_to=0` para que el editor no las comprima solo si las ve en 3D) |
| Sobredibujo (transparencias, niebla, rayos de sol) | Todo se pinta a 640×360: casi no cuesta |
| Física en vez de cuadrícula | La física de los fijos ya es un solo cuerpo y cuesta <0,2 ms en pelea; Maisha se mueve libre (no por casillas) |

## Recomendaciones para el HD-2D (para Gemini)

`espejo_hd2d.gd` es de Gemini (`coordinacion.md`). Medido con `medir_rendimiento hd2d` (Mac M4, de día):

| Mapa | 2D ms | HD-2D ms | Llamadas de dibujo HD-2D | Scripts HD-2D ms |
| --- | --- | --- | --- | --- |
| bosque_cobrizo | 2,85 | 7,76 | 679 | 1,92 |
| cienaga_quieta | 2,63 | 7,55 | 446 | 1,23 |
| lago_espejo | 2,44 | 7,39 | 513 | 1,11 |
| la_travesia | 2,38 | 5,70 | 693 | 1,90 |
| prados_del_eco | 2,67 | 4,37 | 382 | 0,95 |

**Fallo** (avisado en `coordinacion.md`): `espejo_hd2d.gd:370` asigna a una variable con tipo un objeto ya liberado antes
de comprobarlo; desde que se recoge o desaparece un objeto de pie, `_mover_capas` se corta en cada fotograma (~150
errores por segundo) y las ventanitas dejan de moverse.

Ideas:

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
