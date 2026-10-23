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
- **Cinemáticas (ilustraciones de la historia)**: `arte/historia/`, como las de los legendarios en Pokémon Platino: mucho más detalladas que el juego, a tamaño de pantalla (**600×256**, sin ampliar) y con su propia **paleta de cinemáticas** (todos los de Raíz, sus tonos intermedios y rampas de cielo, noche, fuego y luz de Giza). Las pinta `herramientas/cinematicas.py` con el pintor `herramientas/pintor.py` (volumen, pelo, humo, fuego, luz y niebla). Para repintarlas: `python3 herramientas/cinematicas.py` (todas, tarda unos 4 minutos; necesita `pip3 install numpy scipy opencv-python`) o `python3 herramientas/cinematicas.py 4_giza` (solo una). En los diálogos se usan con `"historia": [{"imagen": "1_kitovu_antes", "lineas": [...]}, ...]` y `"tras_historia"`. La paleta de cinemáticas tiene ahora **210 colores** (se añadieron rampas de agua honda, verde agua, bruma, malva y nieve para que los degradados de noche y de los recuerdos no se rompan en manchas), y el marco de los recuerdos es un velo suave. Los árboles se pintan con **racimos de hojas con volumen** (`copa_racimos`: cada racimo con su luz, su sombra y su borde de hojitas), no con ruido. Si quieres cambiar una por un dibujo tuyo, guárdalo con el mismo nombre y tamaño (las de 208×120 de antes también funcionan: se ven al doble).

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

**A pantalla completa, como la bolsa de Pokémon Platino** (`documentacion/diario_bolsa.png`): a la izquierda, la **mochila grande** de Maisha con el nombre del bolsillo encima y los **6 bolsillos** debajo (← → para cambiar; la mochila da un saltito, el bolsillo elegido brilla y asoma lo que guarda: un rollo con sello, el cetro, un brote, un mapa, un colgante o una pluma de búho); a la derecha, la **lista grande** (letra de 18, 7 filas); abajo, a lo ancho, la **descripción** con el dibujo grande (en las misiones, de qué va a la izquierda y los pasos y la recompensa a la derecha). El Mapa y las Habilidades ocupan la pantalla entera, con los bolsillos pequeños arriba. Arte: `bolsa_fondo.png` (cielo de noche con tres marcos de filigrana; los mismos rectángulos que `BOLSA`, `LISTA` y `DESC` en `mochila.gd`), `bolsa_fondo_pleno.png` y `mochila.png` (5 dibujos de 160×160), en `pintar_interfaz.py`. Las letras claras llevan contorno oscuro (`draw_string_outline` en `_texto`). En el **mapa de Raíz**, el dibujo se ve ampliado (`MAPA_ESCALA`, 1,32) y cada nombre de lugar va en una etiqueta de pergamino con tinta oscura, escrita aparte y nítida (no se amplía); los contadores de secretos y el alfiler, igual. Ninguna letra del diario baja de 15 (`documentacion/diario_legible.png`). El **mapa del mundo** (↑ ↓ desde el de Raíz), igual: ampliado (`MAPA_MUNDO_ESCALA`, 1,6) y con los nombres en etiquetas de pergamino (`LUGARES_MUNDO`; el dibujo, `mapa_mundo()` de `dibujar_kitovu.py`, ya no lleva rótulos); cuando Raíz es libre, una hojita dorada junto a su nombre (`documentacion/diario_mapa_mundo.png`).

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
| Bestiario | 6 | Todos los enemigos y jefes, con su **rango** (medalla), cuántos llevas vencidos y su ficha; los que aún no has vencido salen como «???» |

← → cambian de pestaña, ↑ ↓ eligen. Los objetos se describen en `scripts/globales/estado.gd` (`OBJETOS`).

### Acciones rápidas

- **Teclas 1 a 6** (y **M** para el mapa): abren la mochila directamente en esa pestaña. Si ya está abierta en esa pestaña, la cierran.
- **Rueda rápida**: mantén pulsado **Tab** (o **Select** en el mando) y aparece una rueda con las 6 pestañas sobre el juego parado. Inclina hacia una (WASD, flechas o el stick) y suelta: se abre esa pestaña. Si sueltas sin elegir, se cierra. Pulsar Tab sin mantener abre la mochila como siempre.

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
3. En el árbol: ← → eligen el Arte, ↑ ↓ miran sus niveles y **mantener Acción** despierta el siguiente nivel (para no gastar Esencia sin querer). Cada nivel cuesta **2, 3, 5, 7, 10 y 14** de Esencia (`COSTES` en `artes.gd`): 41 por rama y 123 las tres. Es caro a propósito: llenarlo todo solo se podrá completando y explorando del todo los mundos 1 y 2 (los precios se ajustarán al final, con la Esencia total del juego).

| Arte | Niveles (1 → 6) |
| --- | --- |
| **Raíz** (la Semilla) | Semilla ligera (cuesta 22) · Raíces largas · **Brote en la cabeza** (cruz +1 casilla) · Semilla ligera II (19) · Mecha corta (1,2 s) · **Hojas y flores** (cruz +1) |
| **Aliento** (Vida, Aliento, Latido) | Pulmón de brisa (110) · Respirar hondo (+15 %) · **Aura suave** (+1 hoja de Vida) · Latido amplio · Golpe que respira · **Cuerpo de brisa** (+1 hoja, 125) |
| Runa · Tierra | Dormidas: despiertan en Sigilia y en Asterhaul |

- **Cada nivel cambia a Maisha por fuera** (`Artes.aspecto()` decide qué se ve; boceto en `documentacion/boceto_artes_grandes.png`). Los niveles 3 y 6 (✦) cambian la silueta:

| Rama | 1 | 2 | 3 ✦ | 4 | 5 | 6 ✦ |
| --- | --- | --- | --- | --- | --- | --- |
| Raíz | Raíces en las piernas | Les brotan hojas (y en las muñecas) | Brote de dos hojas grandes con capullo | Hombreras de corteza | Capa de hojas (se mece) | Corona del bosque y flores |
| Cetro | Cinta verde | Gema más grande | Corteza de roble con aro de cobre | Hojas de cobre | Gema dorada | Cetro del Primer Árbol (dorado, con dos florecillas) |
| Aliento | Bufanda de brisa | Bufanda larga que vuela | Anillo de viento que gira y aura | Remolino bajo los pies | Alitas de brisa | Cuerpo y alas de brisa |

  Las prendas (raíces, brazaletes, hombreras, capa animada, corona, bufandas y los cetros `cetro_0`…`cetro_6` de 16×21) las dibuja `herramientas/dibujar_prendas.py` y se ponen con la ropa por capas (`ropa_maisha.vestir_artes`; una prenda con `"fotogramas"` se anima sola). Solo ocupan las zonas libres: **lo que Maisha se pone desde la mochila manda** (con el sombrero de paja no se ve la corona del bosque). El golpe gira el cetro que se lleva. Lo vivo (brote, flores, aura, anillo, remolino, alas, brisa) está en `rasgos_maisha.gd`, sutil y sin brillitos sueltos (con todo despierto, Maisha no debe verse cargada); el cetro es fino en todas las fases; lo de detrás (aura, mitad de atrás de los anillos, alas) va en un nodo por debajo de Maisha.
- **Un cetro por mundo**: el Cetro-rama sirve para los mundos 1 y 2; al acabar el 2 Maisha recibirá un cetro nuevo y más poderoso (de piedra, runas y cristal en el boceto; se diseñará más adelante) que se vuelve a subir desde 0.
- **Maisha en grande en Habilidades**: a la izquierda del árbol, sobre un tocón, Maisha a tamaño ×4 se da la vuelta despacio (frente, lado, espalda). Sobre un nivel **sin despertar** se ve **cómo quedaría** («Con Cetro III», halo del color de la rama y lo que cambia debajo); **F** alterna entre ahora y después. Es la misma Maisha del juego (sus animaciones, `ropa_maisha.gd` y `rasgos_maisha.gd` con `niveles` de prueba).
- En todo Raíz se consiguen 43 de Esencia (y 2 más en las islas de la ciénaga, más adelante); antes del jefe final, unas 36. Con los precios nuevos, el mundo 1 completo llega a mitad de camino (unos 3 niveles por rama): hay que elegir. Las Artes de Runa y Tierra despiertan en otros mundos.
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

## La luz: relieve, día y noche (el «2.5D»)

Todo es visual: las colisiones y el movimiento siguen siendo 2D planos y no saben nada de esto (`documentacion/luz_2_5d.png`).

| Qué | Cómo |
| --- | --- |
| Relieve | `herramientas/relieve.py --todo` calcula el «mapa de normales» de cada dibujo del mundo, de los aldeanos y de las criaturas de Raíz (`<dibujo>_n.png`: hacia dónde mira cada píxel) con un abombado a varias escalas más la claridad del pixel art. Los suelos no (su relieve es ruido y ocupaba 40 MB). Hay que relanzarlo al repintar un dibujo |
| En el juego | `scripts/mundo/relieve.gd` (lo pone `escena_mundo.gd` en todas las escenas): cambia cada dibujo con relieve por una CanvasTexture y pone la luz |
| Hora del día | El autoload **Reloj** (`scripts/globales/reloj.gd`): un día dura 16 minutos (día, atardecer, noche y amanecer) y se guarda con la partida. No corre hasta llegar a Cuna de Musgo (el Kitovu del principio es de día) |
| Exteriores | De día, el sol gira suavemente de este a oeste; al atardecer, luz rosada y sombras más largas (`sombra.gd`); de noche, luna azulada y todo oscuro. Cada bioma aporta un matiz suave (`BIOMAS`: cálido en el bosque, verdoso en la ciénaga, frío en la cumbre). Los rayos de sol (`luz_sol.gd`) llevan motas de polvo en el haz, se vuelven naranjas al atardecer y se apagan de noche |
| Luces de noche | Ventanas, faroles y fuegos de 17 edificios (tabla `LUCES`, incluidos los del Kitovu; las ruinas no se encienden), los faroles de la aldea y las hogueras. Alrededor de Maisha, una luz suave para jugar de noche. Las casas abandonadas (Nungu, granero, molino) quedan a oscuras |
| Escenas con su penumbra | Cuevas, Gruta, el amanecer del Kitovu y la casa de Shamba: el ciclo se aparta mientras dure y mandan sus luces (que también ven el relieve) |
| Magia | `Relieve.destello(...)`: fogonazo naranja al estallar una semilla, ámbar con el Latido y verde con el golpe; reutiliza la textura radial en caché y se nota más cuanto más oscuro está (`Reloj.oscuridad`) |

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
- Con el transbordador a flote, en la punta del muelle se **sube** (Bata: «¡Arriba!») y se zarpa a **La Travesía**. La puerta del norte por tierra sigue cerrada (`travesia_abierta`): río arriba se va en barca.
- Música propia: **«Canción de barqueros»** (`embarcadero` en `componer_musica.py`), una canción de trabajo en re dórico: la flauta pregunta y las voces graves contestan, con el balafón y el tambor al ritmo de los remos, la cuerda que cruje y la campana del muelle.

### La Travesía
- Música propia: «Río arriba» (`componer_musica.py travesia`): el tema de la linterna (la despedida de Mauti), decidido y en re mayor, con la pértiga de Bata marcando cada compás y la corriente por debajo.

Escena `escenas/mundo/la_travesia.tscn` (mapa de 48×170, de sur a norte, `construir_mapa.py la_travesia --crear`, `crear_travesia`). **No se anda: se viaja en el transbordador** (`scripts/mundo/travesia/viaje.gd`). Se sube en la punta del muelle del Embarcadero cuando el transbordador ya flota.
- La barca (`cubierta.png`, vista desde arriba: tablas, borda con postes y cuerda, caseta con tejado de paja, campana, farol, cajas y sacos) sube sola por el centro del río, a 34 píxeles por segundo, con su estela. Maisha va en la cubierta: se puede mover por ella pero no salirse (en este mapa el agua no es sólida: `agua_solida = false` en el nodo Region). Bata, en la popa, clava la pértiga al ritmo de la barca.
- Las orillas cambian por el camino: juncos y sauces abajo, bosque cerrado en medio, rocas arriba.
- **Lo que sale del agua** (`OLEADAS` en `viaje.gd`, capturas `documentacion/travesia_oleada.png`): en cuatro momentos del viaje Bata grita y salen cangrejos de herrumbre que **trepan por la borda** (van encima de la barca, como Maisha) y, en la segunda mitad, **anguilas de óxido** (`scripts/enemigos/anguila.gd`, enemigo nuevo, `herramientas/pintar_travesia.py`): saltan de un lado al otro de la cubierta en arco (una sombra avisa); si caen encima de Maisha, daño; un golpe de cetro en el aire las tumba en la cubierta, aturdidas, y entonces el cetro les quita vida. Tras tres saltos se van. Si Maisha cae, vuelve en la cubierta.
- **La isla del séptimo eco** (a media subida, rodeada de agua; `documentacion/travesia_isla.png`): la barca se arrima y se para, Bata tiende una **pasarela** y Maisha puede bajar (a la isla y a la cubierta; nunca al agua). El **séptimo eco** (ilustración `19_eco_travesia`): Mauti llega de noche en su barca sin remos y deja su **hoja de cobre** debajo de una piedra plana para Maisha («Si subes a buscarme, tráemela»). Tras el eco aparece la **hoja de Mauti** (objeto clave `hoja_mauti`, icono 25.º de `objetos.png`). Al volver a bordo, Bata sigue río arriba.
- Arriba atraca junto al **muelle de piedra** de la Gruta de las Raíces: Bata lo anuncia, Maisha baja (marca `travesia_hecha`) y el agua vuelve a ser sólida. Desde la barca se puede volver al Embarcadero. El camino de la Gruta sube del muelle hacia el norte: las raíces de la boca solo se apartan con la **hoja de Mauti** (`cerrada:hoja_mauti`).
- Música: de momento la barcarola de la Orilla. Prueba: `pruebas/prueba_la_travesia.gd`.
- Falta: la música propia del viaje.

## Gruta de las Raíces
- Música propia: «Las raíces que duermen» (`gruta`): un bordón grave, las raíces que roncan (respiraciones lentas), gotas en los charcos y el tema de Maisha en menor, de puntillas.

Escena `escenas/mundo/gruta_raices.tscn` (mapa de 64×84, de sur a norte, `construir_mapa.py gruta_raices --crear`, `crear_gruta`; boceto `documentacion/boceto_gruta_raices.png`). **Una cueva por dentro**: el suelo se pinta aparte (`pintar_gruta` en `pintar_suelo.py`: tierra oscura con guijarros, raíces finas y algún charco; la roca, «0», maciza y con la cara iluminada junto al suelo). Se entra desde el muelle de piedra de La Travesía con la hoja de Mauti.
- **A oscuras** (`scripts/mundo/gruta/oscuridad.gd`, capturas `documentacion/gruta_capturas.png`): un CanvasModulate deja todo en penumbra; alumbran Maisha (una luz que respira), las **semillas dormidas** de los nichos (`ŝ`, `semilla_dormida.png`, laten verdes) y las **huellas lilas de Mauti** (`huella.png`), que van de la entrada al fondo. Sin rayos de sol (`rayos_de_sol = false` en el Ambiente).
- **El pasillo de las raíces dormidas** (sigilo; `scripts/mundo/gruta/raiz_dormida.gd`, `raiz_dormida.png`, capturas `documentacion/gruta_pasillo.png`): tres raíces enormes atravesadas (`ŕ`) duermen y roncan («zzz»). Andando se pasa por encima. El ruido cerca (correr, golpear, una semilla o el Latido) las inquieta: abren un ojo violeta que da luz (el aviso); si el ruido sigue, se levantan y azotan a lo largo del pasillo (daño y empujón); luego se vuelven a dormir. Sonidos `raiz_ronca`, `raiz_despierta`, `raiz_azota`.
- La **maraña de raíces** (`ř`, `raiz_tapon.png`) tapa el atajo del pasillo al fondo hasta que despierte el Guardián (`gruta_guardian`).
- Salas: el vestíbulo de las semillas, el pasillo de las raíces dormidas, el santuario de corteza (`ą`, el escudo), la galería de las espinas (`ę`) y el fondo, con un atajo tapado por raíces (`ř`) y dos secretos. Al norte, el Sendero Olvidado (cerrado: `sendero_abierto`).
- Arte: `herramientas/pintar_gruta.py`. Música: de momento la del Lago. Prueba: `pruebas/prueba_gruta_raices.gd`.
- **El santuario de corteza** (`ą`, `scripts/mundo/gruta/altar_corteza.gd`, `altar_corteza.png`): un tocón enorme del Primer Árbol con un escudo de corteza encima, que brilla. Al tocarlo, la corteza se enrosca en el cetro: **Escudo de corteza** (marca `escudo_corteza`).
- **El escudo** (en `maisha.gd`): tocar J golpea; **mantener J** (`ESCUDO_MANTENER`, 0,25 s) levanta el escudo (`escudo.png`, delante de Maisha). Para todo lo que viene de frente (no las explosiones): suena «clinc» y no hace daño. Con él, Maisha anda a la mitad y no golpea. Está en la pestaña Habilidades del diario.
- **La galería de las espinas** (`ę`): cuatro **espinos de Giza** (`scripts/enemigos/espino.gd`, `espino.png`, enemigo nuevo) que, con Maisha cerca, se hinchan (su capullo violeta da luz) y escupen **espinas** (`espina.gd`) cada 1,7 s. El cetro rebota; una semilla los deshace (marca `espino/x,y`). Capturas: `documentacion/gruta_escudo.png`.
- **El Guardián de la Gruta** (jefe del fondo; `scripts/enemigos/guardian.gd`, dibujo `herramientas/dibujar_guardian.py`, capturas `documentacion/guardian_capturas.png`): un ciervo enorme y viejo, mitad animal y mitad raíz, al que Giza le ha puesto una **máscara de hueso** (su pesadilla) que lo mueve dormido como a una **marioneta** (hilos violetas que bajan del techo). Tiene luz propia (violeta; dorada al despertar). **Embestida**: escarba (una raya marca hacia dónde) y carga; si choca contra la pared queda **aturdido** con la máscara torcida (cetro 1, semilla 2: se agrieta). **Ola de raíces**: se alza y pisa fuerte, y una ola de raíces-látigo avanza por el suelo; **el escudo, de frente, la para**. Fase 2: al aturdirse llama a dos Petrinos. Fase 3: más deprisa y a veces dos embestidas. Al vencerlo, la máscara estalla: el Guardián despierta, se queda en la sala y cuenta que **Mauti durmió a su lado y siguió por el Sendero Olvidado** hacia las Ruinas del Primer Árbol, que solo se abre con **los nueve ecos** (marca `gruta_guardian`; la maraña del atajo se aparta). Música «La pesadilla del Guardián» (`jefe_guardian`) y sonidos `guardian_brama`, `guardian_carga`, `mascara_cruje`, `mascara_rompe`.

### Los ecos perdidos (el misterio de Raíz)

Piedras altas con una espiral tallada (`scripts/mundo/objetos/eco_perdido.gd`). Al acercarse brillan y sueltan motas de luz; con **Acción**, el mundo se tiñe de verde-agua y se oye un recuerdo con su ilustración (conversación `eco_<mapa>` en `datos/dialogos/raiz.json`). Cada uno deja la marca `eco/<mapa>`. Hay **9** en todo Raíz (ocho por los caminos y el del Lago Espejo, que solo se ve en el reflejo): juntos abrirán el Sendero Olvidado hacia las Ruinas del Primer Árbol. Misión «Los ecos perdidos» en el diario.
- El primer recuerdo: `arte/historia/12_eco_puente.png` (`herramientas/cinematicas_sendero.py`): el puente a medio hacer y el Primer Árbol dorado al fondo.
- El segundo (Las Pasarelas): `13_eco_pasarelas.png`: una noche de luna; bajo el agua, las raíces doradas del Primer Árbol y **Kimya, el Silencio**, deslizándose entre ellas.
- El tercero (Camino Cobrizo): `14_eco_cobrizo.png`: una tarde de otoño bajo un árbol de hojas de cobre; Maisha y **Mauti** (plateada y lila, con una hoja seca en lo alto) hablan de por qué caen las hojas: «Tú y yo somos el mismo árbol».
- El cuarto (Senda de los Surcos): `15_eco_surcos.png`: la fiesta de la última siega, de noche, con farolillos, gavillas y una hoguera; Maisha y Mauti bailan de la mano. «Lo que se siembra, Maisha lo despierta. Lo que se siega, Mauti lo guarda.» Y una pregunta que da miedo: «¿Y si un día alguien quisiera que nada se segara nunca?»
- El quinto (Cañada del Eco): `16_eco_canada.png`: un atardecer en la garganta. En la cornisa, Maisha y Mauti gritan sus nombres y la peña se los devuelve; **Kimya** flota sobre el arroyo quieto y no grita: «El Silencio no tiene eco. Por eso puedo oíros a los dos.» Solo el agua refleja a Kimya, y eso apunta al Lago Espejo.
- El sexto (Orilla de Juncos): `18_eco_orilla.png`: **la despedida**. Una noche de luna en el río ancho: Mauti se aleja río arriba en una barca pequeña, con su luz lila, y Maisha se queda en la playa con una linterna encendida. «Déjala encendida aquí, en la orilla. Así sabré por dónde volver.» Mauti iba a hablar con quien no quería que nada se segara nunca, río arriba, hacia el norte. Nadie volvió a buscar la linterna.
- El séptimo (La Travesía): `19_eco_travesia.png`: una noche de niebla junto a la Gruta de las Raíces (la peña con raíces enormes que abrazan su boca). Mauti, de rodillas en la isla del río, deja su hoja de cobre bajo una piedra plana: «Si subes a buscarme, tráemela. Y no te asustes de lo que oigas en la Gruta: las raíces hablan muy alto cuando duermen.»
- El octavo (la cueva de las setas, bajo el Paso de Piedra): `20_eco_cueva.png`: Kimya y sus setas, que se comen lo que cae y se lo devuelven a la tierra. «¿Y si una seta quisiera mandar, en vez de servir?»
- El **noveno** (Lago Espejo): **la voz del Silencio**. La piedra **solo existe en el reflejo**: aparece, plateada, en lo alto de la isla de Kimya cuando el lago se queda quieto (`solo_reflejo` en `eco_perdido.gd`), y se desvanece si el agua tiembla. Al escucharla **todo se calla** (música, ambiente y efectos) mientras dura el recuerdo, `21_eco_lago.png`: arriba solo hay noche, pero en el agua, del revés, brillan el Primer Árbol, Kimya y nueve espirales. Kimya cuenta por qué existen los ecos (el Primer Árbol guardó lo que recordaba en ocho piedras; la voz del Silencio no cabía en una) y avisa de quien vive en las Ruinas: «Quien no soporta que algo se acabe es porque lo quiso muchísimo».
- **Las nueve voces**: al oír el último eco (en el orden que sea) se pone `nueve_ecos`; el Guardián de la Gruta, al hablarle, aparta las raíces del fondo (`sendero_abierto`). La misión «Los ecos perdidos» tiene ese segundo paso. Mientras la escena del Sendero Olvidado no exista, su puerta se porta como cerrada (Maisha piensa que la niebla aún no deja ver dónde pisar): `puerta.gd` no deja pasar a escenas que no existen (`Estado.existe_escena`).

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

La pantalla del **final del mundo** (`scripts/interfaz/fin_mundo.gd`; se le cambian la ilustración, el título, el subtítulo, el pie y los mapas que cuenta) sale dos veces:
- Al vencer a la **Cosechadora**: «Raíz respira · Pero en el norte, algo sigue enfermo · Sigue los ecos hacia el norte...» (Giza ya no lo cubre todo, pero el Primer Árbol sigue enfermo).
- Al curar al **Primer Árbol** (el final de verdad): la ilustración `23_arbol_libre`, «Raíz es libre · Fin del primer mundo · Continuará en Sigilia...», con lo conseguido en todo Raíz (tiempo, zonas, aldeanos, secretos, misiones, Esencia y Cristales). Acción para seguir jugando.

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

En el PC de Windows (PowerShell), con el Godot de consola:

```
& "C:\Users\iamin\Godot\extraido\Godot_v4.7.2-stable_win64_console.exe" --headless --path . res://pruebas/ejecutar.tscn -- prueba_aldea
```

Los modelos 3D (`.glb`) se generan con **Blender 5.2.3 LTS** (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`); es la única versión del pipeline.

### Modelos 3D (Blender)

Cada modelo se programa en `herramientas/blender/` a partir de las fichas de `documentacion/referencias_visuales_3d/` y se exporta a `modelos/`. Para rehacer uno (y, si se quiere, sacar vistas renderizadas para revisarlo):

```
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P herramientas/blender/modelar_casa_granja.py -- --vistas <carpeta>
```

| Modelo | Programa | Archivo | Nodos |
| --- | --- | --- | --- |
| Casa Granja de Mzee Shamba | `modelar_casa_granja.py` | `modelos/entorno/casa_granja.glb` | `CasaGranja`, `RuedaMolino` (gira con `rotate_x`), `AguaGranja`, `Marcador_Humo` |
| La misma casa en ruina (antes de purificar el Kitovu) | `modelar_casa_granja.py -- --ruina` | `modelos/entorno/casa_granja_ruina.glb` | Los mismos nodos menos `Marcador_Humo`; la rueda está atascada (no gira). Tejado roto, ceniza, telarañas, canaleta partida, podredumbre y luces apagadas |
| Mzee Shamba (castor bípedo de 1,45 m, sobre la malla base de Blender Studio) | `modelar_mzee_shamba.py` | `modelos/personajes/mzee_shamba.glb` | 30 huesos (con `jaw`, `beard_root`, `hat_bone`, bigotes y cola); `Baston` anclado a `hand_R` y `Cuenco` a su hueso (escala 0 salvo al ofrecerlo). Animaciones: `idle_labranza`, `hablar_afable`, `cavar_tierra`, `ofrecer_cuenco` |
| Petrino de Giza (jabalí de piedra con grietas violetas, 1,85 × 1,15 m) | `modelar_petrino_giza.py` | `modelos/enemigos/petrino_giza.glb` | Bloques de basalto rígidos a los huesos de la ficha (`Pelvis`…`Head`, `Jaw_Tusk`, patas), 6 nodos `Shards_Break_*`. Animaciones: `reposo`, `caminar`, `embestida`, `aturdido`, `muerte_fractura`; las pone `scripts/enemigos/petrino_3d.gd` según la fase |
| Maisha (1,70 m sobre la malla base `GEO-body_male_stylized`, sin astas, con los Tatuajes de la Memoria) | `modelar_maisha.py` | `modelos/personajes/maisha.glb` (+ `maisha_tatuajes_mascara.png`, 5120×1024: las 5 baldosas UV de la malla base en fila) | Esqueleto de 27 huesos con los nombres de la ficha; mallas `Maisha_Cuerpo` (descalza, como la hoja canónica), `Maisha_Ojos`, `Maisha_Pelo` (melena por los hombros), `Maisha_Tunica` (con mangas al codo, escote en V y la faja verde cruzada), `Maisha_Ropa` (falda con picos, cinturón con bolsas y calabazas, corazón), `Maisha_Capa` (capa doble verde y parda con capucha caída; se puede ocultar) y el `Cetro` anclado a `hand_R`. Animaciones: `reposo`, `caminar_atento`, `correr`, `golpe_cetro`, `idle_mirar_tatuajes`, `eco_despertar`, `esquivar_rodando`, `saltar`, `aterrizar`, `trepar` |
| Atrezo del Huerto Asfixiado (carretilla volcada, pala clavada, espantapájaros, pozo) | `modelar_props_kitovu.py` | `modelos/entorno/carro_madera.glb`, `pala_oxidada.glb` (origen en el suelo, hoja medio enterrada), `espantapajaros.glb`, `pozo_antiguo.glb` | El espantapájaros lleva esqueleto (`poste`, `torso`, `cabeza`, `brazo_L/R`) y animaciones `reposo` y `golpeado`; el resto es estático |
| Cráter del Despertar, árbol seco, Portal de Raíz y nudo de corrupción | `modelar_crater_y_portal.py` | `modelos/entorno/crater_kitovu.glb` (el cuenco baja 0,45 m bajo el suelo), `arbol_seco.glb`, `portal_raiz.glb`, `nudo_corrupcion.glb` | Glifos y vetas del cráter y savia del portal en materiales emisivos propios. El nudo lleva esqueleto (`bulbo`, `cristales`, `zarcillos_L/R`), animaciones `latido` y `purificar` y el suelo de ceniza en el nodo `SueloMarchito` |

**Maisha en el juego** (`scripts/personajes/maisha_3d.gd`): elige sola la animación (quieta, caminando, corriendo, golpeando; a los 8 s quieta se mira los tatuajes) y ajusta su velocidad a la del paso para que los pies no patinen. Al esquivar da una voltereta acelerada para que dure lo mismo que el impulso (0,38 s); en el aire pone `saltar` (se agacha, se impulsa y se queda en la pose de vuelo) y al tocar el suelo, `aterrizar`. `trepar` (en bucle) queda lista para cuando haya escalada. Los tatuajes empiezan dormidos: `despertar_memoria(0..1)` los enciende y `recuperar_eco()` hace la animación del despertar y suma un noveno de brillo. Las vistas de revisión están en `documentacion/referencias_visuales_3d/personajes/vistas_maisha/`.

### Trabajo en pareja (Claude y Gemini)

Los dos agentes trabajan a la vez. Cada uno manda en sus carpetas y cuenta sus cambios en una línea del **Diario** de `documentacion/coordinacion.md`; lo que necesita del otro va en **Pedidos**. Para ver qué ha hecho el otro desde la última vez:

```
python herramientas/novedades.py claude     # lo que ha hecho Gemini
python herramientas/novedades.py gemini     # lo que ha hecho Claude
```

Los commits llevan delante `[claude]` o `[gemini]`.

- `pruebas/prueba_petrino_3d.gd` carga al Petrino 3D y comprueba sus huesos, los puntos de fragmentos, sus 5 animaciones y que la IA pone la de cada fase (quieto, embestida, aturdido y la muerte por fractura).
- `pruebas/prueba_shamba_3d.gd` carga a Mzee Shamba en 3D y comprueba sus huesos, que el bastón y el cuenco van anclados a su sitio, sus 4 animaciones y su altura.
- `pruebas/prueba_maisha_3d.gd` carga a Maisha en 3D y comprueba el esqueleto, el cetro en la mano, las 6 animaciones, qué animación suena al estar quieta, caminar, correr y golpear, y que los tatuajes empiezan dormidos y se encienden con cada Eco.
- `pruebas/prueba_recursos_3d.gd` revisa todas las escenas y falla si alguna pide un archivo que no existe (un `.glb`, un sonido, un script...). Pásala antes de subir cualquier cambio en `escenas/`: así Claude y Gemini no rompen `main` al sincronizarse.
- `pruebas/prueba_sonido.gd` comprueba que estén todas las músicas y efectos, y que suenen cuando toca: el despertar, el «bip» de los diálogos, la brisa de la granja, el silencio entre repeticiones, el agua del estanque, la pesca y las zanahorias, la pausa y el volumen, una mancha de Giza y Mzizi.
- `pruebas/prueba_kitovu.gd` juega el comienzo entero: el despertar lento, la chispa y sus 3 recuerdos, Kuku y la puerta, la noche y el amanecer, el despertar sin cetro, la zona dormida, el susurro del castor, las tres tareas (con la pesca), el cetro y el mapa, el espantapájaros, la mochila, las 3 manchas de práctica con el narrador, la pelea contra Mzizi y el arco hasta los prados y vuelta.
- `pruebas/prueba_guardado.gd` empieza una partida desde el inicio (el diario se abre y la introducción se escribe en él), guarda, pausa, vuelve al inicio, continúa donde lo dejó, comprueba que en plena pelea se guarda el último sitio seguro, que «Nueva partida» pregunta antes de borrar y que un archivo estropeado no rompe nada.
- `pruebas/prueba_encargos.gd` recoge setas y mineral, comprueba que el cetro rebota en la roca y la semilla la rompe, entrega los encargos, ve levantarse las casas, entra en ellas y prueba las recompensas (haces del vigía y cetro templado).
- `pruebas/prueba_hd2d.gd` enciende el HD-2D con H, comprueba que cada dibujo tiene su gemelo 3D, que la interfaz sigue, que Maisha anda igual y su gemelo la sigue, que las peñas se levantan, que se recuerda al cambiar de escena y que al apagarlo vuelve el 2D.
- `pruebas/prueba_estanterias.gd` llega a Las Estanterías Colgantes, comprueba que los huecos no se pisan, que las escaleras rodantes se cruzan tendidas y no recogidas y que si se van con Maisha encima cae y pierde una hoja, que el tintero rabioso embiste, hace daño, deja manchas y cuenta en el Bestiario, que la cerradura de tinta se derrite y guarda la ficha de Daftari, y que Daftari recupera su nombre en Maandiko.
- `pruebas/prueba_maandiko.gd` llega a Maandiko desde el Paso, comprueba la música, la plaza, el Archivo, las casas, los puestos y el taller, los vecinos (Kalamu, Mauti, Wino, Taa y los escribas en blanco), que Kalamu da el trozo del norte del mapa y cumple la misión, que los charcos de Tinta Quieta de las salidas se derriten con tres sigilos, que entonces Wino abre su tienda (pluma, tinta viva y raquetas; la pluma abarata el sigilo) y que con todos los faroles encendidos Taa da 3 Cristales.
- `pruebas/prueba_paso_escarcha.gd` comprueba el paso del norte de las Ruinas (cerrado hasta curar al árbol), llega al Paso de la Escarcha, prueba la nieve honda (frena, no deja correr, deja surcos que ya no frenan), la ventisca (empuja en medio del valle, no detrás de una estela, y se apaga al pasar la racha), a Taa en blanco, la ficha en la nieve honda, que al dársela recupera su nombre y enseña el sigilo de fuego, el sigilo (sin aprender no sale; gasta Aliento; espera) que enciende un farol, el abrigo del farol (ni viento ni nieve honda), que revivir lo quita todo, las páginas sueltas (atacan y el fuego las quema; cuentan en el Bestiario), la Puerta Sellada (no se rodea; tres sigilos la abren), que la misión se cumple y que la puerta a Maandiko aún no deja pasar.
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
- `pruebas/prueba_combate.gd` recorre una pelea entera: aviso, cierre, golpe, mordisco y rebote, semillas contra el Corazón de Giza, purga, agotamiento, autodaño y vuelta al borde. También comprueba que nada deja a Maisha lenta para siempre (el fallo de K + L): la cámara lenta olvidada se quita sola, el entumecimiento se recupera y al revivir no queda nada que frene.
- `pruebas/prueba_ropa.gd` comprueba que la ropa se pone y se quita, va delante o detrás según la dirección, sigue a la cabeza al respirar y se refleja bien.
- `pruebas/prueba_misiones.gd` comprueba el diario (misiones que salen y se cumplen con las marcas, contadores, cuál se sigue y que se guarda), la flecha en el mundo y las acciones rápidas (tecla 4, la rueda de Tab).
- `pruebas/prueba_ruinas.gd` comprueba el final de Raíz: la llegada, la pelea (despertar las piedras manteniendo Acción, el corazón de Giza a golpes), el final (Mauti libre, la semilla, la pantalla del final), volver después y la salida.
- `pruebas/prueba_sendero_olvidado.gd` comprueba los Quietos (mirados no se mueven, de espaldas se acercan, tres golpes los rompen), los braseros (una semilla los enciende y se quedan encendidos), la escarcha (quieta se congela y pierde una hoja; andando o junto al fuego se le pasa), las estatuas, la misión y las puertas.
- `pruebas/prueba_luz.gd` comprueba el reloj del día (no corre hasta Cuna de Musgo, el amanecer sin saltos), el relieve de los dibujos, las ventanas que se encienden de noche y que las cuevas mantienen su propia penumbra.
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
| Sigilo (Sigilia: cuando se aprende) | U | RB |
| Cambiar de semilla | Q | — |
| Tomar sopa | F | Stick derecho (pulsar) |
| Menú | Esc | Start |

(Se pueden cambiar en Godot: Proyecto → Configuración del proyecto → Mapa de entrada.)


## Los hechiceros de Giza y el Bestiario

Dos enemigos nuevos que no pelean cuerpo a cuerpo (`documentacion/boceto_hechiceros.png`; arte en `herramientas/pintar_hechiceros.py` → `arte/mundos/raiz/hechiceros/`):

| Enemigo | Dónde | Cómo pelea |
| --- | --- | --- |
| **Bundi, el búho-mago** (`bundi.gd`) | Bosque Cobrizo, Cañada del Eco | Guarda las distancias: si Maisha se acerca, **se esfuma en plumas** y aparece en otro sitio. **Conjura** (alza el bastón, runas en el suelo) y lanza una **bola de Giza** que persigue (`orbe_giza.gd`). El Latido la deshace; el **escudo** (J mantenida, de frente) **se la devuelve**: si le da, se queda **atontado** y no puede irse. 3 de vida |
| **Buibui, la araña-bruja** (`buibui.gd`) | Camino Cobrizo, Campo Segado | Se queda en su sitio y cada 4,5 s **invoca** (el nido brilla) 2 **bichos de óxido** (`mende.gd`, mueren de un golpe), hasta 4 a la vez. Muerde si te pegas. Una **semilla le sella el nido** con raíces y ya no invoca. 4 de vida |

Los números están en `reglas_combate.gd` (`BUNDI_*`, `ORBE_*`, `BUIBUI_*`, `MENDE_*`). Sonidos: `bundi_ulula`, `bundi_conjura`, `bundi_lanza`, `bundi_esfuma`, `orbe_rebota`, `buibui_invoca`, `mende_corre`, `mende_muere` y `rango_nuevo`.

**El Bestiario** (`scripts/globales/bestiario.gd`, autoload `Bestiario`) cuenta los enemigos que vence Maisha y les da un **rango** para los logros:

| Rango | Enemigos | Jefes | Premio |
| --- | --- | --- | --- |
| 🥉 Bronce | 10 vencidos (los bichos de la bruja, 20) | Vencerlo | La ficha completa |
| 🥈 Plata | 30 (bichos, 60) | Vencerlo dejándote dar 3 veces o menos | 2 cristales y el **secreto** del enemigo |
| 🥇 Oro | 60 (bichos, 120) | Vencerlo sin que te den | 4 cristales |

- Cada enemigo llama a `Bestiario.vencido(tipo, self)` al morir; los que se desmoronan con la purga de una zona no cuentan (meta `sin_contar`). La zona de un jefe avisa al empezar la pelea y cuenta los golpes que se lleva Maisha.
- Las cuentas van en la partida (`Estado.extra["bestiario"]`) y los rangos son marcas `rango/<bronce|plata|oro>/<tipo>` (los cristales, en `datos/tienda.json`). Los jefes vencidos antes del Bestiario cuentan como bronce.
- Al subir de rango sale un aviso («Bestiario: rango de plata»). La ficha de cada uno, con su dibujo, está en el 6.º bolsillo del diario.
- **El rescoldo de Giza** (`scripts/mundo/objetos/rescoldo.gd`): en la arena de cada jefe vencido queda un anillo de piedras con una llama violeta y dorada, mientras no tengas su oro. Al tocarlo (Acción), la zona revive el **eco del jefe** (`zona_corrupta.revivir_eco`): Maisha se aparta al borde, suben las espinas y el jefe despierta. Ganar el eco solo cuenta para el Bestiario (no vuelve a purgar la región ni repite la historia); si Maisha cae dentro, el eco se deshace sin más y el rescoldo vuelve. Si el jefe se queda en la sala (el Guardián), se aparta mientras dura el eco.
- Prueba: `prueba_hechiceros`.


## Paso de Piedra (parte 1: el paso y la casa abandonada)

Escena `escenas/mundo/paso_piedra.tscn` (mapa de 150×48 casillas, de oeste a este: `construir_mapa.py paso_piedra --crear`, `crear_paso`), entre el **Campo Segado** (nueva salida del este del campo) y la **Gruta de las Raíces**. Capturas: `documentacion/paso_piedra_capturas.png`; bocetos de la historia: `documentacion/boceto_paso_piedra.png`. Música propia: «La casa del observatorio» (`componer_musica.py paso`): una caja de música que pregunta y responde, el tic-tac de un reloj que nadie ha parado, el viento del paso y la flauta que contesta.

- Un paso de montaña entre paredes de peña (con mesetas encima, como la Cañada). La hierba seca del campo se vuelve gravilla gris hacia la **cantera** vieja del este (bloques cortados `ĉ`, con marcas de cincel y cuñas). Una zona corrupta en el ensanche del sur (petrinos, búhos-mago y arañas-bruja) y un secreto tras un matorral en la cantera.
- **La casa de Nungu** (`ĥ`, `herramientas/pintar_paso.py`): una casa de piedra abandonada con el tejado de lajas hundido, un observatorio con cúpula de cobre y catalejo, ventanas tapiadas, la puerta entornada, hiedra seca y cajas de muestras de roca. Su puerta (`ď`) lleva dentro (`escenas/interiores/casa_nungu.tscn`, `casa_nungu.gd`): el taller de un científico (estanterías con piedras etiquetadas, una pizarra con la veta violeta, la mesa con el microscopio y una carta a medio escribir) y, al fondo, **el armario** (`scripts/mundo/paso/armario.gd`), cerrado con una cerradura que lleva la marca de Corteza. Con la llave (`llave_nungu`) se abre (`armario_abierto`): dentro, una escalera que baja hacia una luz violeta.
- Misión de historia **«La casa del Paso de Piedra»**: entrar en la casa → buscar pistas (la carta: Nungu le dejó la llave de repuesto a Corteza) → preguntar a Corteza → buscar la llave en su taller → abrir el armario.
- **La llave** (parte 2): Corteza se acuerda de Nungu («me tuvo tres semanas con la cerradura») pero no de dónde guardó la llave (`corteza_busca_llave`). En su taller, las herramientas no la tienen; en el banco hay un cajón vacío con la etiqueta «LLAVE DE NUNGU. NO PERDER» y polvo de carbón; y en el **barril del carbón** está, negra de hollín (`llave_nungu`, objeto clave con icono, el 26.º de `objetos.png`). Al enseñársela, Corteza avisa de que Nungu hablaba de «cosas que crecían bajo tierra».
- Al este, una **maraña de raíces** tapa el paso a la Gruta (puerta `cerrada:gruta_guardian`, espinas `!`). Por dentro de la Gruta, el santuario tiene un túnel al oeste tapado por la misma maraña que el atajo: las dos se apartan al despertar al Guardián (un atajo de vuelta). Cada puerta cerrada puede tener su propio texto: `paso_cerrado_<destino>_desde_<mapa>`.
- Prueba: `prueba_paso_piedra`.

### La cueva de las setas (Paso de Piedra, parte 3)
- Música propia: «Lo que cae y vuelve» (`setas`): una kalimba que da vueltas, burbujitas de esporas que suben y, al final, la frase de Kimya.

Escena `escenas/mundo/cueva_setas.tscn` (mapa de 56×64, de norte a sur: `construir_mapa.py cueva_setas --crear`, `crear_cueva`; suelo de cueva con **micelio** blanco y violeta en vez de raíces, `pintar_gruta(..., setas=True)`). Se baja por la **escalera del armario** de Nungu (con el armario abierto, la puerta `armario` de la casa) y se sube por la escalera `^`. Capturas: `documentacion/cueva_setas_capturas.png`. Música provisional: la del lago.

- **A oscuras** (`scripts/mundo/cueva_setas.gd`): alumbran Maisha y las **setas que brillan** (`ů`, verde-agua y violetas, `seta_luz.png`), que respiran despacio.
- **Nubes de esporas** (`ǯ`, `scripts/mundo/cueva/nube_esporas.gd`): laten (3 s hinchadas, 1,8 s encogidas). Si Maisha las respira se **marea**: los controles van al revés 3 s (`maisha.mareo`, se quita al revivir). El **Latido** las deshace 4 s. La primera vez, Maisha lo piensa en voz alta.
- **Las tres páginas del diario de Nungu** (`ǹ`, `pagina_nungu.gd`): día 1 (las setas se comen la piedra de Giza), día 9 (una seta grande que «mira») y la última («ella decidirá por mí... traed algo que corte hilos»). Marcas `nungu_pagina/1..3`.
- **El octavo eco** (`eco_cueva_setas`, ilustración `20_eco_cueva`): Kimya enseña a Maisha que las setas «se comen lo que cae y se lo devuelven a la tierra»; «¿y si una seta quisiera mandar, en vez de servir?».
- Al sur, la **cortina de micelio** (`ǫ`, `scripts/mundo/cueva/cortina.gd`) tapa la sala de Kuvu: late, y detrás una voz cansada dice «...descansar...». Se **corta con el cetro** (tres golpes, `cortina_abierta`): «traed algo que corte hilos», escribió Nungu.
- Misión de historia **«Bajo la casa»**: bajar por la escalera → leer las páginas (n/3) → cortar la cortina → liberar a Nungu de Kuvu (`nungu_libre`). Premio: la investigación de Nungu.

### Kuvu, la seta que manda (Paso de Piedra, parte 4)

El jefe de la cueva de las setas (`scripts/enemigos/kuvu.gd`, dibujos en `herramientas/dibujar_kuvu.py`, capturas `documentacion/kuvu_capturas.png`): una seta enorme de Giza que, en vez de comerse lo que cae como las setas de Kimya, **manda**. Tiene a **Nungu** colgado de un hilo de esporas (`scripts/enemigos/nungu_jefe.gd`). Música «La seta que manda» (`jefe_kuvu`): la caja de música del Paso, desafinada y en bucle, con tambores en tres y la flauta de Maisha que rompe el bucle.

| Fase | Qué pasa | Cómo se gana |
| --- | --- | --- |
| 1. Nungu controlado | Kuvu, cerrado (el cetro no le hace nada), suelta nubes de esporas cerca de Maisha. Nungu anda como una marioneta, se hace **bola de púas** y rueda hacia ella | Parar la bola con el **escudo de frente**: rebota y se marea; un golpe de cetro le **corta el hilo** (sin marear, el cetro rebota en las púas) |
| 2. Dos contra uno | Nungu, libre, se pone del lado de Maisha y cada 5 s embiste el pie de Kuvu. Kuvu lanza **latigazos de hilo** (aviso: una raya violeta) | Cuando Nungu lo golpea, Kuvu **levanta el sombrero** 3 s: cetro 1, semilla 2. El escudo, de frente, para los latigazos (si pillan: 1 de daño y mareo) |
| 3. Un tercio de vida | Además, un **hilo lento** va a por la cabeza de Nungu | Ponerse en medio con el escudo lo corta; si llega, Nungu vuelve a estar controlado |

Al vencerlo se marchita (`kuvu_vencido`); Nungu habla, da su **investigación** (objeto clave: Giza «crece hacia el norte, hacia las Ruinas, y se alimenta de lo que se queda quieto») y vuelve a su casa, donde se le puede visitar (`scripts/mundo/paso/nungu_casa.gd`). En el Bestiario, con su rescoldo para repetir la pelea. Números: `KUVU_*` y `NUNGU_*` en `reglas_combate.gd`. Prueba: `prueba_kuvu`.


## Sendero Olvidado (partes 1 y 2: la subida y los Quietos)

Escena `escenas/mundo/sendero_olvidado.tscn` (`scripts/mundo/sendero_olvidado.gd`): la subida de la Gruta de las Raíces (sur) a las Ruinas del Primer Árbol (norte). Se abre con las nueve voces (el Guardián aparta las raíces). No tiene viajero ni encargo: lo distinto es la montaña.

| Qué | Cómo |
| --- | --- |
| El mapa | 60×112, de sur a norte (`crear_olvidado` en `construir_mapa.py`): cinco repisas de peña obligan a subir en zigzag; un rellano con estatuas en medio; arriba, el arco de las Ruinas. Nieve con ondas del viento, camino de nieve pisada y nieve sobre las peñas (`_nevar` en `pintar_suelo.py`). Nieva (`olvidado/nevada.gd`) y hay niebla baja |
| **La escarcha de la quietud** | `olvidado/escarcha.gd`, colgada de Maisha. Giza «se alimenta de lo que se queda quieto» (lo descubrió Nungu): quieta más de 1,2 s lejos del fuego, una costra de hielo le sube por el cuerpo siguiendo su silueta, se le va el color al azul y echa vaho. En ~5 s se **congela**: se queda de piedra 1,3 s y pierde una hoja (`maisha.perder_hoja()`: ni el escudo la para). Andar lo quita poco a poco; junto a un brasero, deprisa. Lo contrario del Lago Espejo |
| **Braseros** | `olvidado/brasero.gd` (6; el de la entrada ya encendido): se encienden con el fuego de una semilla (`semilla.gd` enciende lo que está en el grupo «encendibles» dentro de la cruz) y se quedan encendidos (marca `brasero/sendero_olvidado/x,y`). Llamas de píxeles, chispas y luz. Si Maisha cae, vuelve al último brasero junto al que estuvo |
| **Las estatuas** | `olvidado/estatua_quieta.gd`: una liebre abrazada a su gavilla, un tejón con un farol apagado y una garza con las alas abiertas; al mirarlas, Maisha entiende qué no querían perder |
| El arco | `olvidado/arco_ruinas.gd`: pilares rotos de piedra clara con raíces del Primer Árbol y las nueve espirales; la niebla de entre los pilares se dibuja en el juego. Las Ruinas aún no existen: la niebla no deja pasar |
| **Los Quietos** (parte 2) | `scripts/enemigos/quieto.gd`, dibujo en `pintar_olvidado.py` (`quieto.png`, 5 fotogramas). Figuritas de piedra que juegan a no moverse: si Maisha las **mira** (están delante, hacia donde mira, a menos de 230 px), se tapan los ojos con las manos y no se mueven; si **no** las mira (de espaldas, de lado o congelada), bajan las manos, abren unos ojos violetas y se le echan encima muy deprisa (quitan una hoja). Se les golpea de frente: 3 golpes de cetro (se agrietan) o una semilla (2). La trampa: pararse a vigilarlas sube la escarcha, así que hay que ir hacia ellas sin pararse. Siete por el camino (dos en el rellano, entre las estatuas de verdad) y también salen de la zona. En el Bestiario, con rango |
| Zona y enemigos | Una zona corrupta entre las dos primeras repisas: Quietos, petrinos y búhos-mago (los Quietos de la zona salen desde el arreglo del 21-10-2026: antes fallaban al invocarlos) |
| Música | «La montaña que no se mueve» (`olvidado` en `componer_musica.py`): acordes suspendidos que no resuelven, viento, campanillas de hielo y una flauta sola; al final, la frase de Kimya. Ambiente de viento fuerte |
| Arte | `herramientas/pintar_olvidado.py`: pinos nevados, rocas con nieve, el brasero, las tres estatuas y el arco |
| Misión | «El Sendero Olvidado» (historia): aparece al abrirse el sendero; se cumple al llegar a las Ruinas |

## Las Ruinas del Primer Árbol (el final de Raíz)

Escena `escenas/mundo/ruinas_primer_arbol.tscn` (`scripts/mundo/ruinas_primer_arbol.gd`), al final del Sendero Olvidado. Mapa de 64×60 (`crear_ruinas`): una columnata rota de piedra clara lleva a una plaza redonda de losas en la cima nevada.

| Qué | Cómo |
| --- | --- |
| El Primer Árbol | `ruinas/primer_arbol.gd`, dibujo en `herramientas/pintar_primer_arbol.py` (3 estados: enfermo, gris y medio de piedra con vetas de Giza · con el hueco del tronco abierto · curado, con la copa dorada). No se le pelea a él: se pelea contra su **miedo** a acabarse (Giza es su miedo) |
| Mauti | A sus pies, de piedra (`mauti.png`: la forma de Maisha, porque son hermanos, recoloreada; en lo alto, una hoja seca de cobre). Al final queda libre, plateada y lila, y se puede hablar con Mauti |
| La pelea | `ruinas/miedo.gd`. Al pisar la plaza: lo que dice el árbol (ilustración `22_ruinas_mauti`) y la columnata se cierra. Se gana **recordando**: las nueve piedras del recuerdo (`ruinas/piedra_recuerdo.gd`) se despiertan **manteniendo Acción** a su lado 1,6 s (y mientras tanto hiela: la escarcha del Sendero también está aquí). Cada una trae una frase de un eco y, despierta, da calor. El miedo ataca más deprisa con cada tres: **raíces de piedra** (una grieta violeta corre hacia Maisha y luego brotan pinchos; quitan una hoja), **anillos de escarcha** con dos huecos que giran (suben mucho el frío; se pasan por un hueco o con el Latido) y, desde la segunda fase, **Quietos** |
| El corazón | Con las nueve despiertas se abre el hueco del tronco: el **corazón de Giza** late dentro. 4 golpes de cetro (una semilla, 2) lo rompen |
| El final | El árbol se cura y suelta hojas doradas, Mauti queda libre y cae la **Semilla del Primer Árbol** (objeto clave; de ella saldrá el cetro nuevo del mundo 3). Ilustración `23_arbol_libre` y la pantalla del final del mundo: «Raíz es libre · Fin del primer mundo · Continuará en Sigilia...», contando todos los mapas |
| Música | «Las Ruinas» (solemne, coro lejano) y «El miedo del Primer Árbol» (un latido grave que no para y, por encima, las frases de los ecos) |
| Misión | «El Primer Árbol» (historia) |
| Bestiario | «El miedo del Primer Árbol», como jefe (rango por los golpes recibidos) |

# HD-2D (en pruebas: tecla H)

Decidido con Iam: el juego irá a **HD-2D** (los sprites de pixel art de siempre en un mundo 3D). Se hace con un **espejo** (`scripts/mundo/hd2d/espejo_hd2d.gd`): el juego sigue siendo 2D por dentro (nada de la física, los enemigos, las zonas o los diálogos cambia) y el espejo lo **dibuja en 3D**. Así vale para todos los mapas a la vez, también los que se hagan después. En cualquier escena del mundo, **H** cambia entre 2D y HD-2D (se recuerda en la partida).

| Qué | Cómo |
| --- | --- |
| El suelo | Cerca de Maisha, la **capa de suelo**: un SubViewport que mira la misma escena 2D (el suelo pintado con el gris de Giza, la hierba, las zonas, las raíces, los avisos, los golpes, las llamas...) y se tumba sobre el suelo 3D, con luz para recibir las sombras. Más lejos, el suelo pintado (1 casilla = 1 m) |
| Las peñas | Las casillas «0» se levantan lo que mide su pared pintada (1,25 m; 2,5 en gargantas y montaña). La **pared del sur lleva la roca pintada** del suelo (estratos, grietas, vetas) y el techo toma el dibujo de encima, corrido hacia el norte esa misma altura (como lo pinta la vista 3/4) |
| Lo que va de pie | Llamas de braseros, fogatas y faroles, halos de ecos, esencias y recogibles, la niebla del arco de las Ruinas, el portal del Kitovu y el «!» de los aldeanos (`DE_PIE`): cada uno se ve en una **ventanita** (un SubViewport de 128×160 que mira su trocito de la escena 2D) de pie sobre su objeto; hay 10, para los más cercanos a la cámara |
| Los dibujos | Cada Sprite2D y AnimatedSprite2D del mundo tiene un gemelo 3D **de pie** que mira a la cámara, con **sombra real**; lo pegado al suelo (z por debajo de -4) se tumba. Las capas de un personaje (cuerpo, ropa, cetro) se apoyan en el mismo punto. Conservan sus colores de pixel art y de noche se tiñen de azul |
| El agua | Las casillas de agua («~» y el puente del reflejo «\\») se **hunden 35 cm**: el suelo tiene un agujero ahí (máscara del mapa en el sombreador) y debajo va el agua, algo más oscura y con un brillo que se mueve; la orilla es curva (la máscara se suaviza y tiembla) y el agua se oscurece junto a ella, como la sombra del borde |
| Lo de pantalla | Niebla, hojas que caen, nevada, ventisca y rayos de sol: la **capa de pantalla**, delante, igual que en 2D |
| Sombras | Las sombras ovaladas pintadas no se ven: las pone el sol de verdad |
| Cómo se separa | Cada dibujo va a un «canal» (`visibility_layer` 13-16): la pantalla principal deja de pintar el mundo 2D (`canvas_cull_mask`) y cada capa pinta solo el suyo; la interfaz se queda en el canal 1. Al apagarlo, todo vuelve a su canal |
| Luz y cámara | Sol que sigue el reloj del día y luz de ambiente medidas para que el suelo al sol salga igual de claro que en 2D; sin niebla 3D. Cámara en perspectiva (30°, inclinada 48°) que sigue a Maisha sin salirse del mapa |
| Rendimiento | Solo se copian los dibujos a menos de 30 m de la cámara: el fotograma cuesta lo mismo que en 2D (7,5 ms en los Prados) |
| Prueba | `pruebas/prueba_hd2d.gd` |
| El pie de los dibujos | Los gemelos se apoyan en el suelo por el pie de su dibujo (antes, los dibujos sin centrar flotaban tanto como su altura) |

Comparativas: `documentacion/hd2d_comparativa_1.png` a `_5.png`.

Falta: los desniveles del terreno (colinas); el relieve de los dibujos (mapas de normales) en 3D; lo de pie que dibujan los enemigos con código (auras, avisos en el aire) sale aún en el suelo.

# SIGILIA (mundo 2)

Maandiko, el Archivo Infinito: una ciudad-biblioteca de **armiños escribas** en el norte nevado, donde Giza es el **miedo a olvidar** (la Tinta Quieta deja a la gente «en blanco», sin nombre). Ficha completa en el GDD («Sigilia: ficha del mundo 2») y en `documentacion/decisiones.md`; bocetos en `documentacion/boceto_sigilia.png` y `documentacion/boceto_mapa_sigilia.png`. Su arte va en `arte/mundos/sigilia/` (la región tiene `mundo = "sigilia"`) y sus diálogos en `datos/dialogos/sigilia.json`.

## Paso de la Escarcha (parte 1: la nieve honda y la ventisca)

Escena `escenas/mundo/paso_escarcha.tscn` (`scripts/mundo/paso_escarcha.gd`). Se llega por el **paso del norte de las Ruinas del Primer Árbol**, que se abre al curar al árbol (`primer_arbol_libre`). Mapa de 60×110 (`crear_paso_escarcha`): un valle de montaña ancho, todo nevado de **nieve lila**, que sube en eses hasta la puerta del norte (a Maandiko, que aún no existe: no deja pasar).

| Qué | Cómo |
| --- | --- |
| La nieve honda | `sigilia/nieve_honda.gd`. Fuera del sendero pisado Maisha se hunde: anda al 55 % y no puede correr (`maisha.hundirse`, se apaga sola). Por donde pasa deja un **surco** que dura 90 s: por él ya no se hunde |
| La ventisca de páginas | `sigilia/ventisca.gd`. Calma (5,5-8 s) → aviso (1,3 s: empiezan a volar páginas y sube el viento) → racha (2,6 s) que **empuja** a Maisha a favor del viento (casi siempre del oeste), hacia la nieve honda. Si tiene algo sólido al lado del viento (una estela, una roca, un pino, la peña) está **cobijada** y no la mueve. El empuje es `maisha.viento`, que se apaga solo |
| Las estelas rúnicas | `ȩ`, `herramientas/pintar_escarcha.py`: losas de piedra morada con renglones tallados, nieve encima y una runa dorada. Están junto al sendero, en el lado del oeste, para cobijarse |
| Suelo | `pintar_suelo.py` (nieve lila: `NIEVE_LILA`, en `arte/mundos/sigilia/suelos/`) |
| Pensamientos | Al llegar (`escarcha_llegada`) y tras la primera racha (`escarcha_racha`) |
| Música | Por ahora la del Sendero Olvidado |

### Paso de la Escarcha (parte 2: Taa, la primera ficha y el sigilo de fuego)

| Qué | Cómo |
| --- | --- |
| Taa | `ţ`, `sigilia/taa.gd` (un aldeano de `dibujar_aldeanos.py`: `taa` y `taa_blanco`, 4 fotogramas). El armiño farolero, a media subida junto a su farol apagado, **en blanco**: pálido, sin color en los ojos y sin voz (`taa_blanco`, lo piensa Maisha). Si se le devuelve su ficha, le vuelve el color de golpe (destello y gotitas de tinta) y habla (`taa`) |
| La ficha del Índice | `ǩ`: una tarjeta de pergamino con pestaña morada (`ficha.png`, icono 28.º de `objetos.png`; objeto `ficha_taa`). El viento la llevó al este, a la nieve honda. Es la primera de las 12 del misterio de Sigilia |
| El sigilo de fuego | Lo enseña Taa (marca `sigilo_fuego`). **U** (o RB): Maisha traza delante una runa de fuego (`scripts/combate/sigilo_fuego.gd`) que arde a los 0,25 s: enciende los faroles rúnicos, lo que se enciende (braseros), derrite lo «derretible» (la Tinta Quieta, más adelante) y quema a los enemigos (1). Gasta 20 de Aliento; 0,7 s entre uno y otro |
| Los faroles rúnicos | `ƒ`, `sigilia/farol_runico.gd` (`farol.png`: apagado con escarcha / encendido). 6 por el sendero; solo los enciende el sigilo (no las semillas) y se quedan encendidos. A su lado (52 px) **el viento no empuja y la nieve no es honda** |

### Paso de la Escarcha (parte 3: las páginas sueltas, la Puerta Sellada, la misión y su música)

| Qué | Cómo |
| --- | --- |
| Las páginas sueltas | `ƥ`, `scripts/enemigos/pagina_suelta.gd` (`pagina.png`: 4 aleteos, en picado doblada en punta, golpeada). Hojas escritas con Tinta Quieta, con dos manchas de tinta por ojos que brillan violeta. Van a la deriva; si ven a Maisha (110 px) se le echan encima en curva y, al tocarla, le quitan una hoja y se apartan. Vuelan por encima de todo y las rachas las arrastran. El cetro: 2 golpes; **el sigilo de fuego las quema de un trazo**. En el Bestiario («Página suelta») |
| La Puerta Sellada | `sigilia/puerta_sellada.gd` (`puerta.png`: entera, agrietada, medio derretida, abierta). Arriba del todo, la peña se cierra y solo se pasa por su arco. Tapada de Tinta Quieta (negra, brillante, con vetas violetas y carámbanos): **tres sigilos de fuego** la derriten (marcas `sello_escarcha/1-3` y `puerta_sellada_abierta`). Con Acción, Maisha piensa lo que ve |
| La misión | «El Paso de la Escarcha» (historia): aparece al curar al Primer Árbol; pasos: subir, mirar al armiño en blanco, buscar lo que se llevó el viento, devolvérselo y derretir la Puerta Sellada. La flecha sabe ir de la Gruta al Sendero, a las Ruinas y al Paso |
| Música | «La nieve que escribe» (`escarcha`): un vals lento de caja de música en si menor, con viento y roce de páginas; el **tema de Sigilia** (`TEMA_SIGILIA`) en la flauta y luego en el piano |

La puerta del norte lleva a Maandiko, que aún no existe (no deja pasar).

## Maandiko, la Ciudad-Archivo (parte 1: la ciudad, Kalamu y el mapa)

Escena `escenas/mundo/maandiko.tscn` (`scripts/mundo/maandiko.gd`), detrás de la Puerta Sellada del Paso de la Escarcha. Mapa de 72×56 (`crear_maandiko`), nevado de lila y amurallado; capturas en `documentacion/maandiko_capturas.png`.

| Qué | Cómo |
| --- | --- |
| La ciudad | La avenida del sur lleva a la **Plaza del Índice** (losas de piedra lila, con la **fuente** de tinta helada `ḟ`); al norte, el **Gran Archivo** (`ḃ`, cúpula dorada); al oeste, el Barrio de los Copistas (casas de escribas `ḣ` y la **casa de Kalamu** `ḱ`, con torreón y rollos colgados); al este, el **Mercado de Tinta** (puestos `ṗ`); junto a la avenida, el **taller de Taa** (`ṫ`). Arte en `herramientas/pintar_maandiko.py` (con carámbanos en los aleros) |
| Los vecinos | `sigilia/vecino.gd` (un aldeano con su dibujo y otra conversación). **Kalamu**, la archivera mayor (no está en blanco: repite su nombre en voz alta); **Wino**, el comerciante del mercado (su tienda abrirá más adelante); **Mauti**, en la plaza (con `mauti_libre`), hablando a los escribas en blanco; **Taa**, en su taller; y **escribas en blanco** por las calles (`dibujar_aldeanos.py`: `kalamu`, `wino`, `escriba_blanco`; Mauti, de su dibujo de las Ruinas) |
| El mapa | Kalamu cuenta lo que pasó (el miedo a olvidar, la Tinta Quieta, las fichas del Índice que se llevó el viento) y da el **trozo del norte del mapa** (objeto clave `mapa_norte`) |
| Las salidas | Oeste (Estanterías), este (Canal de Tinta) y noroeste (Observatorio), tapadas por **charcos de Tinta Quieta** (`sigilia/charco_tinta.gd`, `charco.png`): tres sigilos de fuego los derriten. Las escenas de detrás aún no existen |
| Música | «Las calles del Índice» (`maandiko`): el tema de Sigilia en re mayor, como un vals de salón, con puente en menor |
| Misión | «La Ciudad-Archivo»: entrar y encontrar a alguien que recuerde su nombre |
| Prueba | `pruebas/prueba_maandiko.gd` |

### Maandiko (parte 2: la tienda de Wino y los faroles de Taa)

| Qué | Cómo |
| --- | --- |
| La tienda de Wino | Abre al deshelar la primera calle (`calle_deshelada`). Es la misma tienda que la de Tawi (`tienda_tawi.gd`, con `tendero = "wino"`; los artículos llevan `"tienda": "wino"`), con su puesto por dentro y Wino grande con 4 gestos (`herramientas/pintar_tienda_wino.py`: `tienda_wino_fondo.png` y `tienda_wino.png`; captura en `documentacion/tienda_wino.png`). Vende la **Pluma de garza nival** (el sigilo gasta 12 de Aliento en vez de 20), la **Tinta viva** (la runa arde a 30 px en vez de 20) y las **Raquetas de nieve** (en la nieve honda se anda al 80 % en vez del 55 %) |
| Los faroles de Taa | Los faroles de las calles son faroles rúnicos apagados (`ƒ`, 10). Con todos encendidos (`faroles_maandiko`), Taa lo agradece y se ganan **3 Cristales del Nexo** |

Falta: los caminos (Estanterías, Canal, Observatorio) con las fichas del Índice y la Sección Prohibida.

## Las Estanterías Colgantes (parte 1: la biblioteca, las escaleras rodantes y Daftari)

Escena `escenas/mundo/estanterias_colgantes.tscn` (`scripts/mundo/estanterias_colgantes.gd`), por la salida del oeste de Maandiko (tras su charco de Tinta Quieta). Mapa de 60×96 (`crear_estanterias`): una biblioteca de cuatro pisos, de sur a norte. Suelo propio (`pintar_suelo.pintar_biblioteca`): parqué, alfombras moradas con cenefa dorada, **estanterías** con tres baldas de libros (con su lomo y su letrero dorado) y los **huecos** a los pisos de abajo. Capturas en `documentacion/estanterias_capturas.png`.

| Qué | Cómo |
| --- | --- |
| Los huecos | `ɵ`: no se pisan (paredes que pone la escena) |
| Las escaleras rodantes | `ǝ`, `sigilia/escalera_rodante.gd` (`escalera.png`, de `herramientas/pintar_estanterias.py`): tendida 4 s → tiembla 1,1 s → se va rodando → recogida 2,6 s → vuelve. Solo se cruza tendida; si se va con Maisha encima, **cae** al piso de abajo (al pie de la escalera) y pierde una hoja. Cinco, desfasadas |
| El Tintero rabioso | `ǜ`, `scripts/enemigos/tintero.gd` (`tintero.png`, 6 fotogramas; `mancha.png`): el «cazador» de Sigilia. Si ve a Maisha en línea recta, se agacha y **embiste**, dejando manchas de tinta que pringan (frenan); al chocar, se queda bizco: ahí entra el cetro. 3 golpes; semilla o fuego, 2. En el Bestiario |
| Cerraduras | `ẋ`: charcos de Tinta Quieta (como en la ciudad) que tapan una alcoba y un paso |
| La ficha de Daftari | `ʣ`, en la alcoba del oeste del piso 3. En Maandiko, **Daftari** (`sigilia/escriba.gd`: un escriba con nombre propio) está en blanco en la plaza; al darle su ficha recupera el color y habla (encuadernador de libros raros). Dibujo `escriba` (con color) en `dibujar_aldeanos.py` |
| La sala de lectura | Arriba, con su atril y un libro enorme (`atril.png`): ahí espera el Bibliotecario Hueco (parte 2) |
| Prueba | `pruebas/prueba_estanterias.gd` |

Falta: el jefe (el Bibliotecario Hueco) y una música propia (por ahora suena la de Maandiko).

## Las construcciones, al nivel de la casa del castor

Todas las casas y construcciones antiguas se han repintado con el pintor de las cinemáticas (volumen, luz, materiales y objetos de su dueño), casi al doble de tamaño. Capturas: `documentacion/aldea_edificios.png` y `documentacion/casas_caminos.png`.

| Construcción | Programa | Qué tiene |
| --- | --- | --- |
| Casa-seta de Pino | `pintar_aldea.py` | Sombrero rojo con lunares, ventanas redondas encendidas, puerta en arco con farol, puesto de vigía con banderín y catalejo, escalerita, buzón y setitas. En ruinas: gris y con un bocado |
| Taller de Corteza | `pintar_aldea.py` | Piedra y entramado, tejado de tablillas, la chimenea con humo, chispas y la forja encendida, portalón con herrajes, el cartel con su marca, yunque, herraduras, muela y barril |
| Cocina de Juncia | `pintar_aldea.py` | Cabaña de juncos con tejado redondo, mostrador con tarros, ollas colgadas, cestos de bayas, ristras, el caldero al fuego con vapor y un barreño con nenúfar |
| Puesto de Tawi | `pintar_aldea.py` | Toldo a rayas con volante, farolillos, cristales del Nexo, frascos, balanza, telas, plumas, cartel con una pluma, cajas y saco |
| Aprisco de Mbuzi | `pintar_canada.py` | Piedra seca, lajas con musgo, chimenea con humo, candil, cayado, cencerros, un queso; el corral con pesebre, abrevadero y portillo |
| Campamento de Msafiri | `pintar_sendero.py` | Tienda remendada, mapa clavado, banderines de viaje, farol, mesita con el diario y el tintero, la mochila, el trípode del cazo (el fuego, en la base + (26, -1)) |
| Madriguera de Fuko | `pintar_camino.py` | Loma con hierba y hojas de cobre, puerta redonda con mirilla, ventana redonda, tubo de chimenea, farol de mina, los tres ganchos, vagoneta con cobre en raíles, pico y pala |
| Palafito de Korongo | `pintar_pasarelas.py` | Pilotes, barandilla, ventana encendida, tejado de juncos con nido de garza, nasas, peces ahumándose, caña, farolillo y escalerilla |
| Hórreo de Sungura | `pintar_senda.py` | Pies de piedra con losas tornarratas, listones, ristras de mazorcas, escalera suelta, tarros de semillas, sacos y semillero |
| Casa de barcas de Kasia | `pintar_orilla.py` | Nave con la piragua y rampa, el soporte de remos vacío, macetas, veleta-pez, boyas, cuerda, farol y la pizarra de alquiler |
| Molino roto | `pintar_campo.py` | Torre encalada con el yeso caído, balcón, capuchón y veleta torcida, aspas con la lona en jirones, sacos y muela |
| Granero en ruinas | `pintar_campo.py` | Hastial rojo desconchado, portón descolgado, pajar con polea, tejado hundido, gallo-veleta, carreta rota y cuervos |

Los **interiores** de la casa de Pino (una seta por dentro: paredes curvas, láminas en el techo, cama de retales, el mapa de sus exploraciones, tarros de luciérnagas, la ventana redonda, el catalejo, la escalera a la trampilla, baúl y macetas) y del taller de Corteza (piedra y vigas, la forja con campana, brasas y fuelle, el carbón, el banco con dibujos de cetros, las herramientas colgadas, el barril y el suelo de losas) también están en `pintar_aldea.py`, con los muebles en el mismo sitio que antes. El Gran Árbol se queda como estaba (la prueba de repintarlo salió peor que el original).

Los lienzos con algo que asoma por arriba (humo, banderines) usan `pintar_aldea._lienzo` (un lienzo alto: se dibuja con las coordenadas de siempre). Los choques de cada una están en `region.gd` (`EDIFICIOS`, `CAMPAMENTOS`, `FIJOS`).


## Los aldeanos, con más detalle y animados

Los aldeanos siguen en pixel art (24×32, el estilo de Maisha), pero con más detalle (`herramientas/dibujar_aldeanos.py`): Corteza con gafas de forja, cejas fruncidas, hollín, bolsillo con tenazas y cinto; Bibi con una flor en el musgo y el dibujo de la concha; Pino con láminas bajo el sombrero de seta, pañuelo verde al cuello, bandolera con hebilla y bolsito de explorador, pecas y una hoja; Juncia con delantal manchado y pañuelo de lunares; Tawi con plumas de colores y bolsa de monedas; y retoques en los demás. Hoja con todos: `documentacion/aldeanos_animados.png`.

Cada uno tiene ahora **4 fotogramas** (`<id>_anim.png`): quieto, respira (todo baja un píxel menos los pies), parpadea (los ojos se cierran solos) y **su gesto** (Corteza alza el martillo con chispas, Pino saluda, Juncia levanta el cucharón humeante, Tawi agita el ala, Fuko se sube las gafas; los demás levantan lo que llevan: el bastón, la caña, el cayado, la red, la pértiga, el remo o la mazorca). En el juego (`aldeano.gd`) respiran, parpadean cada 2,5-5 s, hacen su gesto cada 7-12 s y al empezar a hablar. `<id>_frente.png` (el primer fotograma) se sigue usando para los retratos y las estatuas. Mzee Shamba (32×40, `dibujar_kitovu.py`) también tiene sus 4 fotogramas (`shamba_anim`: respira, parpadea tras las gafas y levanta el bastón). Las **estatuas de piedra** de los aldeanos (`estatua_<id>.png`, `dibujar_aldea.estatua`) salen de los dibujos nuevos y llevan las vetas violetas de Giza que los petrificó.

## Narrativa y género gramatical neutro (`revision/textos`)

- En `datos/dialogos/raiz.json`: se sustituye `"No. Sola no."` por `"No. Sin ayuda no."` para respetar que Maisha no tiene género gramatical asignado en ninguna línea de diálogo ni pensamiento; en el epílogo del Primer Árbol, se pule `"una luz lila, cansada pero entera"` a `"una luz lila, tenue pero entera"`.
- En `scripts/mundo/interiores/casa_shamba.gd`: Mzee Shamba susurra `"(Duerme, brotecito. Mañana será otro día.)"` evitando el adjetivo masculino.
## Estabilidad y ciclo de vida de nodos

- **Desactivación de proceso en nodos eliminados en `_ready()`**: Cuando un nodo condicional (`aldeano.gd`, `recogible.gd`) evalúa que no debe existir según el `Estado` y ejecuta `queue_free()`, se desactiva explícitamente el procesamiento con `set_process(false)`. Esto previene que `_process()` se ejecute en el fotograma inicial accediendo a propiedades de nodos hijos no instanciados.
- **Captura segura en lambdas de cierre**: En lecciones y corrutinas temporales (`kitovu.gd`), las lambdas no retienen referencias a nodos de escena susceptibles de ser liberados durante la animación (`semilla`), sino identificadores numéricos primitivos (`instance_id`) validados dinámicamente con `is_instance_id_valid()`.

## Limpieza de código (`revision/codigo`)

- `Relieve.textura_luz(tam)` (`scripts/mundo/relieve.gd`) centraliza y guarda en caché por tamaño la textura radial `GradientTexture2D` usada por las luces nocturnas, `Relieve.destello()`, `scripts/mundo/olvidado/brasero.gd` y `scripts/mundo/gruta/oscuridad.gd`.
- En `scripts/interfaz/objetivo.gd` se unifica la comprobación de menús en `oculto_por_menu()`, y en `scripts/combate/zona_corrupta.gd` se simplifica `_al_caer_maisha()`.
## Rendimiento y optimización (`revision/rendimiento`)

- En `scripts/mundo/aldea/aldeano.gd`: se cachea `_tiene_novedad` (evaluada cada 0.5 s o al actualizar marcas) para no evaluar misiones por cada aldeano 60 veces por segundo, y se evita llamar a `queue_redraw()` innecesariamente.
- En `scripts/mundo/ambiente.gd`: se eliminan las llamadas a `.filter()` por fotograma usando eliminación in-place inversa para no generar objetos temporales en el GC; se descartan las nubes fuera de la vista y se dibujan con `draw_set_transform()` sin reservar arrays.
- En `scripts/mundo/luz_sol.gd`: se cachean las referencias a los nodos de grupo `maisha` y `corrupcion`.
- `scripts/personajes/sombra.gd` ya no tiene `_process`: escucha `Reloj.luz_cambiada` (hay mapas con casi 2000 sombras). Para medir: `godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento [hd2d] [noche] [mapas...]` (ver `documentacion/optimization.md`).
- Los árboles y rocas sencillos (`region.gd._fijo_sencillo`) son un solo `Sprite2D` (la sombra va detrás con `show_behind_parent`) y sus cajas de colisión van todas en un único cuerpo, `Entidades/Fijos`. El medidor tiene los modos `pelea` (zona cerrada con unos 10 enemigos) y mide también la carga y el `_draw`.
- Las sombras de esos árboles y rocas van juntas en una malla por trozo de 256 px (`scripts/mundo/trozo_sombra.gd`, en `Region/SombrasFijas`): una llamada de dibujo por trozo en vez de una por sombra. Casi la mitad de llamadas de dibujo en los bosques.
- `ambiente.gd` pinta la niebla y las sombras de las nubes en una sola lista de triángulos, y `zona_corrupta.gd` no se redibuja si está lejos de lo que se ve (`_se_ve()`, 512 px de margen). `espejo_lago.gd` solo pinta los anillos y vetas del agua cerca de lo que se ve.
## Pulido de interfaz (`revision/interfaz`)

- En `scripts/interfaz/menu_pausa.gd`, la ficha de objetos llevados muestra el icono de `arte/interfaz/objetos.png` para cualquier objeto y se organiza en dos columnas cuando hay más de tres para no desbordar `CAJA_INFO`.
- En `scripts/interfaz/objetivo.gd`, `menu_pausa.gd` y `mochila.gd` se desactiva el posicionamiento subpíxel de la fuente; en `mochila.gd` se añade `cueva_eco` a `PUNTO_RAIZ` y se acepta `keycode` además de `physical_keycode` en los atajos `1-6` y `M`.
## Efectos de sonido y equilibrio (`revision/sonidos`)

- `cetro_golpe` usa un barrido continuo de aire con cuerpo de madera en lugar de tramos escalonados de ruido; `golpe_acierto` suma chasquido de piedra y corteza; `semilla_plantar` añade roce de hojarasca y reverberación corta (`herramientas/crear_sonidos.py`).
- En `scripts/globales/sonido.gd` (`VOLUMEN`), los rugidos y victorias de jefes se moderan a `-2,0 dB` para no tapar la música ni las fanfarrias, mientras que `cetro_golpe` (`-6,5 dB`) y `semilla_mecha` (`-9,5 dB`) ganan presencia en combate.
## Equilibrio musical y sintetizador (`revision/musica`)

- En `herramientas/sintetizador.py`, `kalimba` incorpora resonancia de caja de madera (`180-900 Hz`) y leve caída inicial de afinación; `balafon` añade el 2.º armónico del resonador de calabaza y el golpe cálido de maza; `flauta` añade soplo de embocadura en el ataque.
- `Pista.bucle()` y `final()` (`herramientas/componer_musica.py`) funden suavemente los últimos 6-8 ms hacia el inicio tras plegar la cola de reverberación para evitar chasquidos al repetir.
- `normalizar()` aplica saturación suave (`tanh`) ante picos aislados (`> 4,4 × RMS`) —regeneradas `kitovu`, `jefe_pembe`, `jefe_konokono` y `jefe_kambare`— y `scripts/globales/sonido.gd` incorpora `VOLUMEN_MUSICA` (`_db_musica()`) para equilibrar el volumen percibido de las 44 pistas en torno a `-15,5 dBFS`.
Cada uno tiene ahora **4 fotogramas** (`<id>_anim.png`): quieto, respira (todo baja un píxel menos los pies), parpadea (los ojos se cierran solos) y **su gesto** (Corteza alza el martillo con chispas, Pino saluda, Juncia levanta el cucharón humeante, Tawi agita el ala, Fuko se sube las gafas; los demás levantan lo que llevan: el bastón, la caña, el cayado, la red, la pértiga, el remo o la mazorca, desplazados verticalmente de forma íntegra hasta el suelo para que no se corte la base al alzarlos). En el juego (`aldeano.gd`) respiran, parpadean cada 2,5-5 s, hacen su gesto cada 7-12 s y al empezar a hablar. `<id>_frente.png` (el primer fotograma) se sigue usando para los retratos y las estatuas. Mzee Shamba (32×40, `dibujar_kitovu.py`) también tiene sus 4 fotogramas (`shamba_anim`: respira, parpadea tras las gafas y levanta el bastón entero). Las **estatuas de piedra** de los aldeanos (`estatua_<id>.png`, `dibujar_aldea.estatua`) salen de los dibujos nuevos y llevan las vetas violetas de Giza que los petrificó.
