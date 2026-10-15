# Registro de decisiones

Las decisiones van al GDD (sección «Registro de decisiones»). Cuando no hay acceso al GDD, se apuntan aquí y luego
se pasan.

| Fecha | Decisión | Motivo |
| --- | --- | --- |
| 2026-10-11 | Bug: Maisha se quedaba celebrando si una zona se purgaba a mitad de un golpe. Arreglado: al empezar una expresión, el golpe a medias se da por acabado. | Lo encontró Iam en el Kitovu. |
| 2026-10-11 | El proyecto tiene su propio git (dentro de `maisha`). | Antes no había ninguno propio. |
| 2026-10-11 | Primero se hace la **Cañada del Eco** (el camino del Bosque Cobrizo al Lago Espejo, con el 5.º eco) y después el Lago Espejo. | Una cosa cada vez, como los otros caminos. |
| 2026-10-11 | Lo especial del **Lago Espejo**: el reflejo. Algunas cosas solo existen en el reflejo del agua (un puente, un camino escondido, un eco). Encaja con Kimya, la Quietud. | Elegido por Iam. |
| 2026-10-11 | El viajero de la Cañada es **Mbuzi**, una cabra montés pastora. Encargo: tres cencerros que el eco esparció por la cañada. Al devolvérselos descuelga una **escala de cuerda** hasta la cornisa del 5.º eco. | Elegido por Iam. |
| 2026-10-11 | Trazado de la Cañada del Eco aprobado tal cual. Enemigo nuevo: **murciélago de eco** (cuelga de las paredes; su grito en onda rebota en la peña y vuelve). | Elegido por Iam. |
| 2026-10-11 | La cara del acantilado de la Cañada, el doble de alta. Mbuzi: cabra mayor y tranquila, blanca y gris, cuernos curvos, pañuelo rojo y cayado. | Elegido por Iam. |
| 2026-10-11 | Mientras no haya música propia, la Cañada usa «La loma de cobre». El paso al Lago Espejo queda cerrado (marca `camino_lago`) hasta que el lago exista. | Falta ffmpeg en el Mac para guardar música nueva; el lago aún no está hecho. |
| 2026-10-11 | Siguiente: el **murciélago de eco**. El recuerdo del 5.º eco será Maisha, Mauti y Kimya en la cañada gritando sus nombres; el de Kimya no vuelve («la Quietud no tiene eco»). Puente hacia el Lago Espejo. | Elegido por Iam. |
| 2026-10-11 | ffmpeg se instala con pip (`imageio-ffmpeg`, en `requirements.txt`), sin Homebrew ni contraseña. `sintetizador.py` lo encuentra solo. | Iam pidió instalar ffmpeg primero; Homebrew necesitaba la contraseña del Mac. |
| 2026-10-11 | Ilustración del 5.º eco: atardecer en la garganta, los tres en la cornisa gritando hacia la peña; vuelven las ondas de Maisha y Mauti, ninguna de Kimya, que mira el agua quieta del arroyo. | Elegido por Iam. |
| 2026-10-11 | Música de la Cañada: «Lo que la peña devuelve» (flauta y su eco; frase de Kimya sin eco). Sonidos propios del murciélago, la onda, los cencerros y la escala. | Pedido por Iam tras instalar ffmpeg. |
| 2026-10-11 | Lago Espejo: el reflejo se hace real con **quietud** (Maisha quieta ~3 s junto al agua: el lago se vuelve espejo; moverse mucho, golpear o luchar lo rompe). Primero un **minijefe de Giza** enturbia el agua; al vencerlo el lago se aquieta y en la isla aparece **Kimya** (historia, sin pelea). El paso desde la Cañada se abre al escuchar el **5.º eco**. | Elegido por Iam. |
| 2026-10-11 | Trazado del Lago Espejo aprobado. Minijefe: **Kambare, el siluro de cieno** (pez gato de barro y óxido, bigotes como cadenas; nada bajo el agua turbia, salta a la orilla con olas de barro, varado se le puede pegar; en la 2.ª fase escupe chorros de cieno). | Elegido por Iam. |
| 2026-10-12 | Kambare hecho: charca de cieno en medio de la arena, salto con sombra de aviso y ola de barro, varado (cetro 1, semilla 2), fase 2 con chorros de cieno. Al vencerlo, marca `kambare_vencido` y el lago se aclara. Música y sonidos propios. | Diseño aprobado por Iam. |
| 2026-10-12 | Kimya en la isla: solo aparece con el lago en espejo (existe en el reflejo). Conversación con ilustración: en el reflejo de Maisha aparece Mauti. Kimya cuenta que Mauti fue a buscar a quien quería que nada se segara y no volvió, y cómo nació Giza (el miedo a que las cosas acaben las vuelve de piedra). Texto en borrador, pendiente de que Iam lo revise. | Propuesta de Claude. |
| 2026-10-12 | Kimya deja de llamarse «la Quietud»: ahora es **Kimya, el Silencio** (lo que significa *kimya* en suajili). «El Silencio no tiene eco.» La mecánica de quedarse quieta junto al agua sigue llamándose quietud. | A Iam no le gustaba «la Quietud». |
| 2026-10-12 | Música del Lago Espejo: «El agua que recuerda» (una frase del tema de Maisha y su reflejo al revés; al final, la frase de Kimya sin eco). Con ella el lago queda terminado. | Siguiente paso acordado con Iam. |
| 2026-10-12 | Orilla de Juncos (camino de la Ciénaga Quieta al Embarcadero Junco, 64×100, sur → norte): trazado aprobado. Viajera: **Kasia**, la nutria barquera («kasia» = remo en suajili), con gorro de paja y un remo al hombro; encargo: tres remos. Se cruza al banco de arena del 6.º eco **montando en su balsa** (con animación). Enemigo nuevo: **cangrejo de herrumbre** (anda de lado, el cetro rebota en sus pinzas de frente; se le pega por detrás o se le da la vuelta con una semilla). | Elegido por Iam (el nombre Kasia, propuesta de Claude). |
| 2026-10-12 | Revisión de diálogos: Mbuzi y Kimya reescritos con voz propia y detalles concretos (sin frases de sentencia). Corregido el lenguaje con género para Maisha («quieta» → «sin moverse»), también en una línea antigua de Korongo. | Iam pidió diálogos que no parezcan de IA y revisar todo antes de seguir. |
| 2026-10-12 | Revisión del Lago Espejo: orilla con juncos, nenúfares, embarcadero viejo, barca varada y altar de Kimya; isla con piedras talladas y un sauce. Vecino rescatable: **Mdiria**, martín pescador viejo, de piedra junto a la arena; al vencer a Kambare despierta y se queda en el embarcadero. | Iam aceptó las propuestas recomendadas. |
| 2026-10-12 | Orilla de Juncos jugable: Kasia y sus remos, la balsa que cruza sola al banco de arena, el cangrejo de herrumbre. La Ciénaga tiene salida al este. Falta el recuerdo del 6.º eco (pendiente de decidir con Iam) y su música. | Siguiente paso acordado. |
| 2026-10-12 | Arreglado: la flecha de la misión no seguía a lo que se mueve (la chispa, el castor…). Solo se recalculaba cada 0,2 s y guardaba una posición fija; ahora guarda la cosa y lee su posición en cada fotograma, y la flechita de encima se pone según la altura de cada uno. | Lo encontró Iam jugando. |
| 2026-10-12 | Tutorial: lecciones que paran el mundo hasta pulsar la tecla (cetro J junto al espantapájaros; semillas K en la primera mancha, con cámara lenta «¡Sal de la cruz!»; Latido L en la segunda). | Pedido por Iam. |
| 2026-10-12 | Diario nuevo y árbol de habilidades: estilo **noche mágica** (libro de cuero con filigrana dorada, cielo nocturno dentro). Árbol con tronco de raíz dorada y ramas **Raíz**, **Cetro** (nueva) y **Aliento**, y Runa y Tierra dormidas. Nodos normales con **Esencia**; nodos grandes también con **Cristales del Nexo**. Se mejora **desde el diario** en cualquier momento (meditar sigue curando y guardando). | Iam aceptó las propuestas. |

## 2026-10-12 · Diario «noche mágica» y árbol de habilidades
| Decisión | Elegido |
| --- | --- |
| Estilo del diario | Noche mágica: cuero azul, páginas de cielo con estrellas y filigrana dorada |
| Coste de los nodos | Normales con Esencia; los grandes (3 y 6) también con Cristales del Nexo (2 y 4) |
| Dónde se mejora | Desde el diario, en cualquier momento (meditar sigue curando y guardando) |
| Ramas | Raíz, Cetro (nueva), Aliento; Runa y Tierra dormidas |

## 2026-10-12 · El sexto eco y la música de la Orilla
| Decisión | Elegido |
| --- | --- |
| Recuerdo del 6.º eco | «La despedida»: Mauti se va en barca río arriba (a buscar a quien no quería que nada se segara); Maisha se queda con la linterna encendida en la orilla para que sepa volver. Ilustración `18_eco_orilla` |
| Música de la Orilla de Juncos | «La linterna en la orilla», una barcarola en seis (sol mayor) |
| `.agents/` y `skills-lock.json` | Ignorados en git (son las skills de Iam, no parte del juego) |
| Embarcadero Junco (trazado) | Propuesta de Claude: 96×72 (`crear_embarcadero`, boceto `documentacion/boceto_embarcadero_junco.png`), pueblo de barqueros, transbordador varado, la dársena con el jefe, 3 zonas, 3 secretos. Pendiente de Iam: jefe, vecino y cómo se abre |

## 2026-10-12 · Embarcadero Junco
| Decisión | Elegido |
| --- | --- |
| Cómo se abre | Al escuchar el 6.º eco (el barrizal de la orilla se seca) |
| Jefe de la dársena | **Mamba, el cocodrilo de herrumbre**: flota como un tronco y salta a morder la plataforma; si se le esquiva, se le clavan los dientes en un poste y el cetro le hace daño |
| Vecino | **Bata, el pato barquero**: de piedra junto a la dársena; arregla el transbordador y abre La Travesía |
| Hecho en este paso | Mapa, suelo, pueblo de barqueros (casas, grúa, almacén), transbordador, Bata, textos y prueba. Mamba y el arreglo del transbordador, en el paso siguiente |
| Mamba hecho | Pelea con 4 postes de amarre en la plataforma, raya de aviso, coletazo en la fase 2; música y sonidos propios. Pendiente: patas más gruesas y raya del aviso más visible |

## 2026-10-13 · Análisis de Iam y fallos
| Decisión | Elegido |
| --- | --- |
| Normas nuevas | Edificios al nivel de la casa del castor; cada ruta con historia y mecánica propias (no recado + zona + jefe); diálogos más humanos; más enemigos con rango |
| Fallo «no puede correr» / «se queda bugueado» | Causa encontrada: la cámara lenta y el parón de impacto se pisaban y el juego quedaba lento. Ahora solo `Impacto` cambia la velocidad |

## 2026-10-13 · Embarcadero con historia propia
| Decisión | Elegido |
| --- | --- |
| Construcciones | Casas, almacén, grúa y transbordador rehechos al nivel de la casa del castor |
| Rescate de Bata | Ya no es estatua: está encerrado vivo en su casa sellada por raíces. Se siguen las venas violetas hasta un nudo de Giza tapado por sacos; Latido para apartarlos, semilla para reventarlo |
| Pelea contra Mamba | 2 contra 1: Bata en su barca sujeta a Mamba con la pértiga contra el borde |
| Arreglar el transbordador | Con los poderes: semilla junto al boquete → juncos tejidos; Latido pegado al casco → la endereza. Sin recados |
| La Travesía | Viaje en el transbordador: la barca sube sola, Maisha en la cubierta, Bata con la pértiga; atraca en el muelle de piedra de la Gruta. Faltan oleadas y el 7.º eco en la isla |
| La Travesía, oleadas | Cangrejos que trepan por la borda; anguilas de óxido (nuevas) que saltan por encima de la cubierta (golpe en el aire las tumba) |
| 7.º eco | En la isla: Mauti llega a la Gruta y deja su hoja de cobre bajo una piedra para Maisha (objeto clave «hoja_mauti») |

## 2026-10-13 · Gruta de las Raíces (propuesta)
| Decisión | Elegido |
| --- | --- |
| Tipo de lugar | Cueva por dentro (64×84, `crear_gruta`, boceto `documentacion/boceto_gruta_raices.png`) |
| Mecánicas nuevas propuestas | Oscuridad (solo el brillo de Maisha, las semillas dormidas y las huellas lilas de Mauti); pasillo de raíces dormidas (sigilo: andar sí, correr o pelear las despierta); escudo del cetro en el santuario; galería de espinas que necesita el escudo |
| Entrada | Las raíces de la boca se apartan con la hoja de Mauti |
| Elegido por Iam | Escudo con J mantenida; en el fondo, el Guardián de la Gruta con una pesadilla de Giza (se pelea contra la pesadilla); bastante oscuridad |
| El Guardián | Ciervo de raíz con máscara de Giza (marioneta): embestida contra la pared, ola de raíces que para el escudo, 3 fases. Al despertar cuenta que Mauti siguió por el Sendero Olvidado (9 ecos) |


### Diario a pantalla completa (13-10)
| Qué | Decisión |
| --- | --- |
| Petición de Iam | Rehacer el diario a pantalla completa, al estilo de la bolsa de Pokémon Platino |
| Bocetos | A «la bolsa» (mochila + lista + descripción), B libro de borde a borde, C casillas |
| Elegido | ⭐ A: mochila grande con 5 bolsillos a la izquierda, lista grande a la derecha, descripción abajo; Mapa y Habilidades a pantalla entera |
| Orden siguiente | Rangos y enemigos nuevos (mago, bruja) → Paso de Piedra (casa abandonada) → construcciones antiguas → diálogos antiguos |

### Enemigos nuevos y rangos (13-10)
| Qué | Decisión |
| --- | --- |
| Mago | **Bundi, el búho-mago**: se esfuma si te acercas, lanza bolas que persiguen; el escudo se las devuelve |
| Bruja | **Buibui, la araña-bruja**: invoca bichos de óxido (mende) desde su nido; una semilla se lo sella |
| Dónde | Bundi en el Bosque Cobrizo y la Cañada; Buibui en el Camino Cobrizo y el Campo Segado (la Gruta no tiene zonas normales) |
| Rango | Bronce/plata/oro por cuántos vences (10/30/60); jefes por golpes encajados (cualquiera/≤3/0). Plata da 2 cristales y el secreto; oro, 4 |
| Bestiario | 6.º bolsillo del diario, con medallas, fichas y «???» para los que no has vencido |
| Oro de los jefes | Se puede repetir la pelea: en cada arena de jefe vencido queda un **rescoldo de Giza** que revive su eco (sin consecuencias para la historia) hasta tener el oro |

### Paso de Piedra (14-10)
| Qué | Decisión |
| --- | --- |
| Dónde | Del Campo Segado (oeste) a la Gruta (este); el paso a la Gruta se abre al despertar al Guardián (atajo) |
| Historia | Casa abandonada de **Nungu**, un erizo científico que estudiaba la piedra de Giza → armario cerrado con cerradura de Corteza → la llave la tiene **Corteza** en Cuna de Musgo → pasadizo a una cueva de setas |
| Jefe | **Kuvu, la seta que manda** (controla mentes con hilos de esporas) tiene a Nungu controlado; con el escudo se corta su hilo y Nungu pasa a ayudar (2 contra 1) |
| Partes | 1 el paso y la casa (hecha) · 2 la llave de Corteza · 3 el pasadizo, la cueva y el 8.º eco · 4 Kuvu y Nungu |
| Parte 4 hecha | La cortina se corta con el cetro; Kuvu (3 fases) con Nungu controlado → libre; el hilo lento de la fase 3; Nungu regala su investigación y vuelve a casa |

### Construcciones al nivel de la casa del castor (14-10)
| Qué | Decisión |
| --- | --- |
| Petición de Iam | Que las construcciones y los personajes sean muy detallados: «quiero que sea muy bonito visualmente» |
| Hecho | Las 4 de Cuna de Musgo (con ruina y reconstruida) y las 8 casas de los caminos, repintadas casi al doble de tamaño con objetos de su dueño |
| Pendiente | Interiores antiguos (casa de Pino, taller), el Gran Árbol y los personajes (aldeanos) |
| Personajes | Pixel art mejorado (no pintados: a 24×32 salían borrosos) y animados: respiran, parpadean y tienen un gesto propio |

### Diálogos antiguos más naturales (14-10)
| Qué | Decisión |
| --- | --- |
| Lo robótico | Explicaciones de manual (Esencia, zonas corruptas), recuentos de recado («Tienes X de Y») e indicaciones de mapa |
| Hecho | 28 frases reescritas con la voz de cada personaje (Bibi, Pino, Corteza, Tawi, Shamba, Msafiri, Korongo, Fuko, Sungura); las teclas solo se nombran en el tutorial de Shamba |
| Sin género | Fuera los «pequeño brote» de Bibi (ahora «brotecito») y el «pequeña» del segundo eco (ahora «lucecita») |

### Artes visuales y Maisha en grande (14-10)
| Qué | Decisión |
| --- | --- |
| Petición de Iam | Que las habilidades mejoren a Maisha por fuera (ropa, cetro, magia) y verlo antes de comprarlo, con el personaje entero |
| Cada nivel | Un cambio visible por nivel en las 3 ramas (brazaletes → flores; cinta → Cetro del Primer Árbol; bufanda → cuerpo de brisa) |
| El cetro | 6 versiones nuevas, algo más grandes (12×20) y con más detalle; también en el golpe |
| La tienda | La ropa elegida en la mochila manda en su zona; las Artes rellenan las zonas libres |
| Pantalla | Maisha ×4 sobre un tocón a la izquierda, árbol algo más pequeño a la derecha; vista previa sobre los nodos sin despertar y F para ver antes/después |
| 2.5D (idea) | Más adelante, probar luces 2D con mapas de normales en una zona (sin tocar colisiones ni movimiento) |

### Artes visuales grandes y precios (14-10)
| Qué | Decisión |
| --- | --- |
| Opinión de Iam | Los primeros cambios eran muy simples: ahora cada rama cambia la silueta en los niveles 3 y 6 (boceto `boceto_artes_grandes.png`) |
| Capa | Más pequeña que en el boceto (no más ancha que los brazos) y se mece |
| Efectos | Muy sutiles: fuera las estrellitas grandes; anillos, alas, aura y luciérnagas casi transparentes |
| Cetro por mundo | El Cetro-rama vale para los mundos 1 y 2; al acabar el 2, un cetro nuevo más poderoso que se sube desde 0 (se diseña más adelante; el boceto de piedra y runas gusta) |
| Precios | 2, 3, 5, 7, 10 y 14 de Esencia por nivel (`COSTES`): llenar las tres ramas solo completando y explorando los mundos 1 y 2 al 100 %. Se ajustarán al acabar el juego, según la Esencia total |
| Retoque (Iam) | Se veía cargado: cetro fino en todas las fases, fuera chispas del cetro, luciérnagas, el anillo de la cabeza y las motitas del aura y del remolino |

### La luz: relieve, día y noche (14-10)
| Qué | Decisión |
| --- | --- |
| Enfoque | El A: luces 2D con mapas de normales, sin tocar colisiones ni movimiento (el 3D se descartó por coste) |
| Prueba | De día casi no se nota (el arte ya lleva su luz pintada); al atardecer y de noche sí: por eso se usa con un ciclo de día y noche |
| Día y noche | 16 minutos por día, en todos los exteriores, guardado con la partida; empieza al llegar a Cuna de Musgo |
| Noche | Oscura y azulada, con ventanas, faroles y hogueras encendidas y una luz suave alrededor de Maisha para poder jugar |
| Cuevas | Mantienen su penumbra; el ciclo se aparta |
| Magia | Fogonazos de luz al estallar semillas, con el Latido y al golpear |
| Suelos | Sin relieve (40 MB de ruido y apenas se notaba) |

### El noveno eco (14-10)
| Qué | Decisión |
| --- | --- |
| Dónde | Lago Espejo, como estaba previsto («algunas cosas solo existen en el reflejo… un eco»): en la isla de Kimya, solo con el lago quieto |
| Idea | Es la voz del Silencio: no suena, se ve. Al escucharla se calla todo el sonido |
| Recuerdo | Kimya cuenta por qué existen los ecos y avisa de quien vive en las Ruinas sin desvelar quién es («quien no soporta que algo se acabe es porque lo quiso muchísimo») |
| Ilustración | `21_eco_lago`: el cielo vacío; en el reflejo, el Primer Árbol, Kimya y nueve espirales |
| Abrir el sendero | Con las nueve voces, el Guardián aparta las raíces (`sendero_abierto`). Hasta que se haga el Sendero Olvidado, la niebla no deja pasar |

### El final de Raíz y el Sendero Olvidado (15-10)
| Qué | Decisión |
| --- | --- |
| Cómo se decidió | Iam respondió «vale sigue»: se toman las opciones recomendadas; se pueden cambiar |
| Quien vive en las Ruinas | El propio Primer Árbol, enfermo de miedo a morir: Giza es su miedo (deja todo gris y quieto para que nada se acabe). Mauti fue a hablar con él y quedó atrapado en piedra |
| El final de Raíz | Maisha libera a Mauti; el Primer Árbol acepta morir y deja una semilla. De esa semilla saldrá el cetro nuevo al acabar el mundo 2 |
| El Sendero | Montaña con nieve, niebla y estatuas de quienes se quedaron quietos. Sin viajero ni encargo (rutas únicas) |
| Mecánica | La escarcha de la quietud (quedarse quieta congela; lo contrario del Lago) y braseros que se encienden con semillas |
| Partes | 1 la subida (hecha) · 2 los Quietos (estatuas que solo se mueven cuando Maisha no las mira) · 3 las Ruinas y el Primer Árbol |
| Los Quietos (hecho) | Se tapan los ojos con las manos cuando Maisha los mira; de espaldas, se acercan muy deprisa. Encaja con la escarcha: vigilarlos parada congela |
| Las Ruinas (hecho) | Se gana recordando: nueve piedras que se despiertan manteniendo Acción (eso es estar quieta, y hiela); el miedo ataca con raíces, anillos de escarcha y Quietos; al final, el corazón de Giza. El final de verdad pasa a las Ruinas; la Cosechadora enseña un final a medias («algo sigue enfermo en el norte») |

### El fallo de K + L (15-10)
| Qué | Decisión |
| --- | --- |
| El fallo | Iam: «cuando presionabas K y L, el personaje se quedaba bugueado, no podía correr, iba muy despacio y hasta que no morías no volvía a su velocidad» |
| Qué se hizo | No se pudo reproducir con certeza, así que se blindaron las dos causas posibles que encajan: (1) el entumecimiento del despertar (andar al 40 % y sin correr) lo recupera ahora Maisha sola, no una animación de la escena que podía cortarse, y a los 20 s sin recuperación se recupera igual; (2) la cámara lenta de la lección «¡Sal de la cruz!» se quita si la lección desaparece y, como seguridad, sola a los 8 s. Además, al revivir se quita todo lo que frena |


### Ilustraciones más realistas (2.ª tanda)
| Qué | Decisión |
| --- | --- |
| Árboles | Las copas eran ruido de puntitos. Ahora `copa_racimos` (en `cinematicas.py`) pinta racimos de hojas con luz, sombra y borde de hojitas; lo usan `arbol` y `arbol_grande`, así que mejoran todas las ilustraciones con árboles (Kitovu de antes, Pembe, la fiesta…) |
| La fiesta (recuerdo 1) | Los castores eran siluetas negras: ahora la hoguera les ilumina la cara y el pecho, y hay un charco de luz en el suelo |
| Pembe (9) | Rehecho con anatomía de ciervo: pecho hondo, anca, patas con rodilla, corvejón y pezuña, cuello largo que baja en reverencia, cabeza con hocico y oreja; musgo en manchitas en vez de rectángulos |
| Manchas en los ecos | Los ecos (noche, agua, niebla) se veían sucios: la paleta no tenía esos tonos y los degradados saltaban a gris en manchas. Se añadieron 5 rampas a la paleta de cinemáticas (agua honda, verde agua, bruma, malva y nieve: 210 colores) y el marco de niebla de los recuerdos pasa a ser un velo suave hecho con la propia escena desenfocada |
| El Primer Árbol en los ecos 15 y 23 | Era una nube amarilla con un palo; ahora usa el mismo árbol de racimos dorados, tronco y raíces que el primer eco (`_primer_arbol` llama a `_arbol_dorado`) |
| La pared de la Cañada en el 17 | Era un polígono negro plano; ahora es roca con escalones, estratos, grietas, un canto iluminado por el horizonte y hierbas arriba |
| Las paredes de la Cañada (16) | Eran una masa oscura borrosa; ahora son capas de roca apiladas con juntas onduladas, el canto de cada capa con luz y hierba, sombra debajo, algunas grietas y la cara del hueco encendida por el sol |
| La cueva de las setas (20) | Era un fondo negro con setas; ahora tiene una bóveda de rocas que iluminan las setas desde abajo, estalactitas con gotas que brillan, suelo con piedras y charcos de luz, setas con láminas, motitas y racimos, y dos setas enormes delante |
| El eco del lago (21) | El árbol del reflejo usa el árbol nuevo, más grande y con más brillo; las nueve espirales forman un arco alrededor de la copa que cabe en el reflejo; más hierba en la isla |

### Sigilia (mundo 2) — decidido con Iam el 2026-10-15 («vale sigue me gusta»)
| Qué | Decisión |
| --- | --- |
| Escribas | Armiños (blancos en invierno, con lentes y plumas) |
| Giza en Sigilia | El miedo a olvidar: lo escribieron todo, la tinta se heló (Tinta Quieta) y quien la toca pierde su nombre («en blanco») |
| Llegada | Por el Paso de la Escarcha, que sale de las Ruinas del Primer Árbol |
| Ficha (propuesta) | Ciudad Maandiko; caminos: Paso de la Escarcha, Estanterías Colgantes, Canal de Tinta, Observatorio de la Aurora y Sección Prohibida. Sigilos Fuego, Hielo y Rayo (arte Runa). Jefes: Bibliotecario Hueco, Pweza, Kengele y el Grimorio de Tinta. Misterio: 12 fichas del Índice que devuelven nombres. Detalle en el GDD, sección «Sigilia: ficha del mundo 2» |
| Bocetos | Ambiente: `documentacion/boceto_sigilia.png` (`herramientas/boceto_sigilia.py`). Mapa de regiones: `documentacion/boceto_mapa_sigilia.png` (`herramientas/boceto_mapa_sigilia.py`) |
| Mauti en Sigilia | Va con Maisha pero se queda en la ciudad ayudando a los escribas en blanco; aparece en momentos clave (Iam: «vale sigue») |
| Paso de la Escarcha, parte 2 | Taa (armiño farolero) está en blanco a media subida; su ficha del Índice se la llevó el viento al este. Al devolvérsela recupera el color y enseña el SIGILO DE FUEGO: tecla nueva U (RB en el mando; RB deja de ser «cambiar de semilla», que no se usaba), 20 de Aliento. Los faroles rúnicos solo los enciende el sigilo y, encendidos, abrigan del viento y ablandan la nieve |
| Paso de la Escarcha, parte 3 | Páginas sueltas (enemigo: 2 golpes, el fuego las quema de un trazo). La Puerta Sellada se derrite con 3 sigilos; arriba la peña se cierra para que no se rodee. Misión «El Paso de la Escarcha». Música «La nieve que escribe» con el tema de Sigilia (vals de caja de música en si menor) |
