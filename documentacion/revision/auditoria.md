# Auditoría Inicial Completa · Maisha

Fecha: 16 de octubre de 2026  
Autora: IA Revisora (modo completo y autónomo)

---

## 1. Datos de partida (mediciones base)

### 1.1 Tamaño de carpetas y recursos

| Carpeta | Archivos | Tamaño en disco | Observaciones |
| --- | ---: | ---: | --- |
| `arte/` (total) | 557 | 17,22 MB (17.628,2 KB) | Incluye dibujos y mapas de normales (`_n.png`) |
| `arte/mundos/` | 322 | 14,42 MB (14.768,9 KB) | Los suelos pintados representan ~11,8 MB en PNG |
| `arte/zonas/` | 76 | 1,17 MB (1.196,2 KB) | Zonas corruptas y jefes/enemigos de Raíz (sin `_n.png`) |
| `arte/historia/` | 26 | 0,90 MB (919,2 KB) | 26 ilustraciones de 600×256 |
| `arte/interfaz/` | 26 | 0,64 MB (650,6 KB) | Diario, bolsa, iconos y mesa de inicio |
| `arte/personajes/` | 94 | 0,07 MB (70,5 KB) | Maisha, prendas y aldeanos (sin `_n.png`) |
| `audio/` (total) | 197 | 35,40 MB (36.248,3 KB) | Todo generado en `.ogg` desde Python |
| `audio/musica/` | 44 | 27,69 MB (28.358,4 KB) | Pistas de zona, jefes y fanfarrias |
| `audio/sonidos/` | 147 | 5,08 MB (5.199,6 KB) | Efectos de combate, mundo e interfaz |
| `audio/ambiente/` | 6 | 2,63 MB (2.690,4 KB) | Agua, brisa, ciénaga, fuego, pájaros, viento |

### 1.2 Rendimiento de partida por mapa (carga, tiempo por fotograma y nodos)

| Mapa | Tiempo de carga | Tiempo por fotograma | FPS equivalentes | Nodos en escena |
| --- | ---: | ---: | ---: | ---: |
| `kitovu` | 2003,1 ms | 7,02 ms | 142 fps | 1.976 |
| `prados_del_eco` | 244,8 ms | 6,75 ms | 148 fps | 4.049 |
| `cuna_de_musgo` | 149,4 ms | 6,83 ms | 146 fps | 1.464 |
| `sendero_del_puente` | 196,2 ms | 6,81 ms | 147 fps | 3.710 |
| `las_pasarelas` | 224,5 ms | 6,88 ms | 145 fps | 752 |
| `camino_cobrizo` | 180,9 ms | 6,81 ms | 147 fps | 3.273 |
| `bosque_cobrizo` | 243,9 ms | 6,62 ms | 151 fps | 5.875 |
| `cienaga_quieta` | 218,2 ms | 6,70 ms | 149 fps | 2.459 |
| `senda_surcos` | 185,3 ms | 6,83 ms | 146 fps | 2.217 |
| `campo_segado` | 162,9 ms | 6,75 ms | 148 fps | 2.819 |
| `canada_eco` | 205,6 ms | 6,82 ms | 147 fps | 1.252 |
| `lago_espejo` | 281,1 ms | 6,55 ms | 153 fps | 2.849 |
| `orilla_juncos` | 182,2 ms | 6,81 ms | 147 fps | 2.232 |
| `embarcadero_junco` | 241,7 ms | 6,80 ms | 147 fps | 3.173 |
| `la_travesia` | 281,7 ms | 6,67 ms | 150 fps | 7.887 |
| `gruta_raices` | 173,4 ms | 9,00 ms | 111 fps | 530 |
| `paso_piedra` | 186,3 ms | 6,85 ms | 146 fps | 1.003 |
| `cueva_setas` | 221,3 ms | 6,82 ms | 147 fps | 373 |
| `sendero_olvidado` | 190,0 ms | 6,71 ms | 149 fps | 1.177 |
| `ruinas_primer_arbol` | 201,7 ms | 6,69 ms | 149 fps | 286 |

### 1.3 Volumen y duración de cada pista musical y ambiente (`audio/`)

| Pista | Tipo | Duración | Volumen medio | Pico máximo | Tamaño | Estado inicial |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `kitovu.ogg` | Exploración | 78,0 s | -19,6 dB | -2,0 dB | 937 KB | Mejorable (muy baja frente al resto) |
| `despertar.ogg` | Cinemática | 60,4 s | -20,1 dB | -2,1 dB | 950 KB | Bien (empieza suave a propósito) |
| `inicio.ogg` | Menú | 58,2 s | -16,8 dB | -1,9 dB | 706 KB | Bien |
| `prados.ogg` | Exploración | 40,0 s | -16,0 dB | -1,8 dB | 687 KB | Mejorable (bucle corto de 40 s) |
| `aldea.ogg` | Exploración | 43,6 s | -15,5 dB | -2,0 dB | 701 KB | Bien |
| `interior.ogg` | Interior | 36,6 s | -18,4 dB | -1,9 dB | 418 KB | Mejorable (2,4 dB más baja que exterior) |
| `noche.ogg` | Cinemática | 40,7 s | -17,1 dB | -1,9 dB | 412 KB | Bien |
| `bosque.ogg` | Exploración | 50,5 s | -15,1 dB | -2,0 dB | 787 KB | Bien |
| `cienaga.ogg` | Exploración | 61,9 s | -13,8 dB | -1,9 dB | 682 KB | Mejorable (+2,2 dB más fuerte que la media) |
| `campo.ogg` | Exploración | 45,7 s | -15,3 dB | -1,9 dB | 664 KB | Bien |
| `sendero.ogg` | Camino | 40,0 s | -16,1 dB | -1,9 dB | 695 KB | Mejorable (bucle de 40 s) |
| `pasarelas.ogg` | Camino | 55,4 s | -15,8 dB | -1,9 dB | 790 KB | Bien |
| `cobrizo.ogg` | Camino | 41,7 s | -15,3 dB | -2,1 dB | 675 KB | Bien |
| `surcos.ogg` | Camino | 43,6 s | -16,0 dB | -1,9 dB | 710 KB | Bien |
| `canada.ogg` | Camino | 49,2 s | -16,7 dB | -1,8 dB | 743 KB | Bien |
| `lago.ogg` | Exploración | 58,2 s | -17,1 dB | -1,9 dB | 849 KB | Mejorable (un poco baja) |
| `orilla.ogg` | Camino | 65,5 s | -16,5 dB | -1,8 dB | 988 KB | Bien |
| `embarcadero.ogg` | Exploración | 80,0 s | -16,6 dB | -1,9 dB | 1202 KB | Bien |
| `travesia.ogg` | Camino | 57,6 s | -15,8 dB | -1,9 dB | 897 KB | Bien |
| `gruta.ogg` | Exploración | 73,8 s | -14,2 dB | -1,9 dB | 645 KB | Mejorable (+1,8 dB alta para ser cueva de sigilo) |
| `paso.ogg` | Camino | 45,7 s | -14,3 dB | -1,8 dB | 580 KB | Mejorable (+1,7 dB alta) |
| `setas.ogg` | Exploración | 50,5 s | -16,4 dB | -1,8 dB | 816 KB | Bien |
| `olvidado.ogg` | Camino | 64,0 s | -14,0 dB | -1,8 dB | 755 KB | Mejorable (+2,0 dB alta) |
| `ruinas.ogg` | Exploración | 68,6 s | -13,4 dB | -2,0 dB | 579 KB | Mal (+2,6 dB por encima de la media; satura el ambiente) |
| `escarcha.ogg` | Sigilia | 68,6 s | -14,4 dB | -1,9 dB | 837 KB | Intocable (Sigilia) |
| `tienda.ogg` | Interfaz | 34,3 s | -17,7 dB | -1,9 dB | 641 KB | Mejorable (-1,7 dB baja) |
| `raiz_libre.ogg` | Final | 58,4 s | -18,8 dB | -1,9 dB | 727 KB | Mejorable (-2,8 dB baja para el cierre épico) |
| `combate.ogg` | Combate | 33,1 s | -16,5 dB | -1,9 dB | 549 KB | Mejorable (debería sonar a -15,5 dB) |
| `jefe.ogg` (Mzizi) | Jefe | 38,7 s | -15,5 dB | -1,9 dB | 567 KB | Bien |
| `jefe_pembe.ogg` | Jefe | 36,4 s | -16,3 dB | -1,9 dB | 557 KB | Mejorable (un poco baja para jefe) |
| `jefe_konokono.ogg` | Jefe | 51,4 s | -17,5 dB | -1,9 dB | 730 KB | Mal (-2,5 dB más baja que otros jefes) |
| `jefe_cosechadora.ogg` | Jefe | 61,9 s | -15,6 dB | -2,0 dB | 961 KB | Bien |
| `jefe_kambare.ogg` | Jefe | 55,4 s | -16,0 dB | -1,9 dB | 812 KB | Bien |
| `jefe_mamba.ogg` | Jefe | 49,7 s | -14,4 dB | -1,9 dB | 681 KB | Mejorable (+1,1 dB fuerte) |
| `jefe_guardian.ogg` | Jefe | 62,6 s | -15,7 dB | -1,9 dB | 855 KB | Bien |
| `jefe_kuvu.ogg` | Jefe | 60,0 s | -18,1 dB | -1,9 dB | 865 KB | Mal (-3,1 dB más baja que otros jefes) |
| `jefe_arbol.ogg` | Jefe | 76,8 s | -14,7 dB | -1,9 dB | 913 KB | Bien |

---

## 2. Inventario por área (de mayor a menor prioridad)

### 2.1 Sprites y animaciones (`revision/sprites`)

| Elemento | Archivo / Generador | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Gestos de aldeanos (bastones/pértigas) | `dibujar_aldeanos.py`, `dibujar_kitovu.py` | **Mal** | En el fotograma 4 del gesto de Shamba, Bibi, Bata, Mbuzi y Msafiri, el bastón se corta 2-4 px antes del suelo dejando la punta flotando desconectada. | Alta |
| Animaciones de Pembe y Konokono | `dibujar_pembe.py`, `dibujar_konokono.py` | **Mal** | Píxeles huérfanos flotantes en fotograma 3 de `pembe.png` y fotograma 6 de `konokono.png`. | Alta |
| Petrino y Jabalí de hierro | `dibujar_criaturas.py`, `dibujar_jabali.py` | **Mejorable** | Sombreado muy plano en bloque frente a enemigos recientes; les falta relieve de piedra/hierro y aviso más nítido. | Alta |
| Pino (aldeano niño-seta) | `dibujar_aldeanos.py` | **Mejorable** | Sombrero y cuerpo demasiado lisos/plásticos al lado de `casa_seta.png`; le faltan láminas bajo el sombrero y matiz en la ropa. | Media |
| Animaciones de Maisha | `dibujar_maisha.py` | **Mejorable** | En `andar` y `correr`, el paso de perfil y el destello del corazón/brote pueden ganar suavidad y lectura a 640×360. | Media |

### 2.2 Ilustraciones de la historia (`revision/ilustraciones`)

| Elemento | Archivo / Generador | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Aro del velo en recuerdos nocturnos | `cinematicas.py` (`velo_recuerdo`, `3_leyenda`, `recuerdo_1..3`) | **Mal** | El borde de niebla y el halo de `3_leyenda` dejan un anillo granulado y escalonado que se nota en fondos oscuros. | Alta |
| Castores y molino (`2_familia_shamba`, `3_leyenda`, `4_giza`, `12_eco_puente`) | `cinematicas.py`, `cinematicas_sendero.py` | **Mal** | Los castores parecen óvalos de plástico 3D sin pelo ni expresión; en `2_familia_shamba` la rueda del molino flota sin canal ni agua. | Alta |
| Sierra repetida en `17_kimya_lago` | `cinematicas_sendero.py` | **Mal** | El horizonte del lago repite el mismo diente de sierra más de 25 veces seguidas mecánicamente. | Alta |
| Ilustraciones 20, 21 y 22 (`20_eco_cueva`, `21_eco_lago`, `22_ruinas_mauti`) | `cinematicas_sendero.py` | **Mejorable** | En `22_ruinas_mauti` el Primer Árbol es un trapezoide gris plano con dos rayas rectas; a `20` y `21` les falta profundidad de primer plano y brillos de esporas/reflejo. | Media |

### 2.3 Luz 2.5D (`revision/luz-2.5d`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Mapas de normales de aldeanos y criaturas | `herramientas/relieve.py` | **Mal** | `arte/personajes/aldeanos/` y `arte/zonas/raiz/` no tienen `_n.png`; no reciben la luz de faroles ni del atardecer. | Alta |
| Sombras de personajes (`sombra.gd`) | `scripts/personajes/sombra.gd` | **Mejorable** | Es una elipse estática idéntica a mediodía, al atardecer y de noche; no se alarga ni desplaza con la inclinación del sol. | Alta |
| Color de ambiente por zona y hora | `scripts/mundo/relieve.gd` | **Mejorable** | Todas las regiones exteriores usan exactamente el mismo tinte `DIA`/`TARDE`/`NOCHE`, sin carácter propio por bioma (ciénaga más verdosa, bosque/campo más cálidos, montaña nevada más azulada). | Media |
| Luces nocturnas faltantes (`casa_shamba`, `almacen`, `cubierta`) | `scripts/mundo/relieve.gd` | **Mejorable** | La casa de Shamba, el almacén del Embarcadero y el farol de la cubierta del transbordador no están en la tabla `LUCES`. | Media |
| Polvo en rayos de sol y reflejos en el agua | `luz_sol.gd`, `ambiente.gd` | **Mejorable** | A los rayos de sol les faltan motas de polvo flotando dentro del haz; los destellos del agua son de 1 px sin ondulación. | Media |

### 2.4 Música (`revision/musica`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Desequilibrio de volumen entre pistas | `sonido.gd`, `componer_musica.py` | **Mal** | Diferencia de hasta 6,2 dB entre pistas (`ruinas.ogg` a -13,4 dB frente a `kitovu.ogg` a -19,6 dB; `jefe_mamba` a -14,4 dB frente a `jefe_kuvu` a -18,1 dB). | Alta |
| Timbre y envolventes del sintetizador | `sintetizador.py` | **Mejorable** | El piano y la flauta tienen armónicos fijos y reverb de 4 ecos discretos algo metálicos; agradecerían micro-humanización determinista, más cuerpo cálido y difusión suave. | Media |
| Costura de bucle en pistas musicales | `sintetizador.py` | **Mejorable** | `guardar_ogg` aplica un fundido de salida al final pero no mezcla la cola de resonancia con el principio para un bucle continuo sin caída. | Media |

### 2.5 Sonidos (`revision/sonidos`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Pasos de Maisha según el terreno | `crear_sonidos.py`, `maisha.gd`, `sonido.gd` | **Mejorable** | Al caminar o correr no suenan pasos suaves adaptados al terreno (hierba, madera, piedra/nieve). | Alta |
| Nivelación y cuerpo de efectos de combate | `crear_sonidos.py`, `sonido.gd` | **Mejorable** | Algunos impactos y avisos suenan secos o dispares en volumen; falta revisar que ningún efecto tenga clic al inicio/final. | Media |

### 2.6 Interfaz (`revision/interfaz`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Atajo de teclado para el 6.º bolsillo (Bestiario) | `mochila.gd`, `LEEME.md` | **Mal** | `LEEME.md` dice «Teclas 1 a 6: abren la mochila directamente en esa pestaña», pero `ATAJOS` en `mochila.gd` solo define `KEY_1` a `KEY_5` (falta `KEY_6: 5` y en `escena_mundo.gd` falta abrir la pestaña 5 con el 6). | Alta |
| Navegación y legibilidad en Diario / Tienda / Pausa | `mochila.gd`, `tienda_tawi.gd`, `menu_pausa.gd` | **Mejorable** | En la rueda rápida y en las pestañas conviene asegurar que los textos largos nunca pisen el marco dorado y que los avisos tengan siempre refuerzo visual y sonoro. | Media |

### 2.7 Código (`revision/codigo`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Textura radial de luz duplicada en 8 scripts | `relieve.gd`, `oscuridad.gd`, `cueva_setas.gd`, `brasero.gd`, `farolillo.gd`, `casa_shamba.gd`, `seta_luz.gd`, `rescoldo.gd` | **Mal** | Cada archivo construye su propio `Gradient` + `GradientTexture2D` radial casi idéntico desde cero. | Alta |
| Código muerto o repetido en enemigos y mundo | `scripts/enemigos/`, `scripts/mundo/` | **Mejorable** | Funciones y constantes repetidas que pueden limpiarse manteniendo el estilo en español con `##` y tabuladores. | Media |

### 2.8 Rendimiento (`revision/rendimiento`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Creación de `GradientTexture2D` en cada `Relieve.destello()` | `scripts/mundo/relieve.gd` | **Mal** | Cada fogonazo de golpe, semilla o Latido instancia una textura de 96×96 desde cero en vez de usar una textura estática en caché. | Alta |
| Redibujado y búsqueda por grupos cada fotograma en `aldeano.gd` | `scripts/mundo/aldea/aldeano.gd` | **Mal** | Llama a `queue_redraw()` en cada `_process` y evalúa `CHARLA.tiene_novedad(id)` + `get_first_node_in_group("maisha")` 60 veces por segundo por cada aldeano. | Alta |
| Asignación de arrays con `.filter()` y nubes fuera de cámara en `ambiente.gd` | `scripts/mundo/ambiente.gd` | **Mejorable** | Crea 5 arrays nuevos por fotograma con `.filter()` y dibuja los polígonos de todas las nubes aunque estén lejos de la vista. | Media |
| Evaluación repetida de `CHARLA.tiene_novedad()` y búsqueda de nodos en `aldeano.gd` y `luz_sol.gd` | `aldeano.gd`, `luz_sol.gd`, `espejo_lago.gd` | **Mal** | `aldeano.gd` evalúa todas las condiciones de conversación (`CHARLA.tiene_novedad`) y busca a Maisha por grupo en cada fotograma de `_draw()`; `luz_sol.gd` busca a Maisha y al gestor de corrupción en cada fotograma incluso de noche cuando los rayos están apagados. | Alta |

### 2.9 Textos y diálogos (`revision/textos`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Lenguaje con género para Maisha y Mauti | `datos/dialogos/raiz.json`, `casa_shamba.gd` | **Mal** | En `embarcadero_darsena_sola`: *"No. Sola no."* (femenino para Maisha). En `primer_arbol_final`: *"Debajo hay una luz lila, cansada pero entera"* y en `LEEME` / diálogos referencias con género; en `casa_shamba.gd`: *"Duerme, pequeño brote"* (cambiado a *brotecito* en Bibi pero olvidado aquí). | Alta |
| Frases robóticas o de manual en diálogos antiguos | `datos/dialogos/kitovu.json`, `datos/dialogos/raiz.json` | **Mejorable** | Algunos pensamientos de objetos y avisos del narrador o aldeanos aún suenan secos o esquemáticos; se pueden hacer más cálidos y naturales sin cambiar lo que pasa ni las marcas. | Media |

### 2.10 Estabilidad y guardado (`revision/estabilidad`)

| Elemento | Archivo | Estado | Qué le pasa | Prioridad |
| --- | --- | --- | --- | --- |
| Error `Invalid access to property 'scale' on Nil` en `aldeano.gd` | `scripts/mundo/aldea/aldeano.gd` | **Mal** | Cuando un aldeano no cumple `requiere` y hace `queue_free()` en `_ready()`, `_process` se ejecuta en ese primer fotograma y falla porque `_sprite` es `null`. | Muy alta |
| Error `Lambda capture at index 0 was freed` en cámara lenta | `scripts/mundo/kitovu/kitovu.gd`, `scripts/interfaz/leccion.gd` | **Mal** | La lambda pasada a `Leccion.camara_lenta()` captura el nodo `semilla`; cuando la semilla estalla y hace `queue_free()`, Godot lanza error de ejecución al evaluar la lambda con una captura liberada. | Muy alta |
| Blindaje total de efectos que frenan o empujan a Maisha | `scripts/personajes/maisha.gd`, `impacto.gd` | **Mejorable** | Garantizar que cualquier efecto temporal (`lentitud`, `mareo`, `viento`, `hundirse`, `escarcha`, `camara_lenta`) tenga caducidad de seguridad y se limpie por completo en `revivir()` y al cambiar de escena. | Alta |
