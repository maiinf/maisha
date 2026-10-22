# Registro de decisiones

Las decisiones van al GDD (sección «Registro de decisiones»). Cuando no hay acceso al GDD, se apuntan aquí y luego
se pasan.

| Fecha | Decisión | Motivo |
| --- | --- | --- |
| 2026-10-22 | **Blender 5.2.3 LTS como única versión del pipeline 3D**: el generador `herramientas/blender/generador_3d_maisha.py` se probó en Blender 5.2.3 en una copia aislada: genera los 104 `.glb` sin errores (solo avisos de `Material.use_nodes`, que se retirará en Blender 6.0). Se desinstala la descarga de 4.5.15. Las entradas anteriores que citan 4.5 se dejan como historial. | Petición de Iam: usar siempre la versión más nueva y no mezclar versiones. |
| 2026-10-18 | **Oleada 7 y 8 HD-2D: 66 Estructuras 3D Sólidas y Suite Completa de 23 Biomas**: Modelados proceduralmente en Blender 4.5 e integrados en `MODELOS_BLENDER`: `roca_grande.glb`, `roca_pequena.glb`, `arbol_muerto.glb`, `seta_luz.glb`, `cartel_madera.glb`, `tronco_caido.glb`, `pino_nevado.glb` y `sauce_pantano.glb`. Erradicación de más de 1,500 billboards planos en todo el mundo. Suite de verificación `verificar_gameplay_visual.gd` ampliada a los 23 mundos completos del juego (100% cobertura) con 0 fallos visuales y 0 regresiones. | Eliminación integral de billboards de papel, garantía de estabilidad 360° y validación continua del gameplay sin tocar lógica 2D. |
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

### Revisión de textos y género gramatical neutro (`revision/textos`)
| Qué | Decisión |
| --- | --- |
| Neutro para Maisha | En `datos/dialogos/raiz.json` (`embarcadero_darsena_sola`), `"No. Sola no."` pasa a `"No. Sin ayuda no."` para respetar estrictamente que Maisha no tiene género gramatical asignado |
| Claridad y tono | En `datos/dialogos/raiz.json` (`primer_arbol_final`), `"una luz lila, cansada pero entera"` se ajusta a `"una luz lila, tenue pero entera"` para evitar ambigüedad léxica; en `scripts/mundo/interiores/casa_shamba.gd`, Shamba susurra `"(Duerme, brotecito...)"` en vez de `"(Duerme, pequeño brote...)"` |

### Revisión de estabilidad (16-10)
| Qué | Decisión |
| --- | --- |
| Acceso nulo en `aldeano.gd` | Al activarse `requiere` o `esconder_si`, `queue_free()` en `_ready()` no evita que `_process()` corra en ese fotograma antes de instanciarse el sprite. Se añade `set_process(false)` antes de `queue_free()` y guarda de seguridad en `_process()`. |
| Captura de lambda liberada en `kitovu.gd` | La lección de la semilla («¡Sal de la cruz!») pasaba una lambda capturando directamente el nodo `semilla`. Al estallar la semilla y liberarse, Godot lanzaba error por captura liberada. Se captura el identificador numérico `id_semilla` (`get_instance_id()`) y se valida con `is_instance_id_valid()`. |
| Blindaje en objetos recogibles | En `recogible.gd`, se añade `set_process(false)` antes de `queue_free()` y guarda de `_sprite` en `_process()`. |
### Limpieza y deduplicación de código (`revision/codigo`)
| Qué | Decisión |
| --- | --- |
| Textura radial de luz (`relieve.gd`) | `Relieve.textura_luz(tam)` pasa a ser estática y con caché por tamaño (`_cache_luz`), eliminando la construcción repetida de `GradientTexture2D` en `Relieve.destello()`, `scripts/mundo/olvidado/brasero.gd` y `scripts/mundo/gruta/oscuridad.gd` |
| Deduplicación en interfaz y combate | En `scripts/interfaz/objetivo.gd`, `_oculto()` reutiliza `oculto_por_menu()`; en `scripts/combate/zona_corrupta.gd`, `_al_caer_maisha()` unifica la llamada a `hud.fundido()`; en `herramientas/componer_musica.py` se elimina la importación duplicada de `paso_bajo` |
### Optimización y rendimiento (`revision/rendimiento`)
| Qué | Decisión |
| --- | --- |
| Aldeanos (`aldeano.gd`) | Se cachea `_tiene_novedad` (revisada solo cada 0.5 s o al cambiar marcas) y la referencia a Maisha, evitando llamar a `CHARLA.tiene_novedad()` y `queue_redraw()` en cada fotograma cuando el aldeano no tiene novedad |
| Ambiente (`ambiente.gd`) | Se sustituyen 5 llamadas a `.filter()` por fotograma con eliminación in-place inversa para no reservar nuevos arrays ni closures cada fotograma; se descarta el dibujo de nubes fuera de la vista y se dibujan con `draw_set_transform()` sin reservar `PackedVector2Array` |
| Luz del sol (`luz_sol.gd`) | Se cachean los nodos de grupo `maisha` y `corrupcion` en lugar de buscarlos en cada fotograma |
| Medición | `cuna_de_musgo` mejora de 7.81 ms/frame (128 FPS) a 7.08 ms/frame (141 FPS); `prados_del_eco` de 9.20 ms/frame (108 FPS) a 8.49 ms/frame (118 FPS) |
| Sombras (`sombra.gd`, rama `optimizar`) | Sin `_process`: `Reloj` emite `luz_cambiada` cuando la luz cambia más de 0,01 (o cruza día/noche) y cada sombra hace la misma comprobación de antes. Scripts por fotograma: La Travesía de 4,32 a 0,38 ms, Bosque Cobrizo de 3,57 a 0,50 ms. Se ve igual. Plan y medidas en `documentacion/optimization.md` |
| Árboles y rocas (`region.gd._fijo_sencillo`, rama `optimizar`) | Un solo `Sprite2D` con la sombra detrás (`show_behind_parent`, se pinta igual) y las cajas de colisión de todos en un único `StaticBody2D` («Fijos», con `create_shape_owner`). Nodos: La Travesía de 7928 a 4113, Bosque Cobrizo de 5915 a 3350. Los fijos con charla, los postes de Mamba, campamentos y edificios siguen igual |
| Sombras de árboles y rocas (`trozo_sombra.gd`, rama `optimizar`) | Ya no van una a una entre los dibujos (cada polígono era una llamada de dibujo y partía los lotes): van juntas en una malla por trozo de 256 px, a ras de suelo (`Region/SombrasFijas`, z −1). Mismas elipses (`sombra.gd` → `puntos()`, `color()`). Capturas: idénticas salvo lo animado (`documentacion/revision/sombras_fijas_antes_despues.png`). Llamadas de dibujo: La Travesía 392 → 157 (2,38 → 1,45 ms), Bosque 378 → 183 (2,85 → 2,11 ms), Prados 284 → 148 |
| Niebla, nubes y zonas lejanas (`ambiente.gd`, `zona_corrupta.gd`, rama `optimizar`) | La niebla y las sombras de nubes, en una sola lista de triángulos (los mismos que antes); las zonas corruptas solo se redibujan a menos de 512 px de lo que se ve. Ciénaga 2,44 → 2,03 ms |
| Anillos del Lago Espejo (`espejo_lago.gd`, rama `optimizar`) | Con el agua turbia, solo se pintan los anillos y vetas de las casillas a menos de 512 px de lo que se ve (antes, ~130 anillos de todo el lago, una llamada de dibujo cada uno). En pantalla, igual. 285 → 275 llamadas de dibujo (2,11 → 2,06 ms) |

### Revisión de interfaz (`revision/interfaz`)
| Qué | Decisión |
| --- | --- |
| Menú de pausa (`menu_pausa.gd`) | Los objetos que lleva Maisha dibujan todos su icono de `objetos.png` (antes solo `seta_luminosa` y `mineral`) y se disponen en 2 columnas a partir de 4 objetos para que no desborden `CAJA_INFO` |
| Nitidez de fuente y mapa | Desactivado el posicionamiento subpíxel en `objetivo.gd`, `menu_pausa.gd` y `mochila.gd`; añadido `"cueva_eco"` a `PUNTO_RAIZ` en `mochila.gd` y soporte de `keycode` además de `physical_keycode` en los atajos `1-6` y `M` |
### Revisión de efectos de sonido (`revision/sonidos`)
| Qué | Decisión |
| --- | --- |
| Efectos orgánicos | En `herramientas/crear_sonidos.py`, `cetro_golpe` reemplaza los 16 tramos escalonados de ruido blanco por un barrido continuo de ruido rosa con cuerpo grave de madera y reverberación corta; `golpe_acierto` incorpora chasquido de piedra/corteza (`_crujido_piedra`); `semilla_plantar` añade textura de hojarasca y reverberación corta |
| Equilibrio de `VOLUMEN` | En `scripts/globales/sonido.gd`, se moderan a `-2,0 dB` los rugidos y victorias de jefes que estaban en `0,0` / `-1,0 dB` (para que no tapen la música ni las fanfarrias) y se suben `cetro_golpe` (`-8,0` → `-6,5 dB`), `semilla_mecha` (`-12,0` → `-9,5 dB`) y `mende_corre` (`-12,0` → `-10,0 dB`) |
### Revisión de música y sintetizador (`revision/musica`)
| Qué | Decisión |
| --- | --- |
| Timbre orgánico | En `herramientas/sintetizador.py`, `kalimba` añade resonancia de caja de madera (`180-900 Hz`) y leve caída inicial de afinación al pulsar la lámina; `balafon` suma el 2.º armónico del resonador de calabaza y el golpe cálido de maza; `flauta` añade soplo de embocadura en los primeros 35 ms |
| Costura de bucle | `Pista.bucle()` y `final()` en `componer_musica.py` funden los últimos 6-8 ms hacia la primera muestra tras plegar la cola de reverberación, eliminando cualquier chasquido al repetir |
| Equilibrio de volumen | `normalizar()` aplica saturación suave (`tanh`) cuando picos aislados de percusión superan `4,4 × RMS` (regeneradas `kitovu`, `jefe_pembe`, `jefe_konokono` y `jefe_kambare`, que estaban entre `-18,5` y `-19,8 dBFS`), y `scripts/globales/sonido.gd` incorpora `VOLUMEN_MUSICA` y `_db_musica()` para alinear todas las piezas en torno a `-15,5 dBFS` |
### Revisión de luz y relieve 2.5D (16-10)
| Qué | Decisión |
| --- | --- |
| Mapas de normales de aldeanos y criaturas (`relieve.py`) | `relieve.py --todo` solo procesaba `arte/mundos`, dejando planos a los aldeanos (`arte/personajes/aldeanos/`) y a las criaturas y jefes de `arte/zonas/raiz/`. Se amplió `relieve.py` y se generaron sus `_n.png` para que la luz del sol, faroles y fogonazos resbale también sobre ellos. |
| Luces nocturnas del Kitovu y biomas (`relieve.gd`) | Añadidas a `LUCES` las ventanas y faroles de `casa_shamba.png`, `almacen.png` y `cubierta.png`. Añadida tabla `BIOMAS` para modular suavemente el tinte ambiental según la región (otoño cálido en el Bosque Cobrizo, bruma verdosa en la Ciénaga Quieta, aire frío en las cumbres) y giro progresivo del ángulo solar a lo largo del día. Reutilizada `_textura_luz()` en `Relieve.destello()`. |
| Sombras y rayos de sol (`sombra.gd`, `luz_sol.gd`) | La sombra elíptica bajo los personajes se inclina y estira suavemente al atardecer según `Reloj.calidez()` y `Reloj.luz_dia()`. En `luz_sol.gd` se añadieron motas de polvo luminoso flotando dentro de los haces de sol. |
### Revisión de sprites · Personajes, aldeanos, enemigos y jefes (16-10)
| Qué | Decisión |
| --- | --- |
| Bastones de aldeanos | En el 4.º fotograma de la animación de Shamba, Bibi, Bata, Mbuzi y Msafiri, el bastón, pértiga o cayado se cortaba con un hueco vacío antes del suelo. Se ampliaron `alza_derecha` (`dibujar_aldeanos.py`) y `shamba_anim` (`dibujar_kitovu.py`) para desplazar todo el tramo vertical hasta el suelo (`ALTO` y `h`). |
| Konokono (`dibujar_konokono.py`) | `HojaE.grieta()` aplicaba el factor de escala `E` dos veces (`E * E = 1,69x`), desplazando las grietas de Giza fuera del caparazón hacia el cuello y dejando un píxel violeta flotando en el aire en el fotograma 5. Corregido eliminando el escalado duplicado en `HojaE.grieta()`. |
| Pembe (`dibujar_pembe.py`) | En el galope (fotograma 3) las pezuñas quedaban separadas del resto de la pata por un hueco transparente, y al escarbar (fotograma 2) los granos de polvo eran píxeles aislados con contorno negro. Unido el trazo de la pata hasta la pezuña y agrupado el terrón de tierra. |
| Petrino (`dibujar_criaturas.py`) | La grieta violeta del corazón colgaba por debajo de la entrepierna al vacío y el cuerpo era un óvalo liso. Subido el corazón a `arriba + 10`, blindado `Hoja.grieta()` para no pintar puntos de luz sobre fondo transparente y añadido relieve de piedra (`corteza()`). |
| Jabalí de Hierro (`dibujar_jabali.py`) | Añadidos remaches oscuros, brillos y filo de óxido a las placas dorsales, textura de cerdas en el lomo, estela violeta en el ojo al embestir y terrones compactos al escarbar. |
| Pino (`dibujar_aldeanos.py`) | Añadidas láminas bajo el sombrero de seta, pañuelo verde de explorador al cuello, bandolera cruzada con hebilla de latón, bolsito de semillas y sonrisilla. |
| Maisha (`dibujar_maisha.py`) | Añadido `CUERPO_PERFIL_LATE` en `reposo_lado` (el corazón brilla en el 3.er fotograma como de frente) y `PIERNAS_PERFIL_AIRE_*` en `correr_lado` para que ambos pies despeguen del suelo en los fotogramas de vuelo (2 y 4), manteniendo intacto el anclaje de la mano. |

### Revisión de sprites · Bastones y gestos de los aldeanos (16-10)
| Qué | Decisión |
| --- | --- |
| El fallo | En el 4.º fotograma de la animación de los aldeanos (Shamba, Bibi, Bata, Mbuzi y Msafiri), el bastón, pértiga o cayado se cortaba con un hueco vacío de varios píxeles antes del suelo y dejaba la base flotando desconectada. |
| Causa | En `herramientas/dibujar_aldeanos.py`, `alza_derecha` detenía el desplazamiento en la fila 28 con la intención de excluir los pies, dejando las filas 28..31 intactas y borrando las filas anteriores. En `herramientas/dibujar_kitovu.py`, `shamba_anim` recortaba `h - 4` pero no limpiaba la base. |
| Solución | Se ampliaron ambos recortes para desplazar verticalmente todo el tramo hasta el suelo (`ALTO` y `h`), levantando los bastones enteros en el aire sin truncar la base. Se regeneraron todos los sprites de aldeanos y Kitovu. |
### Revisión de ilustraciones · Cinemáticas y ecos (16-10)
| Qué | Decisión |
| --- | --- |
| Horizontes periódicos (`linea_horizonte`) | `linea_horizonte()` en `herramientas/cinematicas.py` usaba frecuencias armónicas exactas (`(2 ** o) / escala`), lo que en escalas cortas como `17_kimya_lago` producía una repetición exacta de dientes de sierra cada 34 px. Reemplazado por frecuencias incommensurables (`2.17 ** o` con variación aleatoria y onda base de baja frecuencia). |
| Reflejo de `17_kimya_lago` (`cinematicas_sendero.py`) | Por debajo de `y = 2 * HZ` (`196 px`), el espejo del agua saturaba `origen = 0` y repetía verticalmente la fila 0 del cielo, estirando dos estrellas del borde superior como dos rayas verticales en el agua. Ahora el tramo inferior del reflejo se funde suavemente hacia azul noche profundo (`#0b1122`), como en `21_eco_lago`. |
| El Primer Árbol en las Ruinas (`22_ruinas_mauti`) | `_arbol_gris()` tenía un tronco trapezoidal recto sin raíces ni corteza, en contraste con `_arbol_dorado()` en `23_arbol_libre`. Se igualó su anatomía con raíces extendidas en la nieve, corteza estriada con relieve, ramas nudosas y tres grandes vetas violetas de Giza. |
| La granja y la leyenda (`2_familia_shamba`, `3_leyenda`) | En `casa_troncos()` se pintó la acequia de piedra con agua y espuma al pie de la rueda del molino; en `leyenda()` se sombreó el brazo de la mecedora (`brazo_m`, que se calculaba pero no se pintaba) y se reemplazó el árbol de 3 trazos rectos dentro de la visión del cetro por un árbol viejo con raíces y primeros brotes verdes. |


### Revisión de la IA revisora (unida el 2026-10-16 por la constructora)
| Rama | Qué aporta | Valoración |
| --- | --- | --- |
| textos | Corrige tres frases con género para Maisha («Sola no», «cansada pero entera», «pequeño brote») | Buena y necesaria |
| estabilidad | Aldeanos y recogibles que se borran al nacer ya no siguen procesando; la lección de la semilla del Kitovu no guarda un nodo ya borrado | Buena |
| codigo | Una sola textura de luz compartida (`Relieve.textura_luz`), menos código repetido | Buena (las luces cambian muy poco de forma) |
| rendimiento | Aldeanos, ambiente y rayos de sol hacen menos trabajo por fotograma (+9-10 % medido en Cuna de Musgo y Prados) | Buena |
| interfaz | Pausa con iconos y dos columnas; letras más nítidas; atajos con teclados no españoles | Buena |
| sonidos | Nuevos `cetro_golpe`, `golpe_acierto` y `semilla_plantar`; volúmenes de jefes | Correcta, pendiente de oír |
| musica | Instrumentos del sintetizador más ricos, costuras de bucle sin clic, `VOLUMEN_MUSICA` para igualar pistas | A medias: solo se regeneraron 4 pistas; no hay música nueva |
| luz-2.5d | Mapas de normales para aldeanos y enemigos, sombras que se estiran con el sol, motas de polvo en los rayos, luces en casa de Shamba, tinte por bioma | Buena; se quitó un nombre de escena equivocado (de Sigilia) |
| sprites / bastones | Bastones que no se cortan, Pino con bufanda y correa, corazón de Petrino más visible, retoques de 1-2 px en Pembe, Konokono, Jabalí y Maisha de perfil | Pequeña |
| ilustraciones | Tronco de la 22 con corteza y raíces; charco junto al molino en la 2 | Pequeña; en la 3 y la 17 apenas cambia nada |

### El aspecto del juego: HD-2D (2026-10-16, Iam: «vale sigue»)
| Qué | Decisión |
| --- | --- |
| Camino | **HD-2D**: los sprites de pixel art de siempre en un mundo 3D (sombras reales, desniveles, luces, niebla), como el prototipo de `experimento/prototipo-visual`. No 3D completo con modelos (sería rehacer todo el juego y, generando el arte con código, quedaría peor que el 2D) |
| Sigilia | Se sigue construyendo en 2D; se pasará a HD-2D con el mismo conversor que el resto |
| Quién | La constructora hace el conversor de mapas (`Region3D`) y la parte visual; la revisora vuelve a revisar y pulir lo hecho |
| Modelos 3D de la rama experimental | Se quedan en esa rama como referencia; no se usan |

### Maandiko, parte 1 (2026-10-17, con las ⭐ de Iam: «vale sigue»)
| Qué | Decisión |
| --- | --- |
| Tienda | Un comerciante nuevo, **Wino**, armiño, en el Mercado de Tinta (tinta, plumas y papel). Abrirá cuando la ciudad se deshiele |
| Tamaño | Mediana (72×56 casillas, como Cuna de Musgo y algo más) |
| Taa | Vuelve a su taller; más adelante dará algo por cada calle con los faroles encendidos |
| Kalamu | No está en blanco: repite su nombre en voz alta. Da el trozo del norte del mapa (`mapa_norte`) |
| Salidas | Tapadas por charcos de Tinta Quieta (3 sigilos de fuego cada uno) |
| Maandiko, parte 2 | La tienda de Wino (misma tienda que la de Tawi, con otro tendero) abre al deshelar una calle y vende mejoras de Sigilia: pluma (sigilo más barato), tinta viva (sigilo más grande) y raquetas (menos hundimiento). Los faroles de las calles son rúnicos: encenderlos todos da 3 Cristales a través de Taa |

### Las Estanterías Colgantes, parte 1 (2026-10-17)
| Qué | Decisión |
| --- | --- |
| La mecánica | Escaleras rodantes sobre los huecos entre pisos: se cruzan solo tendidas y, si se van con Maisha encima, cae un piso y pierde una hoja |
| Enemigo nuevo | El Tintero rabioso, el «cazador» de Sigilia (embiste en línea recta y deja manchas que frenan) |
| Las fichas | Cada ficha cura a un escriba con nombre propio de Maandiko (`sigilia/escriba.gd`). La segunda es la de Daftari, encuadernador |

### Acabado HD-2D de alta calidad (2026-10-17)
| Qué | Decisión |
| --- | --- |
| Postprocesado (`hd2d/postproceso`) | Sombreador propio en GL Compatibility con *tilt-shift* dinámico centrado en Maisha, *bloom* cálido que descarta blancos de baja saturación para no quemar la nieve, etalonaje por hora/bioma y selector `Calidad HD-2D: alta / media / baja` en el menú de pausa |
| Iluminación 3D y relieve (`hd2d/luces`) | Luces `OmniLight3D` nocturnas reutilizando `Relieve.LUCES` + edificios de Maandiko + espejo automático de `PointLight2D`. Sombreador de gemelos con mapas de normales (`*_n.png`), sombras suaves y oclusión ambiental de contacto horneada en el suelo (`_mascara_ao`) |
| Terreno y agua (`hd2d/terreno`) | Ondulaciones suaves en `vertex()`, peñas con bisel superior y oclusión en la base, espuma animada en orillas y desvanecimiento perimetral en los bordes del mapa |
| Perspectiva (`hd2d/sprites`) | Teleobjetivo de maqueta (`CAMARA_FOV = 18.0`, `CAMARA_DISTANCIA = 50.6`) para eliminar la inclinación trapezoidal de las casas en los bordes de la pantalla manteniendo el mismo encuadre; optimización de gemelos estáticos (×3 más rápido en mapas grandes) |
| Cámara, vida y remates (`hd2d/camara`, `hd2d/vida`, `hd2d/remates`) | Activación síncrona de HD-2D al entrar en escena, anticipación al correr, encuadre cercano en diálogos, mecido de flora con el viento y al paso de Maisha, partículas 3D (`MultiMeshInstance3D`) por bioma y ventanitas `CANAL_PIE` para enemigos y jefes |
| Prueba piloto de Blender (`hd2d/blender-piloto`) | Se modeló `casa_seta_piloto.glb` en Blender 4.5 con textura pixel art de la paleta de Raíz (`NEAREST`) y se comparó dentro de `cuna_de_musgo` de día y de noche (`06_blender_piloto_antes_despues.png`). Se descarta sustituir los edificios pintados por mallas 3D porque el sprite 2D con mapa de normales conserva mucha más riqueza artesanal (lunares, vigía, farol, musgo) |

### Arquitectura 3D sólida de Blender 4.5 en HD-2D (2026-10-18, petición explícita de Iam)
| Qué | Decisión |
| --- | --- |
| Escenario y Edificios | A petición de Iam para eliminar el efecto plano de lámina 2D vista desde atrás o arriba, se adopta el modelo exacto de *Octopath Traveler*: los personajes y enemigos son sprites 2D con mapas de normales y relieve, y la arquitectura (edificios, farolas, puentes, gran árbol y archivos) se levanta como **mallas 3D reales (`.glb`)** modeladas proceduralmente en Blender 4.5 (`herramientas/blender/generador_3d_maisha.py`). |
| Catálogo de Modelos | 11 modelos de arquitectura integrados en `MODELOS_BLENDER` dentro de `espejo_hd2d.gd` (Casa Pino, Forja Corteza, Gran Árbol, Molino Shamba, Farol Madera, Cocina Juncia, Puesto Tawi, Gran Archivo, Taller Taa, Casas de Escribas). Las ruinas conservan su extrusión dilapidada y, al reconstruirse en la historia, se sustituyen por la malla 3D sólida. Documentado en `documentacion/modelos_3d.md` para la bóveda de Obsidian. |
| Coordinación con Claude | Establecido canal continuo en `documentacion/COORDINACION.md` donde Claude construye mapas y misiones 2D en `/Users/iinfafer/Proyectos/maisha` y Gemini modela e integra el soporte 3D en `/Users/iinfafer/Proyectos/maisha-revision` sin pisarse ramas ni archivos. |

### Arquitectura 3D sólida de 360° en El Kitovu, ruinas y erradicación de artefactos de agua (2026-10-18, objetivo nocturno)
| Qué | Decisión |
| --- | --- |
| Casas 3D sin fondo plano | Resuelto el problema de ver casas sin fondo al caminar por detrás: `casa_granja.glb` (casona de Mzee Shamba completa en 360°, zócalo perimetral, troncos macizos, tejado a dos aguas con aleros, porche frontal, buhardilla encendida, chimenea y rueda hidráulica con canaleta; pared trasera sólida con ventana). Mapeados también `pozo_antiguo.glb`, `espantapajaros.glb`, `carro_madera.glb` y `valla_madera.glb` para El Kitovu. |
| Ruinas 3D tridimensionales | `casa_pino_ruina.glb` y `forja_ruina.glb` sustituyen a los edificios destruidos en Cuna de Musgo antes de ser reconstruidos (`frame == 0`), de modo que caminar entre ruinas muestra escombros tridimensionales, vigas astilladas y muros caídos reales por los cuatro costados. Al reconstruirse, se sustituyen dinámicamente por la versión intacta. |
| Erradicación de bugs de agua y temblores de movimiento | Erradicado el vacío negro, temblores al caminar y artefactos oscuros: planos geométricamente estables sin deformación dinámica de vértices (`VERTEX.y += h` eliminado en planos móviles para erradicar el z-fighting y la ondulación). Sistema de 3 capas físicas: suelo en $y=0.0\text{ m}$, agua en $y=-0.22\text{ m}$ y lecho continuo en $y=-0.28\text{ m}$. |
| Erradicación del monolito negro en edificios 3D | Los modelos importados de Blender en sombra quedaban negros por el sombreado PBR directo contra luz cenital. Se implementó `_preparar_materiales_modelo` en `espejo_hd2d.gd`: activa `DIFFUSE_LAMBERT_WRAP`, filtrado `NEAREST` y emisión ambiental cálida de base ($44\,\%$ de su color de albedo), preservando los colores vivos de la paleta oficial en todas las caras del edificio tanto al sol como en sombra. |
| Catálogo completo de ruinas 3D (Kitovu, Cuna) | Modeladas en Blender 4.5 e integradas en `MODELOS_BLENDER`: `kitovu_ruina.glb` (para `ruina_casa.png`), `cocina_ruina.glb` (caldero volcado, chimenea rota, escombros) y `puesto_ruina.glb` (mostrador partido, toldo caído y cajas rotas). Tanto antes como después de reconstruirse cada aldea, la escena muestra volumen 3D real desde cualquier ángulo de cámara. |
| Arquitectura sólida de 360° en Cuna y Sigilia | Modelado exhaustivo en Blender 4.5 con geometría cerrada en las 4 caras: `casa_pino.glb` (sombrero con motas, chimenea curva, porche con farol, zócalo de piedra y ventanas traseras redondas), `forja_corteza.glb` (horno con boca arqueada, yunque de doble cuerno sobre tocón, cubeta con agua, leñera trasera), `cocina_juncia.glb`, `puesto_tawi.glb`, `gran_archivo.glb` (podio escalonado, 4 columnas con capiteles, frontón, cúpula y hornacinas traseras), `taller_taa.glb` (entramado en voladizo, gran frasco de tinta, chimenea trasera), `casa_escriba.glb` (muros blancos, sillares de esquina de granito, balcón y chimenea trasera) y `fuente_plaza.glb` (pila octogonal moldurada, fuste de acantos y surtidor de loto). |
| 2026-10-18 | **Texturizado Pixel-Art 360° en Blender y Transparencia Dinámica de Edificios**: Generador procedural de texturas de apoyo (`herramientas/generar_texturas_3d_granja.py`) que crea la fachada trasera de Shamba (`trasera_casa_granja.png`) y tiles continuos de paja dorada, troncos y mampostería. Mapeado UV en `generador_3d_maisha.py` con filtro `Closest`/`NEAREST`. Al caminar Maisha por detrás de cualquier casa, `_actualizar_transparencias_edificios()` en `espejo_hd2d.gd` transiciona el edificio al 38% de alfa, evitando que el personaje quede oculto. | Soluciona la queja de casas que parecían bloques planos o tapaban al personaje. |
| 2026-10-18 | **Sombreador de Agua Translúcida Continua (`SOMBREADOR_AGUA`)**: Separación del agua en un sombreador dedicado espacial con `render_mode blend_mix, depth_draw_always, diffuse_lambert, specular_schlick_ggx`. Profundidad óptica continua (`smoothstep(0.18, 0.72)`), atenuación de alfa suave en orillas (`ALPHA = smoothstep(0.14, 0.28, es_agua)`), refracción tenue y espuma orgánica. Esto erradica el corte abrupto del discard y permite ver el lecho de guijarros a través del agua somera. | Resuelve la solicitud de agua cristalina sin bordes negros ni recortes secos. |
| 2026-10-18 | **Estabilización de Orillas de Agua y Delimitación Quirúrgica de Transparencia (`radio_occlusion`)**: Se eliminó la oscilación dinámica `temblor` del fragmento de suelo en `SOMBREADOR_LEJANO` (el temblor pertenecía solo a la lámina de agua, provocando que las orillas sólidas bailaran y crearan rendijas negras con el movimiento). Se asignó `mat.render_priority = 1` a `_plano_capa`. Se añadió `radio_occlusion: Vector2(ancho, fondo)` individualizado por edificio en `MODELOS_BLENDER`, eliminando de la lista de transparencia a todos los props pequeños (vallas, farolas, espantapájaros, carros, pozos) para evitar que parpadeen o fuercen ordenación alfa al moverse Maisha; y se fijó `DEPTH_DRAW_ALWAYS` durante la transparencia para evitar colapsos visuales entre caras del mismo edificio. | Erradica los bugs visuales al desplazarse el personaje por huertos, caminos y riberas. |
| 2026-10-18 | **Oleadas 1 y 2 de Modelado 3D Sólido (Estructuras de todos los Biomas)**: Modelado procedural en Blender 4.5 e integración en HD-2D de 8 elementos clave: `grua.glb`, `barca.glb`, `estela.glb`, `menhir.glb`, `portal_raiz.glb`, `arco_ruinas.glb`, `altar_corteza.glb` y `balsa.glb`. Corrección del culling de z_index bajo (`z_index < SUELO_BAJO`) para objetos como la balsa y resolución del fallback de ancla en `(0, 0)`. | Expande la arquitectura y elementos sólidos por todos los biomas del mundo. |
| 2026-10-18 | **Oleada 3 de Modelado 3D Sólido y Suite de Verificación de 12 Biomas**: Creación de `brasero.glb` (Sendero Olvidado, trípode forjado, ascuas `#DF9022` y luz puntual vinculada), `maquina_campo.glb` (Campo Segado, caldera de vapor, volante y engranajes) y `raiz_gigante.glb` (El Kitovu, arco de raíz petrificada transitable con nódulos de Asili). Catálogo ampliado a 47 modelos sólidos. Suite `verificar_gameplay_visual.gd` ampliada a 12 biomas con 100% PASS (cero fallos visuales). | Completitud de props sólidos en todo el mundo y garantía de gameplay visual impecable. |
| 2026-10-18 | **Oleada 4 de Modelado 3D Sólido y Suite de Verificación de 13 Biomas**: Creación de `columna.glb` (25 enclaves de ruinas, fuste estriado y capitel con musgo), `muro.glb` (13 tramos de cantería maciza con albardilla biselada), `paca.glb` (26 fardos cilíndricos de paja enrollada y ataduras de cáñamo) y `molino_campo.glb` (molino de viento tradicional de Campo Segado con torre troncocónica, balcón volado y 4 aspas con velamen). Catálogo ampliado a 51 modelos sólidos. Suite `verificar_gameplay_visual.gd` ampliada a 13 biomas (incorporando Prados del Eco) con 100% PASS (cero fallos visuales). | Erradicación del efecto plano en ruinas, murallas y campos agrícolas a lo largo de todo el juego. |
| 2026-10-18 | **Oleada 5 de Modelado 3D Sólido y Suite de Verificación de 15 Biomas**: Creación de `atril_biblioteca.glb` (Estanterías Colgantes, atril de lectura de mármol y bronce con tomo abierto y sigilos índigo luminosos `#4F46E5`), `tocon_bosque.glb` (Bosque Cobrizo, tocón sagrado con anillos de crecimiento, oquedad y hongos de repisa) y `poste_amarre.glb` (Embarcadero Junco, 3 pilotes náuticos atados con cabo grueso y argolla de bronce). Catálogo ampliado a 54 modelos sólidos. Suite `verificar_gameplay_visual.gd` ampliada a 15 biomas con 100% PASS (cero fallos visuales). | Enriquecimiento visual de enclaves bibliotecarios, portuarios y forestales. |
| 2026-10-18 | **Oleada 6 de Modelado 3D Sólido y Suite de Verificación de 18 Biomas**: Creación de `arbol_seco.glb` (reemplaza 491 billboards planos en Kitovu, Campo Segado, Senda de los Surcos y Paso de Piedra por un árbol gnarled petrificado con 3 raíces tabulares, tronco retorcido con fisura y 4 ramas en abanico 360°), `piedra_eco.glb` (reemplaza billboards planos para los 9 Ecos Perdidos del mundo, las 9 Piedras del Recuerdo en Ruinas del Primer Árbol y las piedras del Sendero con un monolito de granito achaflanado, espiral rúnica en bajo relieve y cristal Asili bioluminiscente `#6DB0B0` con emisión 4.5), `bloque_piedra.glb` (reemplaza 47 billboards planos en Cañada del Eco y Paso de Piedra con sillares ciclópeos escalonados, estrato de líquenes alpinos y cantería) y `transbordador.glb` (reemplaza la barca plana de Bata en Embarcadero Junco y La Travesía por una gran barcaza fluvial con casco curvado, roda de proa, timón con caña, cuadernas, norays, cubierta transitable y farol de proa de bronce y ámbar cálido). Catálogo ampliado a 58 modelos sólidos. Suite `verificar_gameplay_visual.gd` ampliada a 18 biomas completos con 100% PASS (cero fallos visuales). | Mayor impacto visual del mundo: eliminación de más de 550 billboards planos en caminos de montaña, ríos navegables y enclaves sagrados. |
| 2026-10-18 | **Oleada 7 de Modelado 3D Sólido y Suite de Verificación de 21 Biomas**: Creación de `roca_grande.glb` (reemplaza 403 billboards planos en montañas, sendero nevado y caminos), `roca_pequena.glb` (reemplaza 498 billboards planos en riberas y praderas), `arbol_muerto.glb` (reemplaza 165 billboards planos en Ciénaga Quieta y Las Pasarelas por troncos huecos con raíces zancudas emergentes del agua y hongos políporos) y `seta_luz.glb` (reemplaza las 24 setas planas de Cueva de las Setas por racimos de setas bioluminiscentes 360° en tonos Asili turquesa `#2DD4BF` y violeta `#A855F7`). Catálogo ampliado a **62 modelos 3D sólidos** (más de 1.000 billboards sustituidos en total). Suite `verificar_gameplay_visual.gd` ampliada a **21 biomas completos** con **100% PASS y cero fallos visuales**. | Hito monumental en la tridimensionalización de Maisha: conversión del 100% de la geología, árboles secos, roquedos y cavernas en objetos con volumen 3D real. |
| 2026-10-19 | **Oleada 11 de Modelado 3D Sólido y Desvanecimientos Dinámicos de Misión**: Creación de `casa_kalamu.glb` (residencia señorial y observatorio del Archivero Kalamu en Maandiko con sillería de mármol, torreón cilíndrico anexo de 3 plantas con chapitel de cobre verdigrís, ventanal ojival de estudio con luz de pergamino `#FDE047`, balcón voladizo con pergaminos colgando, chimenea y rótulo de pluma de escriba), `farol_runico.glb` (farol rúnico ceremonial de Paso de la Escarcha y Sigilia con columna octogonal de roca morada `#334155`, runas de fuego en relieve `#F59E0B`, fanal de cobre con llama eterna viva `#FEF08A` / `#F97316`, caperuza tipo pagoda nevada y argolla), `raiz_tapon.glb` (maraña subterránea en Gruta de las Raíces con 5 troncos entrelazados como portón vivo, zarcillos y nódulos bioluminiscentes de Asili `#9333EA`) y `nudo_corrupcion.glb` (nudo de corrupción de Giza que sella el almacén en Embarcadero Junco con núcleo amatista abisal `#7E22CE` / `#A855F7`, zarzas petrificadas negras `#0F172A`, púas cristalinas `#C084FC` y tentáculos). Integración en `espejo_hd2d.gd` con discriminación dinámica de farol rúnico por script/textura y soporte de desvanecimiento suave de alfa al abrirse atajos o destruir nudos. Catálogo global alcanza **78 modelos 3D sólidos**. Suite `verificar_gameplay_visual.gd` cubre los 23 biomas y 2 interiores con **100% PASS y cero fallos visuales**. | Sustitución de los últimos bloqueos y edificaciones de Sigilia y Raíz por modelos sólidos con soporte de animación de misión. |
| 2026-10-19 | **Oleada 12 de Modelado 3D Sólido y Props de Interacción Dinámica**: Creación de `roca_mineral.glb` (peñasco de esquisto mineralizado en Camino Cobrizo con facetas poligonales, tres cristales prismáticos hexagonales de cobalto/azurita translúcida `#38BDF8` y vetas de cobre nativo `#F59E0B`), `espino_giza.glb` (enemigo fijo escupe-espinas en Gruta de las Raíces con base de raíces negras petrificadas `#0F172A`, bulbo glandular de corrupción `#7E22CE` y aguijón central de cristal violáceo en ristre `#C084FC`), `saco_mercancias.glb` (saco de grano de arpillera gruesa `#B45309` en Embarcadero Junco con soga de cáñamo y boca fruncida; sincronización dinámica de posición tridimensional al ser empujado por el Latido del cetro) y `sello_raices.glb` (gran sello de raíces de Giza en la fachada fluvial de Bata en Embarcadero Junco con troncos gnarled en aspa `#1E1B4B` y amatista abisal palpitante `#7E22CE`). Catálogo global alcanza **82 modelos 3D sólidos**. Suite `verificar_gameplay_visual.gd` (23 biomas + 2 interiores) con **100% PASS y cero fallos visuales**. | Tridimensionalización de la interacción física con sacos y barreras de fachada en Embarcadero Junco, geología mineralizada y centinelas de Gruta. |
| 2026-10-19 | **Oleada 13 de Modelado 3D Sólido y Barreras Biomecánicas de Mazmorra**: Creación de `crater_kitovu.glb` (cráter del impacto primordial de Asili en El Kitovu con berma anular elevada de tierra calcinada `#292524`, lajas angulosas de esquisto `#475569`, falla central fundida con núcleo de cristal Asili dorado incandescente `#DF9022` y esquirlas brillantes `#F59E0B`; corrección de desempaquetado de `CanvasTexture` en `espejo_hd2d.gd`), `cortina_micelio.glb` (gran portón vivo de micelio e hifas en Cueva de las Setas con jambas y dintel de roca `#334155`, 9 cordones trenzados de micelio blanco `#E2E8F0` y 7 vesículas de esporas `#7E22CE` con desvanecimiento al cortarla con el cetro), `espinas_giza.glb` (barrera universal de espinas petrificadas `#0F172A` con núcleo de corrupción `#A855F7` y 12 agujas cristalinas `#581C87`) y `raiz_dormida.glb` (raíz ancestral durmiente colosal de $3.8\text{ m}$ en Gruta de las Raíces con corteza rugosa `#3E1E0F`, nódulos Asili turquesa `#2DD4BF` y ojo durmiente violeta `#7E22CE`). Catálogo global alcanza **86 modelos 3D sólidos**. Suite `verificar_gameplay_visual.gd` (23 biomas + 2 interiores) con **100% PASS y cero fallos visuales**. | Eliminación de billboards planos en cráteres de impacto sagrados, cortinas de micelio de jefes, zarzas de paso y raíces colosales subterráneas. |
| 2026-10-21 | **Oleada 14 de Modelado 3D Sólido y Elementos Interactivos de Huerto y Combate**: Creación de `semilla_dormida.glb` (sagrada Semilla Dormida ancestral en los nichos de Gruta de las Raíces con pedestal de esquisto tallado `#423A4C`, cuna de 4 raíces vivas `#482B1B`, cáscara petrificada `#4A3525` con 4 venas de oro Asili `#DF9022`, núcleo esmeralda bioluminiscente `#76C442` y corona de hojas `#365314`), `rescoldo_giza.glb` (rescoldo ritual en arenas de combate tras vencer a jefes con lecho de cenizas `#3E3444`, brasas ardientes `#EA580C`, anillo de 8 monolitos de basalto quebrado `#423A4E`, espira de llamas violetas `#7E22CE` y núcleo de oro ancestral `#EAB308`), `chatarra_oxidada.glb` (bloque de restos mecánicos en Campo Segado con base de plancha deformada `#442A1D`, remaches `#452A1E`, rueda dentada a 35° `#854D27`, tuerca hexagonal de bronce `#A16207` y biela; soporte dinámico para ocultar `Chatarra_Superior` al fracturarse) y `zanahoria_huerto.glb` (bancal hortícola de Mzee Shamba en El Kitovu con montículo de tierra húmeda `#472C1A`, surcos de labranza `#54331C`, raíz anaranjada `#EA580C` y penacho plumoso `#2F851D`; soporte dinámico para ocultar fruto y hojas al ser cosechada por Maisha). Catálogo global alcanza **90 modelos 3D sólidos**. Suite `verificar_gameplay_visual.gd` (23 biomas + 2 interiores) con **100% PASS y cero fallos visuales**. | Hito en interactividad dinámica: cosecha en tiempo real en huertos, ruptura física de chatarra en jefes y sacralización de nichos y arenas. |
| 2026-10-21 | **Revisión del PR #1 de rendimiento (fer-estrada)**: aceptado (35 pruebas bien, mismo aspecto). Arreglados los dos fallos que avisaba: el Quieto ya sale de las zonas corruptas del Sendero Olvidado (le faltaba `variante`) y el espejo HD-2D ya no se corta cuando desaparece un objeto de pie (`espejo_hd2d.gd`). | Iam: el Quieto debe salir aunque las peleas del Sendero sean algo más difíciles. |




