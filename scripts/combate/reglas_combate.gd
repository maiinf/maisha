class_name ReglasCombate
## TODOS LOS NÚMEROS DEL COMBATE EN UN SOLO SITIO.
## Cambia un valor, guarda y pulsa ⌘ + B para probar cómo se siente.

# --- Casillas -----------------------------------------------------------------
const CASILLA := 16                      # tamaño de una casilla en píxeles

# --- Maisha -------------------------------------------------------------------
const VIDA_MAXIMA := 10                  # bloques (hojas) de vida
const ALIENTO_MAXIMO := 100.0
const INVULNERABLE_TRAS_DANIO := 1.0     # segundos sin recibir daño tras un golpe
const VELOCIDAD_AGOTADA := 0.5           # multiplicador de velocidad mientras jadea
const DURACION_AGOTAMIENTO := 2.0        # segundos jadeando al vaciar el Aliento

# Recuperación de Aliento (por segundo): más rápida sin lanzar semillas y aún más quieta
const ALIENTO_RECUPERA := 10.0
const ALIENTO_RECUPERA_SIN_LANZAR := 14.0
const ALIENTO_RECUPERA_QUIETA := 22.0
const SEGUNDOS_SIN_LANZAR := 1.5

# --- Golpe con el cetro (gratis) -----------------------------------------------
const GOLPE_DANIO := 1
const GOLPE_ALCANCE := 24.0              # píxeles desde el centro de Maisha
const GOLPE_ANGULO := 75.0               # grados a cada lado de hacia donde mira
const GOLPE_ESPERA := 0.32               # segundos entre golpes
const GOLPE_EMPUJE := 150.0
const GOLPE_ATURDE := 0.35               # segundos que el enemigo queda aturdido
const GOLPE_RECARGA_ALIENTO := 6.0       # Aliento que recupera cada golpe que acierta
const GOLPE_FRENA := 0.4                 # Maisha se mueve más despacio mientras golpea
const CETRO_TEMPLADO_ALCANCE := 1.35     # con el cetro templado por Corteza, el golpe llega más lejos

# --- Semilla (gasta Aliento) ---------------------------------------------------
const SEMILLA_COSTE := 25.0
const SEMILLA_MECHA := 1.5               # segundos hasta estallar (con 2,5 s los enemigos escapaban)
const SEMILLA_RAICES := 20.0             # la semilla atrapa con raíces a los enemigos a esta distancia (píxeles)
const SEMILLA_ALCANCE := 2               # casillas en cada dirección (explosión en cruz)
const EXPLOSION_DANIO := 3
const EXPLOSION_AUTODANIO := 1           # daño a la propia Maisha si la pilla
const BROTES_DURAN := 5.0                # segundos que duran los brotes

# --- Latido (gasta Aliento) ----------------------------------------------------
const LATIDO_COSTE := 35.0
const LATIDO_ESPERA := 2.5
const LATIDO_RADIO := 30.0
const LATIDO_EMPUJE := 260.0
const LATIDO_INVULNERABLE := 0.5

# --- Petrino (enemigo común de Raíz) --------------------------------------------
const PETRINO_VIDA := 3
const PETRINO_VELOCIDAD := 30.0
const PETRINO_VE_A := 120.0              # distancia a la que persigue a Maisha
const PETRINO_DANIO := 1

# --- Núcleo de Giza -----------------------------------------------------------
const NUCLEO_VIDA := 3                   # solo le hacen daño las explosiones
const NUCLEO_VIDA_PEQUENO := 2           # el Corazón de las zonas de práctica
const NUCLEO_MAX_ENEMIGOS := 3
const NUCLEO_INVOCA_CADA := 6.0          # segundos entre enemigos nuevos


## Casilla (coordenadas enteras) en la que está un punto del mundo
static func casilla_de(punto: Vector2) -> Vector2i:
	return Vector2i(floori(punto.x / CASILLA), floori(punto.y / CASILLA))


## Centro de una casilla en el mundo
static func centro_de(casilla: Vector2i) -> Vector2:
	return Vector2(casilla) * CASILLA + Vector2.ONE * CASILLA / 2.0

# --- Mzizi, la raíz del Arco (miniboss del Kitovu) -----------------------------
const MZIZI_VIDA := 6                    # semillas que hay que acertarle (cada una que le alcance cuenta)
const MZIZI_DOLOR_GOLPEABLE := 0.6       # cada estallido la deja fuera, retorciéndose, al menos esto más
const MZIZI_ASOMA_GOLPEABLE := 0.3       # le alcanza una semilla mientras asome al menos esta parte (0 a 1)
const MZIZI_ESCONDIDO := 1.3             # segundos bajo tierra entre salida y salida
const MZIZI_AVISO := 1.25                # segundos que avisa el agujero antes de salir (fase 2: menos)
const MZIZI_AVISO_FASE2 := 0.9
const MZIZI_FUERA := 2.8                 # segundos fuera, escupiendo piedras
const MZIZI_PIEDRA_VELOCIDAD := 95.0
const MZIZI_PIEDRA_DANIO := 1
const MZIZI_SALIDA_DANIO := 1            # daño si Maisha está encima del agujero cuando sale
const MZIZI_PETRINOS_FASE2 := 2          # Petrinos que llama al meterse (en la fase 2)

# --- Pembe, el ciervo de hierro (minijefe del Bosque Cobrizo) ---------------------
const PEMBE_VIDA := 8                    # golpes del cetro (1) y semillas (2) mientras está atascado
const PEMBE_ANDA := 26.0                 # velocidad al acechar
const PEMBE_ACECHA := 1.8                # segundos acechando antes de prepararse (fase 2: menos)
const PEMBE_PREPARA := 0.9               # segundos escarbando: la línea roja marca por dónde va a ir
const PEMBE_PREPARA_FASE2 := 0.6
const PEMBE_EMBISTE := 200.0             # velocidad de la embestida
const PEMBE_ATASCADO := 2.8              # segundos con las astas clavadas en un árbol (¡el momento de atacar!)
const PEMBE_ATURDIDO := 0.8              # si choca con el borde de la arena (sin árbol): se repone enseguida
const PEMBE_DANIO := 2                   # si atropella a Maisha
const PEMBE_ASTAS_FASE2 := 4             # trozos de hierro que caen del cielo al soltarse (fase 2)
const PEMBE_SEMILLA_DANIO := 2

# --- Konokono, la caracola de óxido (minijefe de la Ciénaga Quieta) -----------------
const KONOKONO_VIDA := 8
const KONOKONO_VELOCIDAD := 16.0         # se arrastra hacia Maisha
const KONOKONO_TRAGA_A := 18.0           # se traga las semillas que pilla con la boca o al pasar por encima
const KONOKONO_DANIO_DENTRO := 2         # una semilla que le estalla dentro
const KONOKONO_ATURDIDA := 2.6           # segundos fuera de la concha, mareada: el cetro le quita 1
const KONOKONO_ESCONDIDA := 1.6          # al recibir un golpe sin estar mareada, se esconde
const KONOKONO_RUEDA := 170.0            # fase 2: se esconde y rueda
const KONOKONO_ESCUPE := 3               # fase 2: bolas de óxido que escupe

# --- La rana de piedra (Las Pasarelas): salta hacia Maisha y queda atontada al caer --------------
const RANA_VIDA := 3
const RANA_VE := 110.0                 # a esta distancia (píxeles) se fija en Maisha
const RANA_AGAZAPA := 0.7              # segundos agazapada (aviso: sombra en el suelo donde caerá)
const RANA_VUELO := 0.6                # segundos en el aire (no se le puede dar)
const RANA_ONDA := 18.0                # radio del golpe al caer
const RANA_ATONTADA := 1.3             # tras caer: el cetro le quita 2
const RANA_ESPERA := 1.2               # entre salto y salto
## Topo de piedra (Camino Cobrizo): va bajo tierra hacia Maisha, avisa y sale de golpe mordiendo
const TOPO_VIDA := 3
const TOPO_VE := 130.0                 # a esta distancia (píxeles) la oye y va a por ella
const TOPO_VELOCIDAD := 58.0           # bajo tierra (Maisha va más deprisa: se le puede dar esquinazo)
const TOPO_BUSCA := 2.4                # segundos como mucho persiguiéndola bajo tierra
const TOPO_AVISO := 0.55               # el suelo tiembla y se agrieta donde va a salir
const TOPO_MORDISCO := 16.0            # radio del mordisco al salir
const TOPO_ATONTADO := 1.4             # fuera, mareado tras salir: ahí el cetro le quita 2
const TOPO_ESPERA := 1.0               # bajo tierra, quieto, antes de volver a buscar
## Cuervo de óxido (Senda de los Surcos): vuela en círculos, apunta (raya en el suelo) y se lanza en picado
const CUERVO_VIDA := 3
const CUERVO_VE := 110.0               # a esta distancia (píxeles) se fija en Maisha
const CUERVO_ALTURA := 30.0            # lo alto que vuela (no se le puede dar)
const CUERVO_VUELO := 70.0             # velocidad dando vueltas
const CUERVO_APUNTA := 0.75            # segundos apuntando (la raya del suelo avisa)
const CUERVO_PICADO := 230.0           # velocidad del picado (píxeles por segundo)
const CUERVO_POSADO := 1.4             # posado picoteando tras el picado: el cetro le quita 2
const CUERVO_ESPERA := 1.3             # dando vueltas antes de volver a apuntar
## Lago Espejo: segundos que Maisha tiene que estar quieta junto al agua para que el lago se vuelva espejo
const QUIETUD_SEGUNDOS := 3.0
## Murciélago de eco (Cañada del Eco): revolotea, avisa y grita una onda que va y vuelve; al tragársela, cae aturdido
const MURCIELAGO_VIDA := 3
const MURCIELAGO_VE := 120.0           # a esta distancia (píxeles) se fija en Maisha
const MURCIELAGO_ALTURA := 20.0        # lo alto que revolotea (no se le puede dar)
const MURCIELAGO_VUELO := 85.0         # velocidad revoloteando (a tirones)
const MURCIELAGO_DESPIERTA := 0.7      # colgado, antes de echar a volar
const MURCIELAGO_ESPERA := 1.4         # revoloteando antes de avisar
const MURCIELAGO_AVISO := 0.8          # segundos avisando (anillo y línea en el suelo)
const MURCIELAGO_ALCANCE := 120.0      # lo lejos que llega la onda antes de volver
const MURCIELAGO_ONDA := 150.0         # velocidad de la onda (píxeles por segundo)
const MURCIELAGO_ONDA_RADIO := 11.0    # lo cerca que tiene que pasar la onda para hacer daño
const MURCIELAGO_ATURDIDO := 1.6       # en el suelo, mareado por su propio eco: el cetro le quita 2

# --- La Cosechadora Oxidada (jefe de Raíz, en el Campo Segado) --------------------
# Se rompe POR PARTES: la caldera (atrás), el depósito frontal y el depósito del techo. Con las tres rotas,
# se desploma y deja al aire el CORAZÓN de Giza, que hay que romper esquivando sus anillos de fuego.
const COSECHADORA_PARTES := {"caldera": 4, "frontal": 3, "techo": 3, "corazon": 3}
const COSECHADORA_VIDA := 13              # la suma de todas las partes (la barra de vida)
const COSECHADORA_VELOCIDAD := [48.0, 64.0, 76.0, 90.0]   # por etapa de Ira: Calma, Enfado, Furia, Frenesí (+40 %)
const COSECHADORA_GIRO := 98.0              # velocidad al cambiar de fila
const COSECHADORA_IRA_RITMO := 2.5         # Ira por segundo (25 = una etapa: unos 10 s)
const COSECHADORA_ATASCADA := 4.0          # segundos enredada en los brotes con la caldera abierta
const COSECHADORA_CHOQUE := 1.6            # segundos aturdida tras estrellarse contra el borde (depósito frontal al aire)
const COSECHADORA_CUCHILLAS := 2           # daño de las cuchillas de delante
const COSECHADORA_SEMILLA_DANIO := 2       # una semilla que estalla junto a una parte al aire
const COSECHADORA_EMBESTIDA := 245.0       # Frenesí: embiste por la fila de Maisha
const COSECHADORA_TUERCAS_CADA := 4.3      # Enfado o más: lanza tuercas que dejan BLOQUES DE CHATARRA
const COSECHADORA_CHATARRA_DURA := 14.0
const COSECHADORA_BABOSAS_CADA := 6.0      # Furia o más
const COSECHADORA_FRENESI_DURA := 9.0     # segundos en Frenesí hasta que se sobrecalienta
const COSECHADORA_RESOPLA := 3.5           # sobrecalentada: quieta soltando vapor (el techo, al aire)
const COSECHADORA_BORDE_MIN := 0.78        # Furia: Giza cierra la arena desde el borde hasta aquí (0..1)
# El ACELERÓN INFERNAL: avisa con una franja, acelera en línea recta y deja un rastro de fuego de Giza.
# Cuanto más Ira, más a menudo, más rápido, más dura el fuego y más ancho es el rastro (por etapa):
const COSECHADORA_ACELERON_CADA := [7.0, 5.6, 4.2, 2.8]           # segundos entre acelerones
const COSECHADORA_ACELERON_VEL := [182.0, 210.0, 240.0, 277.0]    # velocidad del acelerón
const COSECHADORA_ACELERON_AVISO := [0.7, 0.6, 0.5, 0.4]          # segundos de aviso antes de salir
const COSECHADORA_FUEGO_DURA := [3.0, 4.5, 6.0, 8.0]              # segundos que arde el rastro
const COSECHADORA_FUEGO_ANCHO := [1, 1, 3, 3]                     # filas de casillas que quema a la vez
const COSECHADORA_ESTAMPADA := 1.5        # si acelera contra unos brotes, se queda atascada este rato de más
# El CORAZÓN al aire: anillos de fuego que salen de la máquina, con dos huecos que giran
const COSECHADORA_ANILLO_CADA := [2.4, 2.0]   # segundos entre anillos (al principio, con el corazón tocado)
const COSECHADORA_ANILLO_VEL := 90.0          # px/s
const COSECHADORA_ANILLO_HUECO := 50.0        # grados de cada hueco
