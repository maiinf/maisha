# Maisha — proyecto base

Proyecto de Godot 4 para PC (se desarrolla en Mac) (resolución base 640×360, píxeles nítidos, teclado y mando).
La guía para instalarlo todo está en [`documentacion/guia_instalacion.md`](documentacion/guia_instalacion.md).

## Estructura de carpetas

| Carpeta | Qué va dentro |
| --- | --- |
| `arte/` | **Imágenes que usa el juego** (PNG exportados). Nunca se editan aquí directamente. |
| `arte/personajes/maisha/` | Animaciones de Maisha y sus capas de evolución |
| `arte/personajes/aldeanos/` | Aldeanos |
| `arte/enemigos/`, `arte/jefes/` | Enemigos y jefes |
| `arte/mundos/raiz/suelos/` | Tilesets del suelo de Raíz (hierba, camino, agua…) |
| `arte/mundos/raiz/objetos/` | Árboles, rocas, ruinas, matorrales… |
| `arte/mundos/raiz/aldea/` | Cuna de Musgo: el Gran Árbol, las casas (en ruinas y reconstruidas), farolillos, estatuas, el interior del Claro de Calma |
| `arte/retratos/` | Retratos de los diálogos |
| `arte/efectos/` | Explosiones, hojas, partículas |
| `arte/interfaz/` | Marcos, iconos, barras |
| `arte/paletas/` | Paletas oficiales (`raiz.gpl` para Pixelorama) |
| `originales/` | **Archivos editables de Pixelorama** (`.pixelorama`), con las mismas subcarpetas que `arte/` |
| `audio/musica/`, `audio/sonidos/`, `audio/ambiente/` | Música, efectos de sonido y ambientes (todo creado por nosotros: ver «Música y sonido») |
| `fuentes/` | Tipografías (solo con licencia libre OFL). Ahora: Pixelify Sans, con su licencia al lado |
| `escenas/` | Escenas de Godot (`.tscn`): mundo, combate, interfaz, personajes |
| `shaders/` | Efectos de dibujo por código (p. ej. la corrupción gris del suelo) |
| `scripts/` | Código (`.gd`), organizado como `escenas/` |
| `datos/` | Diálogos, mapas, ropa… en archivos de datos (se editan sin tocar código) |
| `documentacion/` | Guías y notas del proyecto |
| `pruebas/` | Pruebas automáticas |

## Cómo nombrar los archivos

- **Minúsculas, sin tildes, sin «ñ», sin espacios.** Separa con guion bajo: `maisha_andar_abajo.png`.
- **Orden:** `quien_que_direccion`. Ejemplos:
  - `maisha_reposo_abajo.png`, `maisha_andar_lado.png`, `maisha_latido.png`
  - `bibi_retrato_contenta.png`
  - `raiz_suelo_hierba.png`, `raiz_arbol_cobre.png`
- **Direcciones:** `abajo`, `arriba`, `lado` (el otro lado se obtiene reflejando el dibujo).
- El original editable se llama igual, con extensión `.pixelorama`, y va en `originales/`.

## Cómo exportar una animación desde Pixelorama

1. Cada animación es un archivo con todos sus fotogramas (ej.: andar hacia abajo = 4 fotogramas de 24×32).
2. **Archivo → Exportar → Hoja de sprites (spritesheet)**, en **una sola fila horizontal**.
3. Guarda el PNG en la carpeta de `arte/` que le toque, con el nombre correcto.
4. Godot lo detecta solo.

## Animaciones de Maisha (ya montadas)

| Animación | Fotogramas | Velocidad | Archivo |
| --- | --- | --- | --- |
| Reposo (abajo, arriba, lado) | 4 | ciclo de 1,25 s (respira, el brote se mece, el corazón late) | `maisha_reposo_<dirección>.png` |
| Andar (abajo, arriba, lado) | 4 | 8 por segundo (pisa, paso, pisa, paso) | `maisha_andar_<dirección>.png` |
| Correr (abajo, arriba, lado) | 4 | 12 por segundo, con un instante en el aire | `maisha_correr_<dirección>.png` |
| Sorpresa (abajo) | 4 | ojos muy abiertos, saltito y el brote de punta | `maisha_sorpresa_abajo.png` |
| Daño (abajo, arriba, lado) | 2 | ojos cerrados de dolor (`> <`) | `maisha_danio_<dirección>.png` |
| Celebrar (abajo) | 4 | brazos (y cetro) en alto, ojos de alegría y saltitos | `maisha_celebrar_abajo.png` |
| Despertar (abajo) | 4 | sentada y dormida, abre los ojos, se levanta y se despereza | `maisha_despertar_abajo.png` |

- **Cuándo salen**: corre con **C** (o LB en el mando), pero no mientras sigue entumecida al despertar. Se sorprende al ver la chispa y cuando Shamba abre la puerta; pone cara de dolor al recibir daño; celebra con cada fanfarria (tarea, objeto, mancha limpia, victoria); y la partida empieza con ella sentada en el cráter.
- En un diálogo, una línea puede llevar la cara al principio: `[sonrisa] ¡Gracias!`. Si habla alguien con retrato, se usa `arte/retratos/<id>_<cara>.png`; si es un pensamiento de Maisha, pone esa expresión (`[sorpresa]`, `[celebrar]`, `[danio]`).
- **Retratos de Mzee Shamba**: normal, `sonrisa`, `sorpresa`, `triste` y `pensativo` (los dibuja `retrato_shamba()` en `dibujar_kitovu.py`). Sus diálogos ya los usan.

- Están en `arte/personajes/maisha/`, cada una como una fila de fotogramas de 24×32.
- `maisha_animaciones.tres` las reúne todas para Godot (nodo **AnimatedSprite2D** de `escenas/personajes/maisha.tscn`).
- Las dibuja `herramientas/dibujar_maisha.py`, que monta a Maisha por piezas (brote, cabeza, cuerpo, brazos, piernas).
  Si retocas un PNG a mano en Pixelorama, **no vuelvas a ejecutar ese programa**, o sobrescribirá tu retoque.

## Pantalla de inicio, guardado y pausa (lo que se abre al pulsar ⌘ + B)

El juego empieza en la **pantalla de inicio** (`escenas/interfaz/inicio.tscn`): el **diario de Maisha**, cerrado, sobre una mesa de madera de noche, a la luz de una vela (la llama tiembla, hay motas de polvo en la luz). El título y el menú están en una tarjeta de papel sujeta con cinta. Al elegir **Continuar** o **Nueva partida**, la tarjeta se va y el diario **se abre** (como la mochila); en una partida nueva, la introducción se **escribe a pluma** en la primera página («Lo primero que recuerdo»), con el rasgueo de la pluma, mientras en la otra página brota una semilla dibujada a tinta.

| Opción | Qué hace |
| --- | --- |
| Continuar | Solo aparece si hay una partida guardada. Dice dónde estabas y cuánto has jugado, y te lleva justo a ese sitio |
| Nueva partida | Si ya hay una partida, pregunta antes de borrarla. Después, una introducción muy corta y Maisha despierta en el Kitovu |
| Pantalla completa | Cambia entre ventana y pantalla completa |
| Salir | Cierra el juego |

- **La partida se guarda sola**: al llegar a cada sitio y cada vez que pasa algo importante (recoger algo, rescatar a alguien, reconstruir una casa…). Abajo a la derecha sale «Guardado». Si Maisha está en plena pelea, se guarda el último sitio seguro.
- El archivo está en `~/Library/Application Support/Godot/app_userdata/Maisha/partida.json` (en el Finder: menú Ir → Ir a la carpeta…). Las pruebas automáticas usan otro archivo y no lo tocan.
- **Pausa** con Esc (o Start en el mando): Seguir, Pantalla completa, Volver al inicio y Salir del juego. También enseña dónde estás, el tiempo jugado, lo que llevas y tus mejoras.
- Para probar una escena suelta sin pasar por el inicio: ábrela en Godot y pulsa `⌘ + R`.
- La mesa (vela, tintero y pluma, hoja prensada, semillas y la esquina de un mapa) la pinta `herramientas/pintar_inicio_mesa.py` (`arte/interfaz/inicio_mesa.png`); el título y la hojita del menú, `herramientas/dibujar_inicio.py`. El diario es el de la mochila (`arte/interfaz/diario/`).

## El Kitovu: el comienzo del juego

Escena `escenas/mundo/kitovu.tscn`: el centro del mundo, gris y roto. Solo la granja de **Mzee Shamba** (castor anciano y agricultor) conserva el color.

1. **Un comienzo pausado.** Maisha despierta sentada en un cráter **sin nada** y muy despacio: le pesa el cuerpo y durante unos 15 segundos anda más lenta (`lentitud` en `maisha.gd`), mientras amanece poco a poco. Sus pensamientos salen en una caja de puntos con una nubecita.
   - Aparece la **chispa de vida**, una lucecita que la guía por tres sitios del valle, siempre por los caminos y rodeando la granja por el este (`RUTAS_CHISPA` en `kitovu.gd`), para no pasar por encima de las manchas dormidas. En cada uno Maisha recuerda algo, con su ilustración: la aldea de noche, los ojos de Giza y una estrella que cae. Su brote brilla un poco más con cada recuerdo. Luego la chispa se mete en la casa de la granja.
   - La puerta está **cerrada**: si Maisha llama, nadie abre. Cerca se oye cacarear a **Kuku**, una gallina perdida que **se escapa** si Maisha corre hacia ella; tras unas cuantas huidas se cansa y se deja coger. Maisha la lleva en brazos hasta la puerta, Mzee Shamba sale a por ella y la invita a entrar.
- **El valle** (64×46 casillas): al suroeste el cráter; en el centro la **granja**, lo único con color (una casa grande de troncos con tejado de paja, chimenea, porche y una **rueda de molino** que gira con la acequia del estanque), el huerto, un **campo de trigo** que se mece y tres **gallinas** que picotean y se apartan si Maisha se acerca. Al noroeste, la **aldea antigua en ruinas** (casas caídas, un pozo seco, faroles apagados, un carro volcado); al norte, la **torre de la campana** y el **monumento de la leyenda** entre **raíces gigantes** secas; al noreste, el Arco de Raíz.
- Las ruinas, el pozo, la torre, el monumento, el carro y las raíces **se pueden mirar** (Acción): Maisha piensa algo distinto antes y después de conocer la historia.

2. **La noche en la granja.** Dentro, el brote de Maisha brilla y el castor lo nota (se le escapa un susurro). Esa noche **no hay tareas**: cenan sopa, la casa se queda a oscuras junto al fuego, suena «Noche en la granja», Shamba susurra «Duerme, pequeño brote» y unos textos en negro cuentan la noche. **Amanece** (fanfarria «Amanece») y por la mañana Shamba le pide ayuda.
3. **Tres tareas**: arrancar 5 zanahorias, **pescar** un pez en el estanque (pulsar Acción cuando la marca está en lo verde) y arreglar la cerca con las tablas del tronco caído.
4. Al terminarlas, Mzee Shamba **cuenta la historia del mundo con 6 ilustraciones** (como un libro: la imagen arriba y el texto debajo): el Kitovu verde de antes, su familia de castores, la leyenda del brote de luz, la llegada de Giza, la gente convertida en piedra y él esperando solo. Después le da el **Cetro de Raíz** de su familia y un **mapa del mundo partido** (falta el trozo del norte: dice que está en Sigilia), y le advierte de Giza.
5. **Manchas de Giza**: por el valle hay 6 sitios posibles y en cada partida nueva salen **3 al azar**, cada una con una de sus 3 formas. El **narrador** (banda arriba; el juego se para mientras habla) enseña algo en cada una: en la 1.ª el golpe y las semillas, en la 2.ª el Latido y el Aliento, y la 3.ª ya «a solas». Son pequeñas: su Corazón se rompe con 2 semillas.
6. Limpias las tres, la tierra tiembla y despierta **Mzizi, la raíz del Arco** (el miniboss), en su arena delante del Arco:
   - Se esconde, **avisa en un agujero** (se agrieta y brilla), sale, **escupe piedras** (abre la boca justo antes) y vuelve a meterse.
   - Solo le hacen daño las **semillas**: pon una junto al agujero que avisa y le estallará al salir. Tiene 6 de vida y una barra arriba con su nombre. **Cada semilla que le alcance cuenta**: si estallan varias a la vez o una detrás de otra, le quitan varios trozos (mientras asome del agujero, cada estallido la deja fuera un poco más, retorciéndose) (pero gastarlas todas de golpe deja a Maisha sin Aliento).
   - Con la mitad de vida avisa más rápido, escupe en abanico y llama a Petrinos.
   - El cetro rebota en su piedra, pero **rompe las piedras** que escupe.
   - Al vencerla, la piedra se cae a trozos, debajo aparece madera viva, se hunde y el **Arco se abre** hacia los **Prados del Eco**. El narrador lo cuenta con dos cinemáticas (`7_mzizi_madera` y `8_arco_despierta`); cuando hay una ilustración, su texto sale en la caja de abajo. Por el arco del claro de columnas se puede volver.

- Sin cetro, las manchas están dormidas y Maisha no se atreve a acercarse; la arena de Mzizi no despierta hasta limpiar las tres manchas.
- Los sitios de las manchas y la arena están en `datos/mapas/kitovu.txt` (números 1-6 y 7) y `kitovu.zonas` (`practica` y `jefe:mzizi`).
- Los textos están en `datos/dialogos/kitovu.json` (estilos: normal, pensamiento y narrador).
- **La casa de Mzee Shamba** (por fuera, la rueda del molino, por dentro y el cetro de la pared) está pintada con el mismo pintor que las cinemáticas: troncos con corteza y cortes con anillos, paja a capas con musgo, ventanas con reflejo y cortinas, chimenea de piedra con la olla al fuego, alfombra trenzada, mesa con la cena, colcha de retales, tarros de semillas, el retrato de la familia y la luz del fuego y de la ventana. Las mismas medidas de antes (puertas, choques y muebles no cambian). Para repintarla: `python3 herramientas/pintar_casa_shamba.py`.
- **El suelo del Kitovu** también está pintado (`herramientas/pintar_suelo.py kitovu`; `construir_mapa.py kitovu` lo llama solo): hierba con manchas, briznas y matas, flores en las casillas «,», caminos de tierra con piedrecitas y la hierba comiéndose los bordes, agua clara en la orilla y honda en el centro con ondas y brillos, losas con volumen y puentes de tablas. Los Prados del Eco y Cuna de Musgo usan ya el mismo suelo pintado (`MAPAS_PINTADOS` en `construir_mapa.py`).
- **Los objetos de la granja** (`herramientas/pintar_granja.py`): la cerca, el tronco con tablas, el trigo y los árboles secos están pintados; la zanahoria, el espantapájaros y las gallinas, dibujados píxel a píxel (a ese tamaño se leen mejor). Mismas medidas y fotogramas que antes.
- **Las ruinas del Kitovu** (`herramientas/pintar_ruinas.py`): casas en ruinas, pozo seco, torre de la campana con su campana muda, monumento de la leyenda, raíces gigantes secas, el Arco de Raíz (dormido y abierto) y el cráter, pintados; el farol apagado, píxel a píxel.
- El resto del arte lo dibuja `herramientas/dibujar_kitovu.py` ( huerto, trigo, gallinas, cerca, tronco, espantapájaros, árboles secos, ruinas, pozo, torre, monumento, raíces, carro, faroles, el arco, el interior, Mzee Shamba y su retrato, los iconos y el mapa del mundo).
- **Cinemáticas (ilustraciones de la historia)**: `arte/historia/`, como las de los legendarios en Pokémon Platino: mucho más detalladas que el juego, a tamaño de pantalla (**600×256**, sin ampliar) y con su propia **paleta de cinemáticas** (177 colores: todos los de Raíz, sus tonos intermedios y rampas de cielo, noche, fuego y luz de Giza). Las pinta `herramientas/cinematicas.py` con el pintor `herramientas/pintor.py` (volumen, pelo, humo, fuego, luz y niebla). Para repintarlas: `python3 herramientas/cinematicas.py` (todas, tarda unos 4 minutos; necesita `pip3 install numpy scipy opencv-python`) o `python3 herramientas/cinematicas.py 4_giza` (solo una). En los diálogos se usan con `"historia": [{"imagen": "1_kitovu_antes", "lineas": [...]}, ...]` y `"tras_historia"`. Si quieres cambiar una por un dibujo tuyo, guárdalo con el mismo nombre y tamaño (las de 208×120 de antes también funcionan: se ven al doble).

  | Cinemática | Qué se ve |
  | --- | --- |
  | `1_kitovu_antes` | El valle verde una mañana dorada: campos, río, aldea, el árbol viejo donde se cruzan las raíces de luz y, en las montañas, los arcos hacia las otras tierras |
  | `2_familia_shamba` | La granja en color: la casa con su rueda de molino y la familia trabajando (azada, cesta de zanahorias, regadera; la abuela mira desde la puerta) |
  | `3_leyenda` | De noche junto a la chimenea: la abuela en su mecedora alza el Cetro de Raíz y dos crías (una es el pequeño Shamba) ven la leyenda en una luz dorada |
  | `4_giza` | Giza, una montaña de humo con ojos, estira brazos de sombra sobre el valle y todo lo que toca se queda gris; la familia lo mira desde una loma |
  | `5_piedra` | La plaza gris: vecinos convertidos en estatuas agrietadas, raíces secas y el Arco cerrado por espinas |
  | `6_hoy` | Anochece: solo la granja conserva el color y Mzee Shamba espera con su farol |
  | `7_mzizi_madera` | Al vencer a Mzizi, plano desde abajo: la gran raíz se alza en S, la piedra de abajo revienta y arriba ya es madera viva; su cabeza tiene una corona de placas de corteza y ojos de grieta que ya brillan ámbar. El sol rompe las nubes y Maisha alza el cetro |
  | `8_arco_despierta` | La vida dorada sube por las raíces del Arco y dentro se ven los Prados del Eco; Maisha, de espaldas, lo mira |
  | `recuerdo_1` a `recuerdo_3` | Los recuerdos de Maisha, con un borde de niebla: la fiesta junto al fuego, los ojos de Giza en la oscuridad y la luz que cae del cielo |
- **Retratos**: si existe `arte/retratos/<id>.png` (64×64), sale junto a la caja de diálogo y en la mochila (ahora solo lo tiene Mzee Shamba).

### Las lecciones (el mundo se para hasta que pulsas)

Como en otros juegos, el Kitovu enseña las acciones parando el mundo (`scripts/interfaz/leccion.gd`): la pantalla se oscurece salvo un círculo de luz sobre Maisha y aquello sobre lo que hay que actuar, aparece una tecla grande que late y un texto, y nada sigue hasta que se pulsa. Cada lección sale una sola vez (marcas `leccion/...`).
- **El cetro (J)**: la primera vez que Maisha llega junto al espantapájaros con el cetro. Al pulsar, golpea.
- **Las semillas (K)**: en la primera mancha, después de que el narrador presente el Corazón de Giza. Al pulsar, Maisha planta la semilla y el tiempo va **a cámara lenta** con «¡Sal de la cruz!» hasta que sale de la cruz (o estalla).
- **El Latido (L)**: en la segunda mancha, la primera vez que un Petrino se le echa encima.
- En las pruebas, `pruebas/ayudante_lecciones.gd` pulsa la tecla que pide cada lección.

## La mochila (Tab, I o Select)

El diario tiene estilo **noche mágica** (`herramientas/pintar_interfaz.py`): tapas de cuero azul noche cosidas con hilo de oro y cantoneras doradas, páginas de cielo nocturno (nebulosa suave, estrellas, constelaciones) con borde de filigrana dorada, y la tapa con el Gran Árbol, la luna y estrellas en oro. Las letras de las páginas usan su propia paleta clara (`TN_*` en `mochila.gd`): títulos en oro, texto en crema, la historia en coral y lo cumplido en gris azulado; la fila elegida, en tinta oscura sobre la banda dorada. El mapa sigue siendo de pergamino.

**El árbol de habilidades** (pestaña Habilidades del diario): un árbol dorado que crece del lomo del libro
(`arbol_ramas.png` y `nodos.png`, en `pintar_interfaz.py`) con tres ramas: **Raíz** (Semilla, K) a la izquierda,
**Cetro** (golpe, J) hacia arriba y **Aliento** (Latido, L) a la derecha; Runa y Tierra asoman dormidas a los lados.
Cada rama tiene en su base la habilidad básica y encima 6 nodos (los niveles de `datos/artes.json`). Los nodos 3 y 6
son **grandes** (corona de cuatro puntas) y, además de Esencia, piden **Cristales del Nexo** (2 y 4). ← → cambian de
rama (en los bordes, de pestaña), ↑ ↓ suben y bajan por ella, y **manteniendo Acción** sobre el siguiente nodo se
despierta, en cualquier momento (meditar en el Claro de Calma sigue curando y guardando, y su árbol también deja
subir). Rama Cetro: alcance +4, barrido más ancho, golpe 2 (grande), golpes más seguidos, más Aliento por golpe,
golpe 3 y más alcance (grande). Los Cristales gastados se cuentan a partir de los niveles (`Artes.cristales_gastados`).

Es el **diario de cuero de Maisha**: un libro con tapas cosidas y cantoneras de latón, páginas de pergamino y una cinta de marcapáginas por pestaña. El juego se para mientras está abierto.
- **Al abrirlo**, el libro sube desde abajo cerrado (se ve la tapa con el Gran Árbol grabado), la tapa gira hacia el lomo y aparecen las páginas; luego se escribe la tinta. **Al cambiar de pestaña** se pasa una hoja (con su sonido de papel). Lo elegido se marca con un **subrayado amarillo** que se desliza y una cinta roja; la historia lleva un **sello de lacre**; lo cumplido se tacha.
- El **mapa** se ve pegado sobre las dos páginas.
- Arte: `herramientas/pintar_interfaz.py` → `arte/interfaz/diario/` (libro, tapa, cintas, sello y las cajas que se estiran: pergamino, papel, cuero y noche). Las cajas y los colores de tinta están en `scripts/interfaz/piel.gd`, que usa toda la interfaz.
- Cada pestaña tiene su icono (`arte/interfaz/pestanas.png`, lo dibuja `herramientas/dibujar_pestanas.py`).

**Toda la interfaz va a juego con el diario:** los diálogos se escriben en pergamino con borde de cuero (el nombre, en una etiqueta de cuero; el retrato, en un marco de cuero), los pensamientos en un papel suelto rasgado, el narrador en un panel de noche con filigrana dorada, las ilustraciones con marco de cuero; la pausa y la tienda de Tawi, en pergamino; la vida, el objetivo, los avisos y la barra de los jefes, en etiquetas de cuero. Sonidos nuevos: `libro_abrir`, `libro_cerrar` y `pagina`.

| Pestaña | Tecla | Qué hay |
| --- | --- | --- |
| Misiones | 1 | El diario: lo que está en marcha (historia, encargos, secretos) y lo cumplido, con sus pasos. **Acción** elige qué misión se sigue en pantalla |
| Objetos | 2 | Lo que lleva Maisha con su descripción, y los objetos clave (el cetro, los mapas). Con **Acción** sobre la sopa, se la toma |
| Habilidades | 3 | Golpe, semilla y Latido, las mejoras conseguidas y las **Artes** del Árbol de la Vida con su nivel |
| Mapa | 4 o M | El **mapa de Raíz** (con niebla: ver abajo) y el mapa del mundo de Mzee Shamba (↑ ↓ cambian de uno a otro), con un alfiler donde está Maisha |
| Lazos | 5 | Los personajes que conoce |

← → cambian de pestaña, ↑ ↓ eligen. Los objetos se describen en `scripts/globales/estado.gd` (`OBJETOS`).

### Acciones rápidas

- **Teclas 1 a 5** (y **M** para el mapa): abren la mochila directamente en esa pestaña. Si ya está abierta en esa pestaña, la cierran.
- **Rueda rápida**: mantén pulsado **Tab** (o **Select** en el mando) y aparece una rueda con las 5 pestañas sobre el juego parado. Inclina hacia una (WASD, flechas o el stick) y suelta: se abre esa pestaña. Si sueltas sin elegir, se cierra. Pulsar Tab sin mantener abre la mochila como siempre.

## Misiones y objetivo en pantalla

Las misiones están en `datos/misiones.json` y **se leen solas a partir de las marcas de la partida**: no guardan nada aparte (solo cuál se sigue). El autoload **Misiones** (`scripts/globales/misiones.gd`) lo calcula todo.

- **Arriba a la derecha** se ve la misión que se sigue y lo que hay que hacer ahora (con contadores: «Arranca zanahorias del huerto (3/5)»). Se esconde al hablar, en plena pelea y con la mochila abierta. Se puede quitar en la pausa («Objetivo en pantalla»).
- **Una flechita** señala adónde ir: encima del sitio si se ve, o en el borde de la pantalla si no. Si el sitio está en otra escena, señala la puerta por la que se va hacia allí (los caminos entre escenas están en el mismo JSON, en `caminos`).
- Avisos de **Misión nueva** y **Misión cumplida** (cada uno con su sonido) y un destello al cumplir cada paso.
- Una misión de historia nueva pasa a ser la que se sigue; los encargos se pueden elegir en el diario (Acción).
- Para añadir una misión: copia una del JSON. Cada paso se cumple con `hecho` (marcas), `objeto` (llevar algo) o `cuenta` (marcas que empiezan por un prefijo); `ir` dice adónde apunta la flecha (`aldeano:<id>`, `grupo:<grupo>`, `puerta:<escena>`, `edificio:<id>`, `casilla:x,y`). Las instrucciones están dentro del propio JSON (`_ayuda`).

Misiones que ya hay: Un despertar extraño, La granja de Mzee Shamba, Las manchas de Giza, Ecos en los prados, Cuna de Musgo, El Árbol de la Vida, El Bosque Cobrizo, La Ciénaga Quieta, El Campo Segado (historia) · La casa-seta de Pino, La forja de Corteza, El puesto de Tawi, La cocina de Juncia, El diario de Msafiri, Las nasas de Korongo, Las campanillas de Fuko, Las mazorcas de Sungura (encargos) · Los ecos perdidos · Los secretos de los prados (secreto).

## El Árbol de la Vida (habilidades)

Así mejora Maisha (el GDD ya lo tenía pensado: reparto libre de Esencia, sin niveles de personaje). El autoload **Artes** (`scripts/globales/artes.gd`) y los datos en `datos/artes.json`.

1. **La Esencia se gana sola**: cada mancha del Kitovu 1, Mzizi 3, cada zona de una región 1, Pembe 4, Konokono 4, la Cosechadora 5, cada secreto 1 y cada casa que se levanta en la aldea 1. Sale un aviso arriba a la izquierda («+1 Esencia · Zona purgada»). No se guarda aparte: se cuenta a partir de las marcas.
2. **Se gasta meditando**: Bibi enseña a meditar (después de conocerla, la siguiente vez que se habla con ella). En el Claro de Calma, junto al brote, Acción → Maisha medita: **recupera la Vida y el Aliento**, se guarda la partida y se abre el **Árbol de la Vida**.
3. En el árbol: ← → eligen el Arte, ↑ ↓ miran sus niveles y **mantener Acción** despierta el siguiente nivel (para no gastar Esencia sin querer). Subir al nivel N cuesta N de Esencia.

| Arte | Niveles (1 → 6) |
| --- | --- |
| **Raíz** (la Semilla) | Semilla ligera (cuesta 22) · Raíces largas · **Brote en la cabeza** (cruz +1 casilla) · Semilla ligera II (19) · Mecha corta (1,2 s) · **Hojas y flores** (cruz +1) |
| **Aliento** (Vida, Aliento, Latido) | Pulmón de brisa (110) · Respirar hondo (+15 %) · **Aura suave** (+1 hoja de Vida) · Latido amplio · Golpe que respira · **Cuerpo de brisa** (+1 hoja, 125) |
| Runa · Tierra | Dormidas: despiertan en Sigilia y en Asterhaul |

- Los niveles en **negrita** cambian a Maisha por fuera (`scripts/personajes/rasgos_maisha.gd`): una tercera hoja con un capullo en el brote, florecillas, un aura que respira, cuerpo casi transparente con estela.
- En todo Raíz se consiguen 43 de Esencia (y 2 más en las islas de la ciénaga, más adelante); antes del jefe final, unas 36. Llevar las dos Artes al máximo cuesta 42: durante el mundo hay que elegir, y al vencer a la Cosechadora se llega casi a todo. Las Artes de Runa y Tierra despiertan en otros mundos.
- Para cambiar números o añadir niveles: `datos/artes.json` (dentro explica cada efecto).

## El Arco de Raíz (rediseñado)

`herramientas/pintar_portal.py` pinta el Arco (`arte/mundos/kitovu/portal.png`, 2 × 96×120): un umbral de losas antiguas con un círculo de runas, **dos pilares de piedra rotos y con musgo** por los que suben raíces enroscadas (por delante y por detrás de la piedra), un arco de raíces trenzadas y, arriba, en el nudo, **la Semilla del Arco**: ámbar cuando está abierto, violeta y agrietada cuando duerme. Dentro: los Prados con rayos de sol, o la oscuridad de Giza con espinas.
En el juego (`scripts/mundo/kitovu/portal.gd`), la semilla **late como un corazón**, las runas de los pilares se encienden por turnos, hay ondas de luz en el paso y motas que suben.

## Prados del Eco

Escena `escenas/mundo/prados_del_eco.tscn`: la primera región jugable de Raíz.

- Maisha llega por el **Arco de Raíz** al claro de columnas, en un prado apagado. Hay **3 zonas corruptas**: cada una que purgas recupera su color y aviva el resto; al purgar las tres, toda la región vuelve a tener color (y salen mariposas).
- **2 secretos**: uno tras un matorral (rómpelo con una semilla) y otro en un escondite de rocas que se abre al golpear las **3 piedras-eco** con el cetro.
- Junto a dos zonas hay **aldeanos convertidos en piedra** (Pino y Corteza): al purgar la zona, la estatua se rompe, el aldeano da las gracias y se va a la aldea.
- **Encargos:** 4 **setas luminosas** (brillan a la sombra de los árboles) y 3 **rocas con mineral** (el cetro rebota: se rompen con una semilla y dejan el mineral en el suelo). Se recogen al pasar por encima.
- Al este, por el **Sendero del Puente**, se llega a **Cuna de Musgo**. Al norte, el **Camino Cobrizo** sube al **Bosque Cobrizo** (cerrado con espinas de Giza hasta que Bibi habla del bosque).
- Ambiente: sombras de nubes, hojas que caen girando con su sombra en el suelo (secas y grises donde Giza ha pasado), polen que brilla al sol, ceniza que cae donde todo es gris, mariposas, destellos en el agua, rayos de sol en diagonal (cálidos con color, fríos en lo gris) y una viñeta suave (`scripts/mundo/luz_sol.gd`).
- **Decorado de la hierba** (`scripts/mundo/decorado.gd`): hierba alta que se mece en olas, flores amarillas/rojas/blancas, helechos, arbustos con bayas, tocones, setas, piedrecitas, trébol y ramas caídas. Se reparte solo, siempre igual (según la casilla), sobre la hierba (`.` y `,`), lejos de las zonas corruptas y sin tapar caminos ni agua. Se vuelve gris con Giza como el resto. Las piezas salen de `arte/mundos/raiz/objetos/decorado.png` (tira de 12 × 16 px), que genera `herramientas/dibujar_decorado.py`.
  - Para poner más o menos: en el nodo **Region**, cambia **Densidad decorado** (0 = nada, 0.3 por defecto). Sirve en cualquier región.
  - Los **puentes** (`=`) con agua (`~`) encima o debajo llevan barandillas de madera automáticamente.
- Probé a pintar los árboles y rocas con el pintor (`herramientas/pintar_prados.py`), pero quedaban peor que el pixel art a mano, así que siguen los de antes. El script se queda por si sirve más adelante.

## Raíz, mundo libre: los caminos

Raíz ya no es una fila de regiones: es un mundo libre con **Cuna de Musgo** en el centro y **caminos con nombre propio** entre los lugares (sección 43 del GDD). Hechos de momento: el **Sendero del Puente**, **Las Pasarelas**, el **Camino Cobrizo** y la **Senda de los Surcos**. Los demás caminos están en el mapa, bajo la niebla, y se irán construyendo.

### El mapa con niebla

El mapa de Raíz lo va dibujando Maisha al andar (`scripts/interfaz/mochila.gd`, dibujo de `herramientas/dibujar_mapa_raiz.py`, 420×220):
- Los **lugares** que aún no ha pisado están bajo una niebla de pergamino con un «?». Los **caminos** se trazan con tinta la primera vez que los pisa; los que no, siguen tapados.
- Abajo: en qué camino está y cuántos ha descubierto (de 9).
- El **mapa de Tawi** (lo da al arreglar su puesto) quita la niebla de todos los lugares, con su nombre; los caminos hay que andarlos.
- Las posiciones de lugares y caminos están en `LUGARES_RAIZ` y `CAMINOS_RAIZ` (mochila.gd) y en `LUGARES` (dibujar_mapa_raiz.py).

### Sendero del Puente

Escena `escenas/mundo/sendero_del_puente.tscn` (mapa de 140×46 casillas: unas 3,5 pantallas de largo), entre los Prados del Eco y Cuna de Musgo. Música propia: «El puente viejo».
- El **Río Lento** y el gran **puente de piedra de los antiguos**: tablero de sillares, pretiles (`|`, no se pueden cruzar) y fachada con arcos sobre el agua, todo pintado en el suelo (`-` tablero, `|` pretil).
- Bajo el puente, un **vado** de piedras (`'`) lleva a un islote con el primer **eco perdido** (`@`). Bayas en la orilla.
- **Msafiri** (`}`), un pangolín viajero y cronista, en su **campamento** (`{`, tienda de lona y una hoguera animada). Encargo: **tres páginas de su diario** (`` ` ``) que el viento llevó a las ruinas del norte, a la orilla bajo el puente y dentro de la zona corrupta. Al devolvérselas, cuenta lo de los ecos y regala el **Cuaderno de ecos**.
- Una **zona corrupta** junto al camino y, al norte, las **ruinas** de quienes hicieron el puente, con un **secreto** tras un matorral.
- Arte: `herramientas/pintar_sendero.py` (eco, campamento, página e icono), Msafiri en `herramientas/dibujar_aldeanos.py`, el suelo con `pintar_suelo.py` (puente, pretiles y vado).

### Las Pasarelas

Escena `escenas/mundo/las_pasarelas.tscn` (140×46), entre Cuna de Musgo y la Ciénaga Quieta (la puerta del este de la aldea lleva aquí; las espinas siguen hasta que Bibi abre el camino). Música propia: «Entre juncos» (un vals lento).
- Un prado inundado de agua clara con nenúfares y juncos. Se cruza por **pasarelas de tablas** sobre pilotes (`=`; las que bajan llevan las tablas en horizontal) entre islotes.
- **Korongo** (`}` con `viajero = "korongo"` en el nodo Region), la garza pescadora, junto a su **palafito** (`{`). Encargo: **tres nasas** (`` ` `` con `objeto_encargo = "nasa"`). Al devolvérselas da dos sopas y **arregla la pasarela rota** del sureste (`"`, `scripts/mundo/objetos/pasarela_rota.gd`: tabla a tabla, a martillazos), que lleva al islote del **segundo eco**.
- **Rana de piedra** (enemigo nuevo, `scripts/enemigos/rana.gd`): da saltitos; si ve a Maisha cerca se agazapa (sale una **sombra con un anillo violeta** donde va a caer) y salta. En el aire no se le puede dar. Al caer, la onda hace daño y se queda **atontada**: ahí el cetro le quita 2. Si se le da sin estar atontada, le quita 1 y se aparta de un salto. Valores en `reglas_combate.gd` (`RANA_*`).
- Una zona corrupta en el islote grande (ranas y babosas) y un secreto tras un matorral en el islote del sur.
- Arte: `herramientas/pintar_pasarelas.py` (palafito, rana, nasa e icono), Korongo en `dibujar_aldeanos.py`.
- Las letras `{` `}` `` ` `` sirven en cualquier camino: cada uno dice en su nodo Region quién es su viajero y qué se recoge.

### Camino Cobrizo

Escena `escenas/mundo/camino_cobrizo.tscn` (mapa de 64×100 casillas: sube de sur a norte, unas 4 pantallas de alto), entre los Prados del Eco y el Bosque Cobrizo. Música propia: «La loma de cobre» (kalimba que sube, flauta, campanillas y, lejos, el pico de un minero).
- Abajo, prado verde; según se sube, la hierba se oscurece, los árboles se vuelven cobrizos y el suelo se llena de hojas (pintado por filas en `pintar_suelo.py`). Caen hojas (`otono` en el Ambiente). Un **arroyo** lo cruza con un puentecito de tablas.
- **Fuko** (`}` con `viajero = "fuko"`), el topo minero: casi no ve (gafas de cristal gordo), casco de cobre con una vela. Vive en una **madriguera** (`{`: loma con puerta redonda, farol de mina y una vagoneta con mineral de cobre; sobre la puerta, una cuerda con tres ganchos vacíos). Encargo: **tres campanillas de cobre** (`` ` `` con `objeto_encargo = "campanilla"`; suenan al cogerlas) con las que se orienta en sus galerías. Al devolvérselas da dos sopas y **despeja el derrumbe**.
- **Peñas** (`0`, letra nueva): roca natural gris en 3/4 (encima, una masa abombada con grietas y musgo en la sombra; al sur, una pared de altura irregular con estratos y vetas de cobre y malaquita; contorno oscuro y piedras sueltas al pie); no se pueden cruzar. Encierran una hondonada al noreste: la **vieja galería de la mina**, con el **tercer eco**. Su boca la tapa un **derrumbe** (`"` en este camino, `scripts/mundo/objetos/derrumbe.gd`): los montones se deshacen uno a uno, con polvo, cuando Fuko lo despeja (marca `derrumbe_despejado/camino_cobrizo`).
- **Topo de piedra** (enemigo nuevo, `scripts/enemigos/topo.gd`): va **bajo tierra** (solo se ve un montoncito de tierra que avanza y su rastro; ahí no se le puede dar). Si oye a Maisha, va a por ella; al alcanzarla, el suelo **tiembla y se agrieta** (anillo violeta) y **sale mordiendo**. Fuera se queda **atontado**: el cetro le quita 2. Luego se vuelve a hundir. Las raíces de una semilla **lo sacan a la fuerza**. Valores en `reglas_combate.gd` (`TOPO_*`).
- Una zona corrupta al oeste (topos y Petrinos) y un secreto tras un matorral entre los árboles del noroeste.
- Arte: `herramientas/pintar_camino.py` (madriguera, topo, derrumbe, campanilla e icono), Fuko en `dibujar_aldeanos.py`.

### Senda de los Surcos

Escena `escenas/mundo/senda_surcos.tscn` (64×100, de sur a norte), entre Cuna de Musgo y el Campo Segado (la puerta del norte de la aldea lleva aquí; las grandes espinas siguen hasta que Bibi abre el camino). Música propia: «Canción de siega» (6/8 de fiesta: balafón, flauta, palmas y tambor).
- Huertas viejas: bancales de surcos con trigo seco, vallas, pacas y setos; abajo, la hierba verde de la aldea; arriba, el pasto seco del campo. Una **acequia** cruza de lado a lado (con un puentecito) y sube por el este.
- **Sungura** (`}` con `viajero = "sungura"`), la liebre guardasemillas, junto a su **hórreo** (`{`: granero sobre pies de piedra, tejado de paja, ristras de mazorcas y sacos). Encargo: **tres mazorcas antiguas** (`objeto_encargo = "mazorca"`). Al devolvérselas da dos sopas y **cierra la compuerta**.
- El **huerto viejo** del noreste, con el **cuarto eco**, está rodeado por un **foso de agua** (`"` en esta senda, `scripts/mundo/objetos/acequia_foso.gd`): al cerrar la compuerta el agua baja poco a poco, con gorgoteo, y queda el barro (marca `acequia_vaciada/senda_surcos`).
- **Cuervo de óxido** (enemigo nuevo, `scripts/enemigos/cuervo.gd`): vuela en círculos, alto (solo se ve su sombra; no se le puede dar). Cuando tiene a Maisha cerca, **apunta**: una **raya violeta** en el suelo marca por dónde va a pasar; luego se lanza **en picado**, rasante, y hace daño a quien esté en la raya. Al acabar se queda **posado** picoteando: el cetro le quita 2. Las raíces de una semilla no lo dejan despegar; la explosión le da aunque vuele. Valores en `reglas_combate.gd` (`CUERVO_*`).
- Una zona corrupta al este (cuervos y Petrinos) y un secreto tras un matorral en el seto del oeste.
- Arte: `herramientas/pintar_senda.py` (hórreo, cuervo, mazorca e icono), Sungura en `dibujar_aldeanos.py`.

### Cañada del Eco

Escena `escenas/mundo/canada_eco.tscn` (mapa de 140×46 casillas, de este a oeste: unas 3,5 pantallas), entre el **Bosque Cobrizo** (la nueva salida del oeste del bosque lleva aquí) y el **Lago Espejo** (el paso del oeste sigue cerrado: niebla, marca `camino_lago`). El mapa se genera con `construir_mapa.py canada_eco --crear` (`crear_canada`). Música propia: «Lo que la peña devuelve» (`componer_musica.py canada`): la flauta toca el tema de Maisha en frases cortas y la peña se las devuelve dos veces, más suaves y del otro lado; al final, una frase de piano sin eco (la de Kimya), con viento en la garganta, kalimba y cencerros lejanos.
- Una **garganta** entre dos paredes de peña (`0`) con la **cara del acantilado el doble de alta** y, encima, una **meseta** de hierba (`_mesetas` en `pintar_suelo.py`): la roca solo se ve en el filo y en la cara.
- Un **arroyo** baja hacia el lago y cruza el camino, recto, bajo un **puentecito** de cuatro tablas apoyado en las dos orillas (este) y por un **vado** de piedras (oeste). Al este, hierba de bosque y hojarasca; al oeste, flores.
- **Rocas caídas** de las paredes (`ñ`: tres formas, una losa alta, una ancha y una partida en dos) al pie de la peña, sobre todo en la garganta, y **troncos secos** (`ç`) hacia el bosque. El **pedregal** (`scripts/mundo/canada/pedregal.gd`) llena el fondo de grava, piedrecitas, losas, matojos secos, tomillo en flor, flores de roca y matas, más espeso junto a las paredes.
- **Las cabras de Mbuzi** (`scripts/mundo/canada/cabras.gd`): doce, y una negra, Tumbo. Asustadas arriba, en el borde de las mesetas; al devolverle los cencerros bajan una a una al corral (Tumbo, la última).
- **Mbuzi** (`}` con `viajero = "mbuzi"`), la cabra montés pastora, mayor y tranquila, junto a su **aprisco** (`{`: cabaña de piedra seca con tejado de lajas, pesebre de heno y un corral grande de piedra seca con postes). Encargo: **tres cencerros** (`` ` `` con `objeto_encargo = "cencerro"`). Al devolvérselos da dos sopas y descuelga la **escala de cuerda** (`"` en esta cañada, `scripts/mundo/objetos/escala_cuerda.gd`: se desenrolla tramo a tramo; marca `escala_descolgada/canada_eco`) hasta la **cornisa** del **quinto eco**.
- Una zona corrupta en el ensanche del sur, con **murciélagos de eco** (enemigo nuevo, `scripts/enemigos/murcielago.gd` y su onda `onda_eco.gd`), y un secreto tras un matorral al noroeste.
  - Aparece **colgado** boca abajo y despierta con un chillido; **revolotea** en zigzag cerca de Maisha (en el aire el cetro no le da).
  - **Avisa**: se para, se le cierra un anillo alrededor y en el suelo sale una línea de puntos blancos por donde irá el grito.
  - **Grita**: una **onda** (arcos violetas y blancos) va en línea recta, rebota en el borde de la zona o al llegar lejos y **vuelve a él**. Hace daño a la ida y a la vuelta. El **Latido** la deshace.
  - Al tragarse su propio eco cae **aturdido** (estrellitas encima): el cetro le quita 2. Las raíces de una semilla lo sujetan en el suelo; la explosión le da aunque vuele. Números en `reglas_combate.gd` (`MURCIELAGO_*`).
- Arte: `herramientas/pintar_canada.py` (aprisco, escala, cencerro e icono, y el murciélago: 6 fotogramas), Mbuzi en `dibujar_aldeanos.py`. Bocetos y capturas en `documentacion/` (`boceto_canada_eco.png`, `boceto_canada_suelo.png`, `canada_eco_capturas.png`, `murcielago_eco_capturas.png`).
- El **quinto eco**, en la cornisa: Maisha, Mauti y Kimya gritando sus nombres (ver «Los ecos perdidos»).
- Sonidos propios (`crear_sonidos.py`): `murcielago_chillido`, `murcielago_aleteo`, `murcielago_grito`, `onda_rebota`, `murcielago_mareo`, `cencerro` (al recoger uno) y `escala_tramo` (cada tramo de la escala al desenrollarse).

## Lago Espejo

Escena `escenas/mundo/lago_espejo.tscn` (mapa de 96×64 casillas, `construir_mapa.py lago_espejo --crear`, `crear_lago`), al oeste de la **Cañada del Eco**. El paso de la Cañada se abre al escuchar el **quinto eco** (la puerta del oeste está `cerrada:eco/canada_eco`). Música propia: «El agua que recuerda» (`componer_musica.py lago`): el piano toca una frase del tema de Maisha y luego su **reflejo** (las mismas notas al revés, más graves y suaves); al final, la frase de Kimya, sin eco; con voces lejanas, kalimba lenta y gotas de agua.
- Un lago grande con una **isla** en el centro (donde aparecerá **Kimya**) y un **islote** con un secreto. El suelo pinta el agua **quieta como un espejo** (`_agua_espejo` en `pintar_suelo.py`).
- **Agua turbia** mientras vive **Kambare** (falta la marca `kambare_vencido`): dos capas de barro y óxido que se funden despacio, con burbujas y brillos de Giza (`scripts/mundo/lago/espejo_lago.gd`). Si Maisha intenta calmarla, piensa que algo grande remueve el fondo.
- **La quietud**: sin Kambare, si Maisha espera **sin moverse junto al agua** 3 segundos (`QUIETUD_SEGUNDOS`), un anillo se cierra a su alrededor y el lago se vuelve **espejo**. Andar no lo rompe; correr, golpear, lanzar una semilla, el Latido o una pelea, sí (salvo con Maisha encima de un puente).
- **Puentes del reflejo** (`\` en el mapa, `scripts/mundo/objetos/puente_reflejo.gd`): tablas de luz que apenas se adivinan con el agua movida y que, con el lago en espejo, se encienden de la orilla hacia dentro y se pueden cruzar. Uno largo hasta la isla y otro corto hasta el islote.
- Al noreste, una zona corrupta (salen ranas de piedra y petrinos). Misión «El Lago Espejo» (aparece al escuchar el quinto eco).
- **La orilla**: juncos espesos, sauces, nenúfares (`*`) en las calas, un **embarcadero viejo** de madera junto al pie del puente del reflejo, una **barca varada** en la playa del oeste (`þ`, se puede mirar) y el **altar de Kimya** en la orilla del este (`ð`: piedras planas apiladas con un cuenco de agua quieta, la piedra de la espiral y ofrendas de conchas y flores; se puede mirar). En la isla, un círculo de **piedras talladas** (`ø`, con espirales y rayas) y un sauce viejo. El bosque del borde, de ancho irregular. Arte: `herramientas/pintar_lago.py`.
- **Mdiria**, un martín pescador viejo (dibujo en `dibujar_aldeanos.py`), está de piedra junto a la arena de Kambare. Al vencer a Kambare despierta («¡Puaj! Tengo la boca llena de barro») y, en vez de irse a la aldea, anda hasta el embarcadero y se queda allí (`viajero = "mdiria"`, `viajero_requiere = "rescatado_mdiria"` en el nodo Region; la estatua con `se_queda_en`). Llama «Bigotes» a Kambare y deja cada mañana una concha en el altar.
- **Kambare, el siluro de cieno** (`scripts/enemigos/kambare.gd`, dibujo `herramientas/dibujar_kambare.py`, música «Kambare, el siluro de cieno»), minijefe en la arena de la orilla sur (zona `1` con `jefe:kambare`):
  - **Nada** en su charca de cieno, medio hundido: solo asoman la cabeza, la aleta y las burbujas, y el cetro no le da. El cieno de la charca frena a Maisha.
  - **Apunta**: una sombra (con el anillo de la ola) marca dónde caerá, cerca de Maisha. **Salta** y, al caer, levanta una **ola de barro** en anillo que hace daño.
  - **Varado** en la orilla, coleteando y con estrellitas: el cetro le quita 1 y una semilla que le estalle al lado, 2. Luego vuelve arrastrándose a la charca.
  - **Fase 2** (con la mitad de vida): escupe **chorros de cieno** en abanico (dejan charcos que frenan) y a veces salta dos veces seguidas.
  - Al vencerlo se le cae el barro: queda un siluro limpio, pardo dorado, que se hunde en la charca. Marca `kambare_vencido`: el agua del lago se aclara y Maisha piensa que, si espera sin moverse, el lago le enseñará lo que guarda. Números en `reglas_combate.gd` (`KAMBARE_*`).
- **Kimya, el Silencio** (`scripts/mundo/lago/kimya.gd`), en el círculo de piedras de la isla: solo existe en el reflejo, así que aparece cuando el lago es espejo y se desvanece si el agua tiembla. Hecha de luz plateada, con los ojos cerrados y dos hilos de luz que caen como cintas. Al hablar con ella (conversación `kimya`, marca `kimya_conocida`) cuenta quién es y, con la ilustración `17_kimya_lago` (`cinematicas_sendero.py`), Maisha ve en el agua que su reflejo no es ella sino **Mauti**, del revés. Kimya cuenta que Mauti fue a buscar a quien quería que nada se segara nunca y no volvió, y cómo nació Giza; y que, con todos los ecos, el camino olvidado se abrirá.
- En el islote del norte hay un **secreto** (esencia), al que se llega por el puente del reflejo corto.
- Capturas: `documentacion/lago_espejo_capturas.png` y `documentacion/kambare_capturas.png`.

### Orilla de Juncos

Escena `escenas/mundo/orilla_juncos.tscn` (mapa de 64×100 casillas, de sur a norte: `construir_mapa.py orilla_juncos --crear`, `crear_orilla`), entre la **Ciénaga Quieta** (la nueva salida del este de la ciénaga lleva aquí) y el **Embarcadero Junco** (el paso del norte se abre al escuchar el **sexto eco**: la puerta está `cerrada:eco/orilla_juncos`; antes, la orilla hundida no deja pasar).
- Por el este baja el **río ancho**, con **playas de arena** y barro húmedo en las dos orillas (`_playas` en `pintar_suelo.py`), juncos y sauces. En medio, un **banco de arena** con el **sexto eco**.
- **Kasia** (`}` con `viajero = "kasia"`), la nutria barquera, risueña y charlatana, con sombrero de paja y un remo al hombro, junto a su **casa de barcas** (`{`: caseta de tablas sobre pilotes, tejado de juncos, la proa de la barca asomando, una red tendida y el soporte de los remos con tres huecos vacíos). Encargo: **tres remos** (`` ` `` con `objeto_encargo = "remo"`), que se llevó una crecida y han ido pescando los cangrejos.
- **La balsa** (`"` en esta orilla, `scripts/mundo/objetos/balsa.gd`): medio hundida hasta que Kasia la saca del agua (marca `balsa_arreglada/orilla_juncos`). Entonces, con Acción, Maisha se sube y **la balsa cruza sola el río** hasta el banco de arena (y vuelve igual).
- **Cangrejos de herrumbre** (enemigo nuevo, `scripts/enemigos/cangrejo.gd`) en una zona corrupta de la playa del sur: andan de lado; de frente, el cetro rebota en su caparazón. Avisan levantando las pinzas y pellizcan con un pasito hacia delante; justo después quedan **expuestos** (el cetro les quita 1). La explosión de una semilla los **vuelca** panza arriba (el cetro les quita 2). Números en `reglas_combate.gd` (`CANGREJO_*`).
- Un secreto entre los juncos del noroeste. Arte: `herramientas/pintar_orilla.py` (casa de barcas, balsa, cangrejo, remo e icono), Kasia en `dibujar_aldeanos.py`. Sonidos: `cangrejo_chasca`, `cangrejo_vuelca`.
- Música propia: **«La linterna en la orilla»** (`orilla` en `componer_musica.py`), una barcarola en seis (la canción de las barcas, que se mece): kalimba en vaivén, flauta, piano, gotas y el chapoteo de un remo.

## Embarcadero Junco

Escena `escenas/mundo/embarcadero_junco.tscn` (mapa de 96×72 casillas, `construir_mapa.py embarcadero_junco --crear`, `crear_embarcadero`), al norte de la **Orilla de Juncos** (se llega tras el sexto eco). El puerto del río de Raíz. Boceto: `documentacion/boceto_embarcadero_junco.png`; capturas: `documentacion/embarcadero_capturas.png`.
- El **río ancho** baja por el este, con playas (las mismas de la Orilla). En la orilla del oeste, el **pueblo de barqueros**: seis casas sobre pilotes con los pies en el agua (`æ`, 100×92, dos dibujos), un **almacén** (`œ`, 132×108) y una **grúa** rota (`å`); se pueden mirar. Las casas y el almacén están pintados con las mismas ayudas y el mismo nivel de detalle que la casa del castor (`pintar_casa_shamba.py`: paja a capas, troncos, ventanas con contraventanas y jardinera, zócalo de piedra).
- Arriba, el **muelle del norte** con el **transbordador** varado (`ß`: dibujo 0 varado, escorado y con un boquete; 1 arreglado, con la marca `transbordador_listo`). Al norte, **La Travesía** (río arriba, hacia la Gruta de las Raíces), cerrada hasta `transbordador_listo`.
- **La casa sellada de Bata** (`scripts/mundo/embarcadero/casa_sellada.gd`, capturas `documentacion/casa_sellada_capturas.png`): Bata, el pato barquero, está encerrado **vivo** en su casa junto al muelle (`{`, `casa_bata.png`), con la puerta y la ventana tapadas por raíces de piedra de Giza (`sello_raices.png`). Habla a través de la puerta y da la pista. De las raíces salen **venas violetas** por el suelo, con pulsos que van hacia la casa; siguiéndolas al revés se llega a un **nudo de Giza** (`nudo_giza.png`) tapado por **sacos** delante del almacén. El cetro no mueve los sacos: el **Latido** los aparta. El cetro rebota en el nudo: una **semilla** lo revienta. Entonces las venas se secan como una mecha hasta la casa, las raíces se deshacen y Bata sale y se va a su muelle (marca `casa_bata_abierta`, que es también la que hace falta para ver a Bata en el muelle).
- Abajo, la **dársena**: un entrante de agua con una gran **plataforma de madera** en medio (zona 1), donde acecha Mamba.
- Tres zonas corruptas (cangrejos, petrinos y babosas) y tres secretos. Música: de momento la de la Orilla.
- Arte: `herramientas/pintar_embarcadero.py`. Prueba: `pruebas/prueba_embarcadero_junco.gd`.
- **Mamba, el cocodrilo de herrumbre** (jefe de la dársena, `scripts/enemigos/mamba.gd`, dibujo `herramientas/dibujar_mamba.py`, capturas `documentacion/mamba_capturas.png`): flota como un tronco alrededor de la plataforma (en el agua no se le puede dar); avisa con una raya de por dónde va a embestir; embiste en línea recta y, si hay un **poste de amarre** (`ł`, cuatro en la plataforma) en su camino, se le clavan los dientes y queda atascado: el cetro le quita 1, una semilla 2. **Pelea 2 contra 1**: si Bata ya está libre, rema en su barca (`barca_bata.gd`, `barca_bata.png`) alrededor de la plataforma persiguiendo a Mamba y, cuando lo alcanza, lo **sujeta con la pértiga** contra el borde: a tiro desde la plataforma (cetro 1, semilla 2). La dársena no despierta hasta que Bata está libre (antes, Maisha piensa que sola no). Fase 2: avisa más deprisa, si Bata lo sujeta al soltarse le muerde la barca (Bata se aparta asustado), a veces embiste dos veces y al soltarse da un coletazo en círculo. Vencido, se le cae la herrumbre y se va río abajo (marca `mamba_vencido`). Música propia «Mamba, el cocodrilo de herrumbre» y sonidos `mamba_*`.
- Los vecinos con su sitio lejos (como Bata y su transbordador) dan unos pasos, se pierden de vista y aparecen allí (`estatua.gd`).
- **Arreglar el transbordador**, con los poderes de Maisha y sin recados (`scripts/mundo/embarcadero/arreglo_transbordador.gd`, capturas `documentacion/transbordador_arreglo.png`), solo cuando Mamba ya no está: una **semilla** que estalle en la punta del muelle, junto al boquete, hace crecer **juncos que se tejen** y lo tapan (`boquete_tapado`, dibujo 2: tapado pero escorado); después, el **Latido** pegado al casco la endereza y vuelve a flotar (`transbordador_listo`). Bata va dando las pistas según el momento.
- La puerta del norte (La Travesía) sigue cerrada (`travesia_abierta`) hasta que exista ese camino: se irá en el transbordador.
- Falta: La Travesía y la música propia del Embarcadero.

### Los ecos perdidos (el misterio de Raíz)

Piedras altas con una espiral tallada (`scripts/mundo/objetos/eco_perdido.gd`). Al acercarse brillan y sueltan motas de luz; con **Acción**, el mundo se tiñe de verde-agua y se oye un recuerdo con su ilustración (conversación `eco_<mapa>` en `datos/dialogos/raiz.json`). Cada uno deja la marca `eco/<mapa>`. Hay **9** en todo Raíz (uno por camino, de momento solo el del puente): juntos abrirán el Sendero Olvidado hacia las Ruinas del Primer Árbol. Misión «Los ecos perdidos» en el diario.
- El primer recuerdo: `arte/historia/12_eco_puente.png` (`herramientas/cinematicas_sendero.py`): el puente a medio hacer y el Primer Árbol dorado al fondo.
- El segundo (Las Pasarelas): `13_eco_pasarelas.png`: una noche de luna; bajo el agua, las raíces doradas del Primer Árbol y **Kimya, el Silencio**, deslizándose entre ellas.
- El tercero (Camino Cobrizo): `14_eco_cobrizo.png`: una tarde de otoño bajo un árbol de hojas de cobre; Maisha y **Mauti** (plateada y lila, con una hoja seca en lo alto) hablan de por qué caen las hojas: «Tú y yo somos el mismo árbol».
- El cuarto (Senda de los Surcos): `15_eco_surcos.png`: la fiesta de la última siega, de noche, con farolillos, gavillas y una hoguera; Maisha y Mauti bailan de la mano. «Lo que se siembra, Maisha lo despierta. Lo que se siega, Mauti lo guarda.» Y una pregunta que da miedo: «¿Y si un día alguien quisiera que nada se segara nunca?»
- El quinto (Cañada del Eco): `16_eco_canada.png`: un atardecer en la garganta. En la cornisa, Maisha y Mauti gritan sus nombres y la peña se los devuelve; **Kimya** flota sobre el arroyo quieto y no grita: «El Silencio no tiene eco. Por eso puedo oíros a los dos.» Solo el agua refleja a Kimya, y eso apunta al Lago Espejo.
- El sexto (Orilla de Juncos): `18_eco_orilla.png`: **la despedida**. Una noche de luna en el río ancho: Mauti se aleja río arriba en una barca pequeña, con su luz lila, y Maisha se queda en la playa con una linterna encendida. «Déjala encendida aquí, en la orilla. Así sabré por dónde volver.» Mauti iba a hablar con quien no quería que nada se segara nunca, río arriba, hacia el norte. Nadie volvió a buscar la linterna.

## Bosque Cobrizo

Escena `escenas/mundo/bosque_cobrizo.tscn`: la segunda región de Raíz, al norte de los Prados del Eco.

- **Cómo se abre**: cuando Pino y Corteza han vuelto, Bibi siente que las raíces del Gran Árbol han secado las espinas del norte de los prados y las del este de la aldea (marcas `camino_bosque` y `camino_cienaga`; las espinas se marchitan): el bosque y la ciénaga se pueden hacer en el orden que se quiera. Antes, Maisha piensa que no puede pasar.
- **El bosque** (112×72 casillas): árboles cobrizos y rojizos (`J`, `j`) y altos (`I`), muy juntos en los bordes y con claros dentro, cada uno un poco movido para que no vayan en filas; suelo de musgo con hojarasca (`pintar_suelo.py`), helechos, tocones huecos que se pueden mirar, un arroyo con puentes y muchas más hojas cayendo, cobrizas y rojizas (`otono` en el Ambiente). Música propia: «Hojas de cobre» (arpa y flauta).
- **3 zonas corruptas**; junto a la segunda está **Tawi** de piedra. **2 claros secretos** tras matorrales.
- **Troncos podridos** (`U`): estorban el paso; el cetro solo los hace temblar, una **semilla los parte** y dejan **madera**.
- **Jabalí de hierro** (enemigo «cazador», `scripts/enemigos/jabali.gd`): deambula; si ve a Maisha en su fila o columna, **escarba** (sale una «!») y **embiste** en línea recta muy deprisa. Al chocar con algo (un árbol, una roca, **los brotes de una semilla**, el borde de la zona) se queda **aturdido** con estrellitas: es el momento de golpearle, porque si no, el cetro rebota en su hierro. Las semillas le dañan siempre y el Latido le corta la embestida. En el bosque las zonas sacan jabalíes y Petrinos por turnos (`tipos_enemigo` en el nodo Region).
- **Pembe, el ciervo de hierro** (minijefe, `scripts/enemigos/pembe.gd`), en su claro con cuatro árboles:
  - Acecha, **escarba** (una franja roja marca por dónde va a ir) y **embiste**.
  - Si se clava contra un **árbol**, queda **atascado** unos segundos: el cetro le quita 1 y cada semilla que le estalle al lado, 2. Si choca con el borde del claro, se repone enseguida. Mientras no está atascado, todo rebota en sus placas.
  - Con la mitad de vida: se prepara más rápido, llama a dos jabalíes y, al soltarse de un árbol, **caen trozos de hierro del cielo** (con su sombra de aviso).
  - La cámara enseña el claro entero durante la pelea. Música propia: «Pembe, el ciervo de hierro».
  - Al vencerlo, el hierro se le cae, sus astas vuelven a tener hojas de cobre, se inclina ante Maisha y se va. El narrador lo cuenta con la ilustración `9_pembe_libre` (`herramientas/cinematicas_bosque.py`).
- Para rehacer el arte: `python3 herramientas/dibujar_bosque.py` (árboles, troncos, madera, tocón, helechos), `dibujar_jabali.py`, `dibujar_pembe.py`; el mapa: `python3 herramientas/construir_mapa.py bosque_cobrizo` (con `--crear` se genera de nuevo y **se sobrescribe**).

## Ciénaga Quieta

Escena `escenas/mundo/cienaga_quieta.tscn`: la tercera región de Raíz, al este de Cuna de Musgo.

- **Cómo se abre**: a la vez que el Bosque Cobrizo (el jugador elige el orden): Bibi siente que se han secado las espinas del norte de los prados y las del este de la aldea (marcas `camino_bosque` y `camino_cienaga`). Antes, Maisha piensa que no puede pasar.
- **La ciénaga** (100×68 casillas): agua quieta con nenúfares, sauces, árboles muertos, juncos y barro; caminos de tierra y pasarelas de madera. **Niebla baja** que se arrastra despacio (`niebla` en el nodo Ambiente): es más espesa donde todo está gris y se levanta al purgar la región. Luciérnagas, ranas lejanas en el ambiente y música propia: «Agua quieta» (balafón y flauta muy lentos, gotas de piano).
- **3 zonas corruptas**; junto a la segunda está **Juncia** de piedra. **3 secretos**: uno tras un matorral y **dos en islas** que todavía no se pueden alcanzar (se llegará con el hielo de Sigilia).
- **Bayas** (`$`) y **juncos** (`:`): se recogen al pasar y **vuelven a salir** a los 4 minutos de juego (se guarda en la partida).
- **Babosa de óxido** (enemigo «errante», `scripts/enemigos/babosa.gd`): se arrastra despacio y deja un **rastro de óxido** que frena a Maisha. Dos golpes de cetro o una semilla la deshacen; no cruza los brotes. Aquí las zonas sacan babosas y Petrinos.
- **Konokono, la caracola de óxido** (minijefe, `scripts/enemigos/konokono.gd`, 100×74 píxeles), en su poza:
  - Se arrastra hacia Maisha dejando óxido. Su concha lo aguanta todo: el cetro rebota (y se esconde un momento) y las semillas de fuera no le hacen nada.
  - **Se traga las semillas** que encuentra delante o por las que pasa por encima (abre la boca cuando ve una). La semilla le **estalla dentro**: le quita 2 y la deja **mareada** fuera de la concha. Entonces el cetro le quita 1.
  - Con la mitad de vida: llama a dos babosas, a veces se esconde y **rueda** en línea recta (rebota en el borde y se marea al tercer rebote) o **escupe bolas de óxido** (con sombra de aviso) que dejan charcos que frenan.
  - La cámara enseña la poza entera. Música propia: «Konokono, la caracola de óxido».
  - Al vencerla, la herrumbre se le cae y la concha vuelve a ser de nácar con musgo y flores. El narrador lo cuenta con la ilustración `10_konokono_libre` (`herramientas/cinematicas_cienaga.py`).
- Para rehacer el arte: `python3 herramientas/dibujar_cienaga.py` (sauce, árbol muerto, juncos, nenúfar, babosa, bayas, junco, sopa), `dibujar_konokono.py`; el mapa: `python3 herramientas/construir_mapa.py cienaga_quieta`.

## Campo Segado (el jefe de Raíz)

Escena `escenas/mundo/campo_segado.tscn`: la última región de Raíz, al norte de Cuna de Musgo.

- **Cómo se abre**: cuando Pembe y Konokono son libres, Bibi oye un crujido: caen las grandes espinas del camino del norte de la aldea (marca `camino_campo`).
- **El campo** (96×64 casillas): los viejos campos de trigo de Raíz. Surcos de tierra labrada (`/`, un suelo nuevo con lomos y rastrojo), trigo seco, espantapájaros, vallas, pacas, máquinas viejas oxidadas, un granero en ruinas y un molino roto en el cruce (se pueden mirar). Hierba seca y dorada. Música propia: «Surcos de hierro» (tensa y metálica, con un traqueteo que no para).
- **2 zonas corruptas**: salen jabalíes, babosas y Petrinos (lo aprendido en todo Raíz). **1 secreto** tras un matorral.
- **La Cosechadora Oxidada** (jefe del mundo, `scripts/enemigos/cosechadora.gd`), en el gran campo del norte. Mide **128×96 píxeles** y se dibuja **por capas** (`arte/zonas/raiz/cosechadora/`): las ruedas, los pistones y el molinete giran de verdad al andar, los depósitos burbujean y cada parte se ve agrietada y luego rota.
  - Recorre el campo **fila a fila** con su molinete de cuchillas (las cuchillas quitan 2; el cuerpo, 1). Va un **40 % más rápida** que antes en todo.
  - **Se rompe por partes** (una fila bajo su barra con cada parte y sus marcas). Su chapa lo aguanta todo; cada punto débil se abre de una forma:

| Parte | Vida | Cuándo se puede dañar | Al romperla |
| --- | --- | --- | --- |
| Caldera (atrás) | 4 | Atascada en los brotes de una semilla. Cetro 1, semilla 2. Al 3.er golpe (2.º en Furia) se suelta | Revienta, sale volando la rueda grande y va dando **bandazos** (+15 % de velocidad) |
| Depósito frontal | 3 | Aturdida tras estrellarse contra el borde en un acelerón, o estampada contra brotes. Cetro 1, semilla 2. Al 2.º golpe se suelta | **Fuga de fuego**: deja llamas por donde pasa y las cuchillas arden (+1 de daño) |
| Techo | 3 | Solo explosiones y solo con la máquina **en marcha**, estrellada o sobrecalentada (atascada, la tolva lo tapa). 1 por semilla | Sus **tuercas caen en llamas** y prenden tres casillas |
| Corazón de Giza | 3 | Solo cuando se abre, justo después de cada anillo. Cetro o semilla, 1; del golpe se cierra | Cae |

  - Con las tres partes rotas **se desploma** y deja al aire el **corazón de Giza**: lanza **anillos de fuego** con dos huecos que giran (pasa por un hueco o usa el Latido). Si estás encima al lanzarlo, quema.
  - La **Ira** sube sola (unos 10 s por etapa). Cada golpe en una parte la baja una etapa, pero cada parte rota sube el mínimo (con una no baja de Enfado; con dos, de Furia):
    - **Calma**: recorre las filas.
    - **Enfado**: se para a lanzar **tuercas** que dejan **bloques de chatarra** (una semilla los deshace).
    - **Furia**: llama a babosas y **Giza cierra la arena desde el borde**.
    - **Frenesí**: si Maisha se pone en su fila, **embiste**. Al cabo de 9 s **se sobrecalienta**: se para 3,5 s soltando vapor (el techo, al aire) y la Ira vuelve a su mínimo.
  - El **acelerón infernal**: avisa con una franja roja, sale disparada y deja un **rastro de fuego de Giza**. Cuanto más enfadada, más «rota»:

| Etapa | Cada | Velocidad | Aviso | El fuego dura | Ancho | Además |
| --- | --- | --- | --- | --- | --- | --- |
| Calma | 7 s | 182 | 0,7 s | 3 s | 1 fila | — |
| Enfado | 5,6 s | 210 | 0,6 s | 4,5 s | 1 fila | — |
| Furia | 4,2 s | 240 | 0,5 s | 6 s | 3 filas | Apunta a la fila de Maisha |
| Frenesí | 2,8 s | 277 | 0,4 s | 8 s | 3 filas | El fuego se extiende; repite el acelerón de vuelta |

  - Jugadas buenas: esperar al final de la franja para golpear el depósito al estrellarse; plantar una semilla **dos filas al lado** de su camino para que estalle cuando pasa el techo (o donde se va a estrellar).
  - Música propia: «La Cosechadora Oxidada» (pistones y vapor; al final, el tema de Maisha en mayor, resistiendo).
  - Al vencerla se apaga, la cubren enredaderas y flores y el campo se llena de trigo dorado. El narrador lo cuenta con la ilustración `11_cosecha_libre` (`herramientas/cinematicas_campo.py`) y **Raíz queda libre** (marca `raiz_libre`). Bibi lo nota en las raíces y habla del trozo del mapa que falta: Sigilia.
- Para rehacer el arte: `python3 herramientas/pintar_campo.py` (granero, molino, máquinas, pacas, chatarra, tuerca) y `pintar_cosechadora.py`; el mapa: `python3 herramientas/construir_mapa.py campo_segado`.

## La tienda de Tawi y los Cristales del Nexo

- Los **Cristales del Nexo** son el dinero de las tiendas (la Esencia no se gasta en tiendas: es solo para las Artes, como dice el GDD). Se ganan al **cumplir misiones** (historia 3, encargo 2, secreto 2, lazo 2), con los **jefes** (Mzizi 2, Pembe 3, Konokono 3, la Cosechadora 5) y con cada **secreto** (1). Sale un aviso azul («+3 Cristales · …»). No se guardan aparte: se cuentan a partir de las misiones y marcas; lo gastado, sí.
- Con el puesto arreglado, **hablar con Tawi abre la tienda** (`scripts/interfaz/tienda_tawi.gd`): a la izquierda el puesto por dentro con Tawi detrás del mostrador (parpadea, habla mientras salen las letras y aplaude al vender); a la derecha lo que vende, con su precio. ↑ ↓ elegir · Acción comprar · Tab salir. Música propia: «El puesto de Tawi».
- Lo que vende (`datos/tienda.json`, se edita sin tocar código):

| Artículo | Precio | Qué hace |
| --- | --- | --- |
| Bayas y junco | 2 | 2 bayas y 1 junco (para una sopa). Se puede comprar siempre |
| Mapa de los secretos | 5 | En el Mapa de Raíz, cuántos secretos quedan en cada sitio |
| Corona de hojas | 6 | Prenda (cabeza) |
| Sombrero de paja | 7 | Prenda (cabeza), cuando se ha visto el Campo Segado |
| Capa de musgo | 9 | Prenda (espalda) |
| Semilla del olvido | 4 (+2 cada vez) | El Árbol de la Vida devuelve toda la Esencia para repartirla de nuevo |

- Las **prendas** compradas se ponen solas y luego se ponen o se quitan en la mochila (Objetos, con Acción). Se guardan con la partida. Las dibuja `herramientas/dibujar_prendas.py`; el puesto y Tawi, `pintar_tienda.py`; los iconos, `dibujar_tienda.py`.
- El autoload **Tienda** (`scripts/globales/tienda.gd`) lleva la cuenta de los cristales, las compras y la ropa.

## Fin de Raíz

Al vencer a la Cosechadora y acabar el narrador sale la pantalla del **final del mundo** (`scripts/interfaz/fin_mundo.gd`): la ilustración `11_cosecha_libre`, hojas doradas que caen, Maisha celebrándolo y lo conseguido, línea a línea (tiempo de juego, zonas purgadas, aldeanos de vuelta, secretos, misiones, Esencia y Cristales). Suena «Raíz respira». «Continuará en Sigilia...» · Acción para seguir jugando (no se cierra el juego: se puede seguir por Raíz).

## Cuna de Musgo (la aldea)

Escena `escenas/mundo/cuna_de_musgo.tscn`. En la aldea no se lucha.

- El **Gran Árbol** hueco, con la plaza de losas delante. Su puerta lleva al **Claro de Calma** (`escenas/interiores/claro_de_calma.tscn`): al cruzarla cambia la escena y se ve la habitación entera, como en Pokémon Platino.
- **Bibi Musgo** espera junto al árbol. Pino y Corteza aparecen junto a sus casas en ruinas cuando se les rescata.
- Con **Acción** (Espacio, E o botón A) se habla con los aldeanos y se miran las cosas: sale un bocadillo encima de lo que se puede usar. Una **«!»** avisa de que un aldeano tiene algo nuevo que contar.
- Casas en ruinas: casa-seta de Pino, taller de Corteza, cocina de Juncia y puesto de Tawi (cada dibujo trae ya su versión reconstruida).
- **Reconstrucción:** con 3 setas luminosas, Pino levanta su casa-seta y estrena la **torre del vigía** (los secretos de los prados lanzan un haz de luz). Con 2 trozos de mineral, Corteza enciende su forja, **templa el cetro** (el golpe llega más lejos) y se mete a trabajar en su taller.
- Las casas reconstruidas **se pueden visitar**: la casa de Pino (`escenas/interiores/casa_pino.tscn`) y el taller de Corteza (`escenas/interiores/taller_corteza.tscn`).
- **Tawi** (el pájaro mercader) vuelve a la aldea cuando se le rescata en el Bosque Cobrizo. Con **3 maderas** arregla su **puesto** y da el **Mapa de Raíz** (`arte/interfaz/mapa_raiz.png`, lo dibuja `herramientas/dibujar_mapa_raiz.py`): las regiones de Raíz con su nombre cuando se han visitado («???» si no) y dónde está Maisha. Después, al hablar con Tawi se abre su **tienda** (ver «La tienda de Tawi y los Cristales del Nexo»).
- **Juncia** (la rana cocinera) vuelve a la aldea cuando se la rescata en la Ciénaga Quieta, junto a su cocina. Con **4 bayas y 3 juncos** arregla la **cocina** y da **dos sopas**. Después, con **2 bayas y 1 junco** cocina otra cada vez.
- **Sopa de Juncia**: devuelve **3 hojas de vida** al momento, también en plena pelea. Se toma con **F** (o desde la mochila, con Acción). Arriba a la izquierda, junto a la vida, se ve cuántas llevas.
- Ambiente: farolillos, setas, flores y luciérnagas.

### Cómo editar los diálogos

Todos los textos están en `datos/dialogos/raiz.json`. Cada personaje tiene varias conversaciones y se usa **la primera que cumple sus condiciones**:

- `"si"`: marcas que tienen que estar puestas · `"no"`: marcas que no pueden estar puestas · `"marca"`: se pone (o se ponen, si es una lista) al terminar de hablar.
- `"tiene"`: objetos que Maisha tiene que llevar · `"entrega"`: objetos que da al terminar · `"despues"`: líneas que se dicen un poco más tarde · `"aviso"`: mensaje que sale arriba al final.
- `{seta_luminosa}` y `{mineral}` se cambian por cuántos lleva Maisha.
- Marcas que ya existen: `bibi_conocida`, `rescatado_pino`, `rescatado_corteza`, `encargo_pino`, `encargo_corteza`, `construido_casa_seta`, `construido_taller`, `vigia`, `cetro_templado`, `bibi_aldea_viva`, `bibi_casas`, `zona/prados_del_eco/2`…
- Recuerda que Maisha es un espíritu sin género: nada de «bienvenido/a», «solo/a», «cansado/a»…

### Lo que el juego recuerda

`scripts/globales/estado.gd` (se carga solo al arrancar: lo verás en Proyecto → Configuración del proyecto → Globales) guarda lo que ya ha pasado aunque cambies de escena: zonas purgadas, secretos, el escondite abierto, setas y mineral recogidos (y lo que lleva Maisha), rocas rotas, aldeanos rescatados, casas reconstruidas y conversaciones. Todo eso es lo que se guarda en la partida.

### Cómo editar un mapa

1. Abre `datos/mapas/prados_del_eco.txt` con TextEdit (Formato → Convertir a texto sin formato). **Cada letra es una casilla.**
   La lista de letras está al principio de `herramientas/construir_mapa.py` (`T` árbol, `R` roca, `#` camino, `~` agua, `%` losas, `1`-`9` zonas corruptas, `G` Gran Árbol, `h` `f` `k` `n` casas, `l` farolillo, `b` `p` `o` aldeanos…).
2. El tamaño de cada zona corrupta (y el aldeano de piedra que tiene al lado) está en `datos/mapas/<mapa>.zonas`; las salidas a otras escenas, en `datos/mapas/<mapa>.puertas`.
3. En la Terminal, dentro de la carpeta del proyecto: `python3 herramientas/construir_mapa.py prados_del_eco` (o `cuna_de_musgo`)
   La primera vez, instala antes lo que necesitan los programas de dibujo: `python3 -m pip install --user pillow numpy`
   (vuelve a dibujar el suelo y prepara el mapa para el juego).
4. Pulsa `⌘ + B` en Godot.

> No uses la opción `--crear`: genera un mapa nuevo y **sobrescribe** el tuyo.

## Prototipo de combate

Escena `escenas/prueba_combate.tscn` (para abrirla: doble clic en ella en Godot y `⌘ + R`): un prado con una sola **zona corrupta**, útil para probar el combate.

1. Al acercarte, el color se apaga y aparecen la Vida (hojas) y el Aliento (barra).
2. Al cruzar el umbral, se levantan **raíces-espina de piedra** y la zona se cierra: no se puede salir hasta romper el **Corazón de Giza** (el tocón de piedra con el ojo violeta).
3. Los **Petrinos** (trozos de raíz de piedra que caminan) se vencen a golpes de cetro (J); el Corazón solo se rompe con **semillas** (K): hacen falta 3.
4. Al romperlo, la piedra se deshace, la raíz vuelve a ser **madera viva** y el color vuelve en una ola. Si caes dentro, vuelves al borde.

**Cómo es una zona infectada («el nudo de raíces de piedra»):** su borde tiene **forma natural** (no es un círculo perfecto: se aleja o se acerca según la dirección, distinta en cada zona) y las raíces-espina lo siguen. Giza se agarra a una raíz del mundo, le bebe la vida y la vuelve de piedra. En el suelo se ven las raíces de piedra saliendo del Corazón, con grietas violetas; por ellas corren gotas de luz **hacia** el Corazón (Giza bebiendo) y una **sombra viva** respira a su alrededor. Al purgarla, la luz corre **hacia fuera**.
- El suelo de cada zona lo dibuja `herramientas/dibujar_zona.py` según su tamaño (`arte/zonas/<mapa>_<zona>.png` y el recorrido de las raíces en `datos/zonas/`). `construir_mapa.py` lo llama solo, así que si cambias una zona basta con volver a construir el mapa.
- Las raíces-espina, el Corazón (grande y pequeño), el Petrino y Mzizi de cada mundo están en `arte/zonas/<mundo>/` (ahora solo `raiz`). Los dibuja `herramientas/dibujar_criaturas.py` (el Corazón, los Petrinos, Mzizi, sus agujeros y sus piedras) y `dibujar_zona.py` (los suelos y las raíces-espina).
- En `.zonas`, un sexto campo convierte una zona en **de práctica** (`practica`: cada partida salen 3 de ellas) o en la **arena de un jefe** (`jefe:mzizi`). Cada mundo tendrá su versión (por ejemplo, algas de piedra en el agua).

| Archivo | Qué hace |
| --- | --- |
| `scripts/combate/reglas_combate.gd` | **Todos los números del combate** (vida, Aliento, daño, tiempos). Cámbialos aquí para ajustar la sensación |
| `scripts/personajes/maisha.gd` | Movimiento, golpe, semilla, Latido, daño y caída |
| `scripts/combate/zona_corrupta.gd` | Borde, umbral de raíces-espina, cierre, enemigos, purga, vuelta al borde, y la luz y la sombra de Giza |
| `scripts/combate/semilla.gd` | Mecha, explosión en cruz, reacción en cadena y brotes |
| `scripts/enemigos/petrino.gd`, `nucleo_giza.gd` | El enemigo común de Raíz y el Corazón de Giza (su pupila sigue a Maisha) |
| `scripts/enemigos/mzizi.gd`, `piedra_mzizi.gd` | Mzizi, la raíz del Arco (miniboss del Kitovu) y las piedras que escupe |
| `scripts/interfaz/barra_jefe.gd` | La barra de vida de un jefe, con su nombre |
| `scripts/combate/forma_zona.gd` | La forma natural del borde de cada zona |
| `scripts/efectos/astillas.gd` | Trocitos de piedra que saltan al romperse algo |
| `scripts/interfaz/hud_combate.gd` | Vida, Aliento y mensajes (solo aparecen cuando hacen falta) |
| `scripts/combate/gestor_corrupcion.gd` | El gris de la región y de sus zonas; devuelve el color al purgar |
| `scripts/mundo/region.gd` | Construye una región a partir de su mapa de texto |
| `scripts/mundo/ambiente.gd` | Nubes, hojas, polen y ceniza, mariposas, luciérnagas y brillos del agua |
| `scripts/mundo/luz_sol.gd` | Rayos de sol y viñeta en la pantalla (`rayos_de_sol` en el nodo Ambiente para quitarlos) |
| `scripts/mundo/escena_mundo.gd` | Lo común a todas las escenas: dónde aparece Maisha, la cámara, el título |
| `scripts/mundo/puerta.gd` | Pasar a otra escena al pisarla (con fundido a negro) |
| `scripts/mundo/aldea/` | Gran Árbol, edificios, farolillos y aldeanos |
| `scripts/mundo/objetos/estatua.gd` | Aldeanos de piedra que despiertan al purgar su zona |
| `scripts/mundo/objetos/recogible.gd`, `roca_mineral.gd` | Setas luminosas y mineral que se recogen; rocas que se rompen con semillas |
| `scripts/mundo/interiores/` | Interiores: Claro de Calma, y la base de las casas (`interior_casa.gd`) con la casa de Pino y el taller de Corteza |
| `scripts/mundo/charla.gd` | Elige qué dice cada personaje, entrega objetos y da recompensas |
| `scripts/interfaz/dialogo.gd` | Caja de diálogo y bocadillos de «se puede usar» |
| `scripts/globales/estado.gd` | Lo que el juego recuerda entre escenas, guardar y cargar la partida, y los cambios de escena |
| `scripts/interfaz/inicio.gd` | La pantalla de inicio y la introducción |
| `scripts/interfaz/menu_pausa.gd` | El menú de pausa |
| `scripts/interfaz/mochila.gd` | La mochila y sus pestañas |
| `scripts/mundo/kitovu/` | El Kitovu: el guion del comienzo (`kitovu.gd`), el arco, la casa, el huerto, la pesca… |
| `scripts/mundo/interiores/casa_shamba.gd` | La casa del castor y la escena en la que nota el brillo |
| `scripts/interfaz/menu_lista.gd` | Las listas de opciones de los menús (teclado, mando y ratón) |
| `herramientas/dibujar_aldea.py` | Dibuja la aldea, las estatuas y los interiores (Claro de Calma, casa de Pino, taller) |
| `herramientas/dibujar_raiz.py` | Dibuja los objetos de Raíz (árboles, rocas, ruinas, matorral, setas luminosas, mineral…) |
| `herramientas/dibujar_combate.py` | Dibuja el cetro, la semilla, la explosión y los brotes |
| `herramientas/dibujar_zona.py` | Dibuja las zonas infectadas: su forma natural, el suelo de raíces de piedra (y vivas) y las raíces-espina |
| `herramientas/dibujar_criaturas.py` | Dibuja con detalle el Corazón de Giza, los Petrinos y Mzizi (cabeza, cuerpo, agujeros y piedras) |

La escena anterior, solo para pasear y probar la ropa, sigue en `escenas/prueba_maisha.tscn`.

## Impacto: que los golpes se sientan

**La velocidad del juego la lleva solo `Impacto`** (`poner_lenta`, `pausa`, `restablecer_velocidad`): la velocidad es la de base × la cámara lenta × el parón del golpe. Antes, la cámara lenta de la lección de la semilla y el parón de un golpe se guardaban «cómo estaba» cada uno, y si se cruzaban el juego se quedaba a cámara lenta para siempre (parecía que Maisha no podía correr). Cada escena deja la velocidad normal al empezar.

El autoload **Impacto** (`scripts/globales/impacto.gd`) da contundencia al combate:

| Cuándo | Qué pasa |
| --- | --- |
| El cetro acierta | El juego se congela 0,045 s, la cámara tiembla un poco y salta una estrella de chispas (gris si rebota, como en la piedra de Mzizi) |
| Estalla una semilla | Fogonazo de luz, una onda que se abre por el suelo, humo que sube, chispas y terrones que caen, y temblor |
| Maisha recibe daño | Pausa breve, temblor y un velo rojo suave en la pantalla |
| Se rompe un Corazón de Giza | Pausa más larga, temblor fuerte y un fogonazo violeta claro |
| Mzizi recibe una semilla | Pausa breve (además de sus astillas y su temblor) |

En el menú de pausa se pueden quitar los **temblores de pantalla** (se guarda).

## Ropa por capas

La ropa de Maisha se dibuja aparte y el juego la cuelga de sus **puntos de anclaje** en cada fotograma (nodo `Ropa` de `escenas/personajes/maisha.tscn`).

- Catálogo de prendas: `datos/prendas.json` · anclajes: `datos/maisha_anclajes.json`
- Dibujos: `arte/personajes/maisha/prendas/`
- Prendas de Raíz ya hechas: **Corona de hojas** (cabeza) y **Capa de musgo** (espalda)
- En las escenas de prueba, las teclas **1 a 8** cambian la prenda de cada zona (8 = arma: el cetro).
- Cómo añadir prendas nuevas: [`documentacion/ropa_por_capas.md`](documentacion/ropa_por_capas.md)

## Música y sonido

**Todo lo que suena lo hemos creado nosotros** con un sintetizador hecho en Python (`herramientas/sintetizador.py`): no hay muestras ni canciones de nadie, así que no hay problemas de derechos. La base es un **piano suave** (de fieltro, cálido, con mucho espacio), como la música tranquila de los juegos de explorar, con kalimba, balafón y flauta para darle el aire del mundo. La melodía que vuelve en todas las piezas es el **tema de Maisha**.

Cada pieza tiene **nombre** (va también dentro del `.ogg`, en el título):

| Archivo (`audio/musica/`) | Nombre | Dónde suena |
| --- | --- | --- |
| `despertar` | «Un largo letargo» | Partida nueva: un zumbido apagado, como desde dentro del sueño, un latido que se apaga, notas de piano sueltas, la **brisa** en la hierba y, al final, acordes y el tema de Maisha. Luego pasa sola a la del Kitovu |
| `kitovu` | «Raíces dormidas» | Piano solo, con mucho silencio. **No suena sin parar**: al acabar hay un rato de silencio (brisa, viento, agua) y vuelve |
| `inicio` | «El tema de Maisha» | La pantalla de inicio |
| `prados` | «Camino de los Prados» | Los Prados del Eco (piano con ritmo y flauta) |
| `aldea` | «Cuna de Musgo» | La aldea (piano saltarín y balafón) |
| `interior` | «Nana de la chimenea» | Dentro de las casas (con silencios entre una vez y otra) |
| `noche` | «Noche en la granja» | La primera noche en casa de Mzee Shamba |
| `combate` | «Manchas de Giza» | Dentro de una mancha de Giza |
| `jefe` | «Mzizi, la raíz del Arco» | La pelea contra Mzizi |
| `recuerdo` | «Un eco de antes» | Fanfarria: cada recuerdo de la chispa de vida |
| `amanece` | «Amanece» | Fanfarria: la mañana después de la noche en la granja |
| `tarea` | «Tarea cumplida» | Fanfarria: entregar un encargo |
| `objeto` | «¡Lo tengo!» | Fanfarria: conseguir algo importante |
| `purga` | «Vuelve el color» | Fanfarria: limpiar una mancha |
| `victoria` | «El Arco despierta» | Fanfarria: vencer a Mzizi |
| `bosque` | «Hojas de cobre» | El Bosque Cobrizo (arpegios como de arpa, flauta y campanitas que caen como hojas) |
| `jefe_pembe` | «Pembe, el ciervo de hierro» | La pelea contra Pembe (galope de tambores y hierro) |
| `cienaga` | «Agua quieta» | La Ciénaga Quieta (re dórico muy lento: el tema de Maisha como un reflejo, en balafón y flauta grave) |
| `jefe_konokono` | «Konokono, la caracola de óxido» | La pelea contra Konokono (tambor pesado que se arrastra en 3+3+2 y el tema «oxidado») |
| `campo` | «Surcos de hierro» | El Campo Segado (la menor, balafón inquieto, hierros que suenan con el viento) |
| `jefe_cosechadora` | «La Cosechadora Oxidada» | La pelea contra la Cosechadora (pistones y vapor; al final el tema de Maisha en mayor) |
| `tienda` | «El puesto de Tawi» | La tienda de Tawi (alegre, de mercado) |
| `raiz_libre` | «Raíz respira» | La pantalla del final de Raíz (no se repite) |
| `sendero` | «El puente viejo» | El Sendero del Puente |
| `pasarelas` | «Entre juncos» | Las Pasarelas (un vals lento) |
| `cobrizo` | «La loma de cobre» | El Camino Cobrizo (kalimba, flauta, campanillas y el pico de un minero) |
| `surcos` | «Canción de siega» | La Senda de los Surcos (6/8 de fiesta: balafón, flauta y palmas) |

- **Partes con nombre** para reutilizar: al principio de `herramientas/componer_musica.py` están las melodías y acordes sueltos (`TEMA`, `TEMA_MENOR`, `ACORDES_LETARGO`, `TEMA_DESPERTAR`, `ACORDES_RAICES`, `MELODIA_RAICES`, `TEMA_COMPLETO`, `TEMA_CAMINO`, `MOTIVO_MUSGO`, `TEMA_NANA`, `ACORDES_NANA`). Una pieza nueva puede usar cualquiera de ellas.
- **Ambientes** (`audio/ambiente/`): **brisa** en la hierba, viento entre árboles secos, el fuego de la chimenea, **agua que corre** y la **ciénaga** (gotas, burbujas en el barro y ranas lejanas). En el Kitovu la brisa se oye más cerca de la granja y el viento más lejos; **cuanto más cerca del agua** (estanques, la acequia, el río de los prados), más se oye correr (`scripts/mundo/oido_agua.gd`).
- Los **pájaros** se han quitado (no quedaban naturales). El archivo `pajaros.ogg` se queda guardado para un futuro bioma de selva, pero no suena en ningún sitio.
- **Efectos** (`audio/sonidos/`): el «bip» al pasar cada línea de un diálogo (y al cerrarlo), los menús, la mochila (y su rueda), la pausa, el cetro, las semillas y explosiones, el Latido, recoger cosas, las puertas, los Petrinos, las manchas de Giza, el Corazón y Mzizi; las misiones (nueva, paso, cumplida), meditar y despertar un Arte; el jabalí (gruñido) y Pembe (bramido, escarbar, galope, choque contra un árbol, dolor y su liberación).
- **Cada tarea suena a lo que es**: pescar (lanzar la caña, el corcho que se mece, el tirón al picar, sacarlo o que se escape), arrancar zanahorias (tierra y raicillas), coger las tablas (madera hueca), arreglar la cerca (martillazos), el espantapájaros (paja), las setas luminosas, el mineral (piedra y cristal), entregar un encargo, reconstruir una casa (martillos y sierra) y despertar a un aldeano de piedra. Konokono tiene los suyos (despertar, tragar, escupir, esconderse, rodar, dolor y liberación), la Cosechadora también (arrancar, tolva, tuercas, atascarse, subir la Ira, embestir, chocar, dolor y apagarse) y Maisha sorbe la sopa.
- El **volumen** de la música y de los sonidos se cambia en el menú de pausa (izquierda y derecha) y se guarda.
- El sistema es el autoload **Sonido** (`scripts/globales/sonido.gd`). En `VOLUMEN` está el volumen de cada efecto y en `CON_SILENCIO` cuánto silencio hay entre repeticiones.
- Para rehacer el sonido: `python3 herramientas/crear_sonidos.py` (efectos y ambientes) y `python3 herramientas/componer_musica.py` (música). Si quieres usar tu propia música, guárdala en `.ogg` con el mismo nombre en `audio/musica/`.

## Grabar un vídeo del comienzo

`pruebas/grabar_video.gd` juega solo desde la pantalla de inicio hasta el primer recuerdo. Para grabarlo (con sonido), desde la carpeta del proyecto:

```
godot --path . --resolution 640x360 --fixed-fps 30 --write-movie video.avi res://pruebas/ejecutar.tscn -- grabar_video
```

También se puede grabar la pelea contra la Cosechadora (Maisha juega sola: la atasca con semillas y golpea la caldera, la espera al final del acelerón para el depósito, le tira semillas al techo y esquiva los anillos del corazón con el Latido; dura hasta la pantalla del final):

```
godot --path . --resolution 640x360 --fixed-fps 30 --write-movie pelea.avi res://pruebas/ejecutar.tscn -- grabar_cosechadora
```

## Pruebas automáticas

Se lanzan desde la Terminal, dentro de la carpeta del proyecto (cambia el nombre del final por el de cada prueba):

```
/Applications/Godot.app/Contents/MacOS/Godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_aldea
```

- `pruebas/prueba_sonido.gd` comprueba que estén todas las músicas y efectos, y que suenen cuando toca: el despertar, el «bip» de los diálogos, la brisa de la granja, el silencio entre repeticiones, el agua del estanque, la pesca y las zanahorias, la pausa y el volumen, una mancha de Giza y Mzizi.
- `pruebas/prueba_kitovu.gd` juega el comienzo entero: el despertar lento, la chispa y sus 3 recuerdos, Kuku y la puerta, la noche y el amanecer, el despertar sin cetro, la zona dormida, el susurro del castor, las tres tareas (con la pesca), el cetro y el mapa, el espantapájaros, la mochila, las 3 manchas de práctica con el narrador, la pelea contra Mzizi y el arco hasta los prados y vuelta.
- `pruebas/prueba_guardado.gd` empieza una partida desde el inicio (el diario se abre y la introducción se escribe en él), guarda, pausa, vuelve al inicio, continúa donde lo dejó, comprueba que en plena pelea se guarda el último sitio seguro, que «Nueva partida» pregunta antes de borrar y que un archivo estropeado no rompe nada.
- `pruebas/prueba_encargos.gd` recoge setas y mineral, comprueba que el cetro rebota en la roca y la semilla la rompe, entrega los encargos, ve levantarse las casas, entra en ellas y prueba las recompensas (haces del vigía y cetro templado).
- `pruebas/prueba_sendero.gd` va de los Prados al Sendero del Puente y a la aldea y vuelta, prueba los pretiles y el vado, el eco perdido (con su ilustración), el encargo de Msafiri y el cuaderno de ecos.
- `pruebas/prueba_pasarelas.gd` va de la aldea a Las Pasarelas y a la ciénaga y vuelta, prueba el agua y las tablas, el tramo roto, la rana de piedra (aviso, salto, onda, atontada), el encargo de Korongo (que arregla la pasarela) y el segundo eco.
- `pruebas/prueba_camino_cobrizo.gd` sube de los Prados al Camino Cobrizo y al bosque y vuelta, prueba la peña y el derrumbe, el topo de piedra (bajo tierra, aviso, mordisco, atontado, las raíces que lo sacan), el encargo de Fuko (que despeja la galería) y el tercer eco.
- `pruebas/prueba_orilla_juncos.gd` va de la Ciénaga Quieta a la Orilla de Juncos y vuelta, prueba el cangrejo de herrumbre (rebota de frente, pellizca, expuesto, volcado), el encargo de Kasia, la balsa (rota, arreglada, el viaje de ida y vuelta al banco de arena del eco) el sexto eco y el paso al Embarcadero (cerrado antes del eco, abierto después).
- `pruebas/prueba_embarcadero_junco.gd` sube de la Orilla al Embarcadero Junco tras el sexto eco y prueba el pueblo de barqueros, el transbordador varado, las zonas y secretos, La Travesía cerrada y a Bata (de piedra, despierta al purgar la dársena y se va a su transbordador).
- `pruebas/prueba_lago_espejo.gd` llega al Lago Espejo desde la Cañada, prueba el agua turbia (no se calma y los puentes no se pisan), la pelea contra Kambare (charca, salto con su sombra, ola de barro, varado, chorros de cieno, vencido y la arena purgada), la quietud que vuelve el lago espejo, el puente del reflejo que se enciende y se cruza hasta la isla, Kimya (aparece con el espejo, habla con su ilustración y se desvanece), que andar no lo rompe y un golpe en la orilla sí, y la vuelta a la Cañada.
- `pruebas/prueba_canada_eco.gd` va del Bosque Cobrizo a la Cañada del Eco y vuelta, prueba la peña de la garganta, el murciélago de eco (colgado, vuelo, aviso, la onda que va y vuelve, aturdido, el Latido que deshace la onda), la escala de cuerda (enrollada y descolgada), el encargo de Mbuzi, el quinto eco (con su ilustración) y el paso al Lago Espejo, aún cerrado.
- `pruebas/prueba_senda_surcos.gd` sube de la aldea a la Senda de los Surcos y al Campo Segado y vuelta, prueba la acequia y el foso, el cuervo de óxido (vuelo, raya de aviso, picado, posado, raíces), el encargo de Sungura (que vacía el foso) y el cuarto eco.
- `pruebas/prueba_aldea.gd` cruza el sendero hasta la aldea, habla con Bibi, entra y sale del Gran Árbol, rescata a Pino y comprueba que todo se recuerda al volver.
- `pruebas/prueba_maisha_animaciones.gd` comprueba que existen las 6 animaciones, que Maisha mira hacia donde camina y que, si celebra a mitad de un golpe (al purgar una zona dando cetrazos), no se queda celebrando para siempre.
- `pruebas/prueba_prados.gd` recorre los Prados: agua y árboles que frenan, el secreto del matorral, las piedras-eco y la purga de las tres zonas.
- `pruebas/prueba_combate.gd` recorre una pelea entera: aviso, cierre, golpe, mordisco y rebote, semillas contra el Corazón de Giza, purga, agotamiento, autodaño y vuelta al borde.
- `pruebas/prueba_ropa.gd` comprueba que la ropa se pone y se quita, va delante o detrás según la dirección, sigue a la cabeza al respirar y se refleja bien.
- `pruebas/prueba_misiones.gd` comprueba el diario (misiones que salen y se cumplen con las marcas, contadores, cuál se sigue y que se guarda), la flecha en el mundo y las acciones rápidas (tecla 4, la rueda de Tab).
- `pruebas/prueba_artes.gd` comprueba la Esencia, los costes y efectos de las Artes, que se guardan, y meditar en el Claro de Calma (curar, mantener Acción para despertar un nivel, rasgos).
- `pruebas/prueba_bosque.gd` abre el camino del norte, recorre el Bosque Cobrizo, parte un tronco podrido, prueba al jabalí (embestida, choque, aturdido), rescata a Tawi, vence a Pembe y arregla el puesto (mapa de Raíz).
- `pruebas/prueba_campo.gd` abre las grandes espinas del norte (solo con los dos minijefes libres), recorre el Campo Segado, purga una zona y pelea contra la Cosechadora (capas animadas, rebota, se atasca, cada parte y lo que pasa al romperla, la Ira por etapas, el acelerón, el corazón y sus anillos) hasta que Raíz queda libre y Bibi lo nota.
- `pruebas/prueba_tienda.gd` comprueba los Cristales (misiones, jefes, avisos), la tienda de Tawi (comprar, lo que no se puede pagar, prendas que se ponen solas, el mapa de los secretos, la semilla del olvido que devuelve la Esencia y sube de precio), la ropa desde la mochila, que todo se guarda y la pantalla del final de Raíz.
- `pruebas/prueba_cienaga.gd` abre el camino del este con Bibi, recorre la Ciénaga Quieta (niebla, bayas que vuelven a salir), prueba la babosa y su rastro, rescata a Juncia, vence a Konokono (semilla tragada, mareo, segunda fase), arregla la cocina y toma sopa (con F y desde la mochila).

No hace falta ejecutarlas; sirven para detectar si algo se rompe al cambiar el código.

## Controles ya configurados

| Acción | Teclado | Mando |
| --- | --- | --- |
| Moverse | WASD o flechas | Stick izquierdo o cruceta |
| Acción (hablar, leer…) | Espacio o E | A |
| Mochila | Tab o I (mantener: rueda rápida) | Select (mantener: rueda rápida) |
| Pestañas de la mochila | 1 a 5 (M: mapa) | — |
| Golpe con el cetro | J | X |
| Semilla (explosivo) | K | Y |
| Latido | L o Mayúsculas | B |
| Correr (mantener) | C | LB |
| Cambiar de semilla | Q | RB |
| Tomar sopa | F | Stick derecho (pulsar) |
| Menú | Esc | Start |

(Se pueden cambiar en Godot: Proyecto → Configuración del proyecto → Mapa de entrada.)
