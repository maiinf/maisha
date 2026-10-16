extends Node2D
## REGIÓN: construye una zona del mundo a partir de su mapa de texto (datos/mapas/<mapa>.json).
##   - el suelo (dibujo generado por herramientas/construir_mapa.py)
##   - árboles, rocas, ruinas... con su colisión y su sombra
##   - zonas corruptas (con su estatua, si la tienen), matorrales, piedras-eco, secretos y carteles
##   - la aldea: el Gran Árbol, los edificios, farolillos, vallas y aldeanos
##   - las puertas a otras escenas
##   - el agua (no se puede pisar, salvo los puentes)
## Todo lo del mundo comparte el material de corrupción: empieza gris y recupera el color al purgar.
## Lo que ya ha pasado (zonas purgadas, secretos recogidos...) se consulta en Estado.

signal secreto_encontrado(cuantos: int, total: int)

const R := preload("res://scripts/combate/reglas_combate.gd")
const ZONA := preload("res://scripts/combate/zona_corrupta.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const MATORRAL := preload("res://scripts/mundo/objetos/matorral.gd")
const PIEDRA_ECO := preload("res://scripts/mundo/objetos/piedra_eco.gd")
const ROCA_MOVIL := preload("res://scripts/mundo/objetos/roca_movil.gd")
const ESENCIA := preload("res://scripts/mundo/objetos/esencia.gd")
const CARTEL := preload("res://scripts/mundo/objetos/cartel.gd")
const ESTATUA := preload("res://scripts/mundo/objetos/estatua.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ROCA_MINERAL := preload("res://scripts/mundo/objetos/roca_mineral.gd")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const GRAN_ARBOL := preload("res://scripts/mundo/aldea/gran_arbol.gd")
const EDIFICIO := preload("res://scripts/mundo/aldea/edificio.gd")
const FAROL := preload("res://scripts/mundo/aldea/farol.gd")
const ALDEANO := preload("res://scripts/mundo/aldea/aldeano.gd")
const PORTAL := preload("res://scripts/mundo/kitovu/portal.gd")
const CASA_GRANJA := preload("res://scripts/mundo/kitovu/casa_granja.gd")
const ZANAHORIA := preload("res://scripts/mundo/kitovu/zanahoria.gd")
const TRONCO := preload("res://scripts/mundo/kitovu/tronco.gd")
const CERCA_ROTA := preload("res://scripts/mundo/kitovu/cerca_rota.gd")
const SITIO_PESCA := preload("res://scripts/mundo/kitovu/sitio_pesca.gd")
const ESPANTAPAJAROS := preload("res://scripts/mundo/kitovu/espantapajaros.gd")
const COSA := preload("res://scripts/mundo/objetos/cosa.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const ESPINAS_PASO := preload("res://scripts/mundo/objetos/espinas_paso.gd")
const TRONCO_PODRIDO := preload("res://scripts/mundo/objetos/tronco_podrido.gd")
const BOSQUE := "res://arte/mundos/raiz/bosque/"
const CIENAGA := "res://arte/mundos/raiz/cienaga/"
const CAMPO := "res://arte/mundos/raiz/campo/"
const CANADA := "res://arte/mundos/raiz/canada/"
const LAGO := "res://arte/mundos/raiz/lago/"
const EMBARCADERO := "res://arte/mundos/raiz/embarcadero/"
const PASO := "res://arte/mundos/raiz/paso/"
const MECERSE := preload("res://scripts/mundo/objetos/mecerse.gd")
const GALLINA := preload("res://scripts/mundo/kitovu/gallina.gd")
const OBJ := "res://arte/mundos/raiz/objetos/"
const KITOVU := "res://arte/mundos/kitovu/"
const ALDEA := "res://arte/mundos/raiz/aldea/"
const SENDERO := "res://arte/mundos/raiz/sendero/"
const ECO_PERDIDO := preload("res://scripts/mundo/objetos/eco_perdido.gd")
const FOGATA := preload("res://scripts/mundo/objetos/fogata.gd")

## Objetos fijos: letra -> [dibujo, tamaño de la colisión, ancho de la sombra]
const FIJOS := {
	"T": [OBJ + "arbol_a.png", Vector2(8, 5), 12.0],
	"t": [OBJ + "arbol_b.png", Vector2(8, 5), 12.0],
	"R": [OBJ + "roca_grande.png", Vector2(16, 8), 10.0],
	"r": [OBJ + "roca_pequena.png", Vector2(10, 5), 6.0],
	"C": [OBJ + "columna.png", Vector2(9, 5), 6.0],
	"W": [OBJ + "muro.png", Vector2(22, 6), 12.0],
	"v": [ALDEA + "valla.png", Vector2(16, 4), 0.0],
	"d": [KITOVU + "arbol_seco.png", Vector2(6, 4), 7.0],
	# del Sendero Olvidado: pinos nevados y rocas con nieve (dos formas cada uno)
	"ğ": ["res://arte/mundos/raiz/olvidado/pino_nevado.png", Vector2(8, 5), 12.0, 2],
	"ň": ["res://arte/mundos/raiz/olvidado/roca_nevada.png", Vector2(16, 7), 11.0, 2],
	# del Kitovu, con [fotogramas (variantes), charla al usarlo, radio]
	"A": [KITOVU + "ruina_casa.png", Vector2(50, 12), 0.0, 2, "kitovu_ruina", 34.0],
	"B": [KITOVU + "pozo.png", Vector2(24, 10), 13.0, 1, "kitovu_pozo", 24.0],
	"D": [KITOVU + "torre.png", Vector2(32, 14), 18.0, 1, "kitovu_torre", 30.0],
	"F": [KITOVU + "monumento.png", Vector2(30, 12), 18.0, 1, "kitovu_monumento", 30.0],
	"N": [KITOVU + "raiz_gigante.png", Vector2(86, 10), 0.0, 2, "kitovu_raiz_gigante", 52.0],
	"V": [KITOVU + "carro.png", Vector2(36, 10), 16.0, 1, "kitovu_carro", 26.0],
	"i": [KITOVU + "farol_apagado.png", Vector2(4, 4), 4.0],
	# del Bosque Cobrizo
	"J": [BOSQUE + "arbol_cobre.png", Vector2(9, 5), 14.0, 2],
	"j": [BOSQUE + "arbol_rojizo.png", Vector2(9, 5), 14.0, 2],
	"I": [BOSQUE + "arbol_alto.png", Vector2(7, 5), 11.0, 2],
	"H": [BOSQUE + "tocon.png", Vector2(16, 6), 11.0, 1, "bosque_tocon", 22.0],
	# de la Ciénaga Quieta
	"s": [CIENAGA + "sauce.png", Vector2(10, 5), 15.0, 2],
	"x": [CIENAGA + "arbol_muerto.png", Vector2(8, 5), 9.0, 2],
	# del Campo Segado
	"[": [CAMPO + "granero.png", Vector2(100, 14), 0.0, 1, "campo_granero", 54.0],
	"]": [CAMPO + "molino.png", Vector2(40, 12), 22.0, 1, "campo_molino", 36.0],
	"&": [CAMPO + "maquina.png", Vector2(38, 8), 20.0, 2, "campo_maquina", 28.0],
	"+": [CAMPO + "paca.png", Vector2(14, 6), 8.0, 2],
	# de la Cañada del Eco
	"ñ": [CANADA + "bloque.png", Vector2(24, 9), 16.0, 3],
	"ç": [CANADA + "tronco.png", Vector2(34, 7), 16.0, 2],
	# del Lago Espejo
	"þ": [LAGO + "barca.png", Vector2(40, 8), 22.0, 1, "lago_barca", 30.0],
	"ð": [LAGO + "altar.png", Vector2(24, 8), 14.0, 1, "lago_altar", 26.0],
	"ø": [LAGO + "menhir.png", Vector2(10, 6), 8.0, 3],
	# del Embarcadero Junco (el transbordador: 0 varado, 1 arreglado, según la marca «transbordador_listo»)
	"æ": [EMBARCADERO + "casa_juncos.png", Vector2(40, 10), 0.0, 2, "embarcadero_casa", 30.0],
	"å": [EMBARCADERO + "grua.png", Vector2(30, 10), 0.0, 1, "embarcadero_grua", 34.0],
	"œ": [EMBARCADERO + "almacen.png", Vector2(100, 16), 0.0, 1, "embarcadero_almacen", 50.0],
	"ß": [EMBARCADERO + "transbordador.png", Vector2(140, 16), 0.0, 3, "embarcadero_transbordador", 70.0],
	"ł": [EMBARCADERO + "poste.png", Vector2(12, 7), 8.0, 2],
	# del Paso de Piedra (la casa de Nungu: su puerta, «ď», lleva dentro)
	"ĥ": [PASO + "casa_nungu.png", Vector2(124, 14), 0.0, 1],
	"ĉ": [PASO + "bloque.png", Vector2(22, 8), 14.0, 2],
	# SIGILIA · del Paso de la Escarcha: las estelas rúnicas (cobijan del viento)
	"ȩ": ["res://arte/mundos/sigilia/paso/estela.png", Vector2(14, 6), 10.0, 2],
}
## La casa del viajero de cada camino («{»): [dibujo, colisión, charla al usarla, radio, hoguera]
const CAMPAMENTOS := {
	"msafiri": [SENDERO + "campamento.png", Vector2(72, 10), "sendero_campamento", 40.0, true],
	"korongo": ["res://arte/mundos/raiz/pasarelas/palafito.png", Vector2(88, 12), "pasarelas_palafito", 46.0, false],
	"fuko": ["res://arte/mundos/raiz/camino/madriguera.png", Vector2(96, 14), "camino_madriguera", 50.0, false],
	"sungura": ["res://arte/mundos/raiz/senda/horreo.png", Vector2(84, 12), "senda_horreo", 46.0, false],
	"mbuzi": ["res://arte/mundos/raiz/canada/aprisco.png", Vector2(124, 20), "canada_aprisco", 56.0, false],
	"kasia": ["res://arte/mundos/raiz/orilla/casa_barcas.png", Vector2(100, 14), "orilla_casa_barcas", 54.0, false],
	"bata": ["res://arte/mundos/raiz/embarcadero/casa_bata.png", Vector2(60, 12), "embarcadero_casa_bata", 46.0, false],
}
## Edificios de la aldea: letra -> [id, dibujo, tamaño de la colisión]
const EDIFICIOS := {
	"h": ["casa_seta", ALDEA + "casa_seta.png", Vector2(60, 14)],
	"f": ["taller", ALDEA + "taller.png", Vector2(100, 16)],
	"k": ["cocina", ALDEA + "cocina.png", Vector2(76, 14)],
	"n": ["puesto", ALDEA + "puesto.png", Vector2(84, 10)],
}
## Aldeanos: letra -> [id, marca que hace falta para que esté, marca que lo hace irse, edificio al que se va]
const ALDEANOS := {
	"b": ["bibi", "", "", ""],
	"p": ["pino", "rescatado_pino", "", ""],
	"o": ["corteza", "rescatado_corteza", "construido_taller", "taller"],
	"a": ["tawi", "rescatado_tawi", "", ""],
	"?": ["juncia", "rescatado_juncia", "", ""],
}
const DIRECCIONES := {"arriba": Vector2.UP, "abajo": Vector2.DOWN, "izquierda": Vector2.LEFT, "derecha": Vector2.RIGHT}

@export var mapa := "prados_del_eco"
## El mundo al que pertenece el mapa: su suelo está en res://arte/mundos/<mundo>/suelos/
@export var mundo := "raiz"
## Cuánto decorado hay por la hierba (0 = nada)
@export var densidad_decorado := 0.3
@export var nombre_region := "Prados del Eco"
@export var entidades: NodePath
@export var textos_carteles: Array[String] = ["→ Cuna de Musgo"]
## Los enemigos que salen en las zonas de esta región (se turnan)
@export var tipos_enemigo: PackedStringArray = ["petrino"]
## En los caminos: el viajero que vive aquí («}», con su casa «{») y lo que se recoge con «`» para su encargo
@export var viajero := "msafiri"
@export var objeto_encargo := "pagina"
## (en los lugares) el «}» solo aparece con esta marca: p. ej. Mdiria, cuando ya se le ha rescatado
@export var viajero_requiere := ""
## Si el agua no se puede pisar (en La Travesía no: Maisha va en el transbordador, que la sujeta a su cubierta)
@export var agua_solida := true

var inicio := Vector2.ZERO               # donde despierta Maisha
var tam := Vector2.ZERO                  # tamaño del mapa en píxeles
var secretos_total := 0
var secretos_encontrados := 0

var _entidades: Node2D
var _gestor: Node
const DECORADO := preload("res://scripts/mundo/decorado.gd")
var _filas: PackedStringArray = []
var _marca_espinas := ""                 # la marca que marchita las espinas «!» de este mapa


func _ready() -> void:
	add_to_group("region")
	_entidades = get_node(entidades)
	_gestor = get_tree().get_first_node_in_group("corrupcion")
	var datos: Dictionary = (load("res://datos/mapas/%s.json" % mapa) as JSON).data
	for f in datos["filas"]:
		_filas.append(String(f))
	tam = Vector2(_filas[0].length(), _filas.size()) * R.CASILLA
	_crear_suelo()
	_crear_decorado(datos["zonas"])
	_crear_objetos(datos["zonas"])
	_crear_puertas(datos.get("puertas", {}))
	for pos in _espinas_pendientes:
		var espinas: Node2D = ESPINAS_PASO.new()
		espinas.marca = _marca_espinas
		_poner(espinas, pos)
	_crear_agua()
	_crear_pretiles()
	if not _tablas_rotas.is_empty():
		# «"»: en Las Pasarelas, un tramo de pasarela hundido; en el Camino Cobrizo, el derrumbe de la galería
		# (en la Senda de los Surcos, el foso de agua que Sungura vacía; en la Cañada del Eco, la escala de cuerda)
		var rota: Node2D
		match viajero:
			"fuko":
				rota = DERRUMBE.new()
				rota.marca = "derrumbe_despejado/" + mapa
			"sungura":
				rota = ACEQUIA_FOSO.new()
				rota.marca = "acequia_vaciada/" + mapa
			"mbuzi":
				rota = ESCALA_CUERDA.new()
				rota.marca = "escala_descolgada/" + mapa
			"kasia":
				rota = BALSA.new()
				rota.marca = "balsa_arreglada/" + mapa
			_:
				rota = PASARELA_ROTA.new()
				rota.marca = "pasarela_reparada/" + mapa
		rota.casillas = _tablas_rotas
		add_child(rota)
	_crear_puentes_reflejo()
	_crear_riscos()
	_crear_limites()
	for piedra in get_tree().get_nodes_in_group("piedras_eco"):
		piedra.encendida.connect(_al_encender_piedra)
	# el escondite de las piedras-eco ya se abrió en otra visita
	if Estado.tiene("escondite/" + mapa):
		for piedra in get_tree().get_nodes_in_group("piedras_eco"):
			piedra.encender_sin_aviso()
		for roca in get_tree().get_nodes_in_group("rocas_moviles"):
			roca.apartarse(true)


func _crear_suelo() -> void:
	var suelo := Sprite2D.new()
	suelo.name = "Suelo"
	suelo.texture = load("res://arte/mundos/%s/suelos/%s_suelo.png" % [mundo, mapa])
	suelo.centered = false
	suelo.z_index = -10
	add_child(suelo)
	_gestor.aplicar_a(suelo)


## Detalles pequeños por la hierba (hierba alta, flores, setas...), lejos de las zonas corruptas
func _crear_decorado(zonas: Dictionary) -> void:
	var prohibidas := {}
	for y in _filas.size():
		for x in _filas[y].length():
			var c := _filas[y][x]
			if zonas.has(c):
				var z: Dictionary = zonas[c]
				var rx: int = int(z["radios"][0]) + int(z["borde"]) + 2
				var ry: int = int(z["radios"][1]) + int(z["borde"]) + 2
				for dy in range(-ry, ry + 1):
					for dx in range(-rx, rx + 1):
						prohibidas[Vector2i(x + dx, y + dy)] = true
	var decorado: Node2D = DECORADO.new()
	decorado.name = "Decorado"
	decorado.densidad = densidad_decorado
	decorado.preparar(_filas, prohibidas)
	add_child(decorado)
	_gestor.aplicar_a(decorado)


func _base(x: int, y: int) -> Vector2:
	# los objetos se apoyan en la parte de abajo de su casilla
	return Vector2(x * R.CASILLA + 8, y * R.CASILLA + 14)


## Zonas de práctica: cada partida salen PRACTICAS_POR_PARTIDA de las que haya en el mapa,
## cada una con una de sus formas. La elección se guarda con la partida.
const PRACTICAS_POR_PARTIDA := 3
const FORMAS_POR_PRACTICA := 3


func _elegir_practicas(zonas: Dictionary) -> void:
	if Estado.tiene("practica/" + mapa):
		return
	var claves: Array = []
	for clave in zonas:
		if String(zonas[clave].get("grupo", "")) == "practica":
			claves.append(clave)
	if claves.is_empty():
		return
	claves.shuffle()
	for clave in claves.slice(0, PRACTICAS_POR_PARTIDA):
		Estado.marcar("practica/%s/%s/%d" % [mapa, clave, randi() % FORMAS_POR_PRACTICA])
	Estado.marcar("practica/" + mapa)


## La forma elegida para una zona de práctica (-1 si esta partida no le toca salir)
func _forma_de_practica(clave: String) -> int:
	for v in FORMAS_POR_PRACTICA:
		if Estado.tiene("practica/%s/%s/%d" % [mapa, clave, v]):
			return v
	return -1


var _espinas_pendientes: Array[Vector2] = []
var _tablas_rotas: Array[Vector2i] = []
var _reflejos: Array[Vector2i] = []
var _sitio_viajero := Vector2.INF        # dónde está el «}» (si el aldeano de piedra de una zona es el viajero, va allí)      # «\»: lo que solo existe en el reflejo del lago (puentes de luz)
const PUENTE_REFLEJO := preload("res://scripts/mundo/objetos/puente_reflejo.gd")
const PASARELA_ROTA := preload("res://scripts/mundo/objetos/pasarela_rota.gd")
const DERRUMBE := preload("res://scripts/mundo/objetos/derrumbe.gd")
const ACEQUIA_FOSO := preload("res://scripts/mundo/objetos/acequia_foso.gd")
const ESCALA_CUERDA := preload("res://scripts/mundo/objetos/escala_cuerda.gd")
const BALSA := preload("res://scripts/mundo/objetos/balsa.gd")


func _crear_objetos(zonas: Dictionary) -> void:
	_elegir_practicas(zonas)
	var carteles := 0
	for y in _filas.size():
		var fila := _filas[y]
		for x in fila.length():
			var c := fila[x]
			var pos := _base(x, y)
			if FIJOS.has(c):
				var desvio := Vector2.ZERO
				if c in "JjIsx":
					# en el bosque, los árboles no van en filas: cada uno un poco movido (siempre igual)
					desvio = Vector2(((x * 73 + y * 31) % 9) - 4, ((x * 17 + y * 53) % 7) - 3)
				var variante := x * 3 + y
				if c == "ß":
					variante = 1 if Estado.tiene("transbordador_listo") else (2 if Estado.tiene("boquete_tapado") else 0)
				elif c == "ł":
					variante = 0                    # (los postes, enteros: Mamba los muerde)
				var fijo := _fijo(FIJOS[c], pos + desvio, variante)
				if c in "TtJjIdsx":
					fijo.add_to_group("arboles")
				elif c == "ł":
					fijo.add_to_group("postes")

			elif c == "{":
				var casa: Array = CAMPAMENTOS.get(viajero, CAMPAMENTOS["msafiri"])
				_fijo([casa[0], casa[1], 0.0, 1, casa[2], casa[3]], pos, 0)
				if casa[4]:
					# la hoguera del campamento, delante de la tienda (bajo el trípode del cazo)
					_poner(FOGATA.new(), pos + Vector2(26, -1))
			elif c == "}":
				var viaj: StaticBody2D = ALDEANO.new()
				viaj.id = viajero
				viaj.requiere = viajero_requiere
				_sitio_viajero = pos
				_poner(viaj, pos)
			elif c == "\"":
				_tablas_rotas.append(Vector2i(x, y))
			elif c == "\\":
				_reflejos.append(Vector2i(x, y))
			elif c == "y":
				var trigo: Sprite2D = MECERSE.new()
				trigo.texture = load(KITOVU + "trigo.png")
				trigo.desfase = float(x * 5 + y * 3) * 0.37
				_poner(trigo, pos + Vector2(int(pos.y) % 5 - 2, 0))
				_gestor.aplicar_a(trigo)
			elif c == "c":
				_poner(GALLINA.new(), pos)
			elif c == "M":
				_poner(MATORRAL.new(), pos)
			elif c == "E":
				_poner(PIEDRA_ECO.new(), pos)
			elif c == "@":
				var eco: StaticBody2D = ECO_PERDIDO.new()
				eco.id = mapa
				_poner(eco, pos)
			elif c == "`":
				var pagina: Node2D = RECOGIBLE.new()
				pagina.objeto = objeto_encargo
				pagina.marca = "recogido/%s/%d,%d" % [mapa, x, y]
				pagina.color_halo = Color(0.95, 0.88, 0.62)
				_poner(pagina, pos)
			elif c == "Q":
				_poner(ROCA_MOVIL.new(), pos)
			elif c == "X":
				_crear_secreto(Vector2i(x, y), pos)
			elif c == "u":
				var seta: Node2D = RECOGIBLE.new()
				seta.objeto = "seta_luminosa"
				seta.marca = "recogido/%s/%d,%d" % [mapa, x, y]
				_poner(seta, pos)
			elif c == "Y":
				var roca: StaticBody2D = ROCA_MINERAL.new()
				roca.marca = "roca/%s/%d,%d" % [mapa, x, y]
				_poner(roca, pos)
			elif c == "L":
				var cartel: Node2D = CARTEL.new()
				cartel.texto = textos_carteles[mini(carteles, textos_carteles.size() - 1)]
				carteles += 1
				_poner(cartel, pos)
			elif c == "S":
				inicio = pos
			elif c == "G":
				_poner(GRAN_ARBOL.new(), pos)
			elif EDIFICIOS.has(c):
				var def: Array = EDIFICIOS[c]
				var edificio: StaticBody2D = EDIFICIO.new()
				edificio.id = def[0]
				edificio.textura = load(def[1])
				edificio.colision = def[2]
				_poner(edificio, pos)
			elif c == "l":
				_poner(FAROL.new(), pos)
			elif c == "K":
				_poner(CASA_GRANJA.new(), pos)
			elif c == "z":
				var zanahoria: Node2D = ZANAHORIA.new()
				zanahoria.marca = "recogido/%s/%d,%d" % [mapa, x, y]
				_poner(zanahoria, pos)
			elif c == "Z":
				_poner(TRONCO.new(), pos)
			elif c == "q":
				_poner(CERCA_ROTA.new(), pos)
			elif c == "w":
				var pesca: Node2D = SITIO_PESCA.new()
				pesca.estanque = Rect2(-118, -46, 104, 46)
				_poner(pesca, pos)
			elif c == "e":
				_poner(ESPANTAPAJAROS.new(), pos)
			elif c == "O":
				var crater := Sprite2D.new()
				crater.texture = load(KITOVU + "crater.png")
				crater.position = pos + Vector2(0, -12)
				crater.z_index = -5
				_gestor.aplicar_a(crater)
				add_child(crater)
				var cosa: Node2D = COSA.new()
				cosa.charla = "kitovu_crater"
				cosa.radio_interaccion = 30.0
				cosa.position = pos + Vector2(0, -10)
				add_child(cosa)
			elif c == "m":
				_adorno(ALDEA + "setitas.png", 2, (x * 7 + y * 3) % 2, pos)
			elif c == "g":
				_adorno(BOSQUE + "helecho.png", 2, (x * 5 + y * 3) % 2, pos)
			elif c == ";":
				_adorno(CIENAGA + "juncos.png", 2, (x * 7 + y) % 2, pos)
			elif c == "*":
				var nenufar := Sprite2D.new()
				nenufar.texture = load(CIENAGA + "nenufar.png")
				nenufar.hframes = 2
				nenufar.frame = 1 if (x * 13 + y * 7) % 5 == 0 else 0
				nenufar.position = pos + Vector2(((x * 5 + y) % 7) - 3, -6)
				nenufar.z_index = -6
				_gestor.aplicar_a(nenufar)
				add_child(nenufar)
			elif c == "$" or c == ":":
				var ingrediente: Node2D = RECOGIBLE.new()
				ingrediente.objeto = "bayas" if c == "$" else "junco"
				ingrediente.marca = "recogido/%s/%d,%d" % [mapa, x, y]
				ingrediente.color_halo = Color(0.75, 0.45, 0.85) if c == "$" else Color(0.85, 0.8, 0.5)
				ingrediente.rebrota = 240.0
				_poner(ingrediente, pos)
			elif c == "!":
				_espinas_pendientes.append(pos)
			elif c == "U":
				var tronco: StaticBody2D = TRONCO_PODRIDO.new()
				tronco.marca = "tronco/%s/%d,%d" % [mapa, x, y]
				_poner(tronco, pos)
			elif ALDEANOS.has(c):
				var aldeano: StaticBody2D = ALDEANO.new()
				aldeano.id = ALDEANOS[c][0]
				aldeano.requiere = ALDEANOS[c][1]
				aldeano.esconder_si = ALDEANOS[c][2]
				aldeano.se_mete_en = ALDEANOS[c][3]
				_poner(aldeano, pos)
			elif zonas.has(c):
				_crear_zona(c, zonas[c], Vector2i(x, y))


## Adorno sin colisión (setas, flores...) con orden de profundidad
func _adorno(ruta: String, fotogramas: int, fotograma: int, pos: Vector2) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = load(ruta)
	sprite.hframes = fotogramas
	sprite.frame = fotograma
	sprite.centered = false
	sprite.offset = Vector2(-sprite.texture.get_width() / (2 * fotogramas), -sprite.texture.get_height() + 1)
	sprite.position = pos + Vector2(int(pos.x * 3.0) % 5 - 2, 0)
	_gestor.aplicar_a(sprite)
	_entidades.add_child(sprite)


## Un secreto que ya se recogió en otra visita no vuelve a aparecer
func _crear_secreto(casilla: Vector2i, pos: Vector2) -> void:
	secretos_total += 1
	var marca := "secreto/%s/%d,%d" % [mapa, casilla.x, casilla.y]
	if Estado.tiene(marca):
		secretos_encontrados += 1
		return
	var esencia: Node2D = ESENCIA.new()
	_poner(esencia, pos)
	esencia.recogida.connect(func() -> void:
		Estado.marcar(marca)
		_al_recoger_secreto())


func _crear_zona(clave: String, z: Dictionary, casilla: Vector2i) -> void:
	var practica := String(z.get("grupo", "")) == "practica"
	var forma_practica := _forma_de_practica(clave) if practica else -1
	if practica and forma_practica < 0:
		return                                   # esta partida no le toca salir
	var zona: Node2D = ZONA.new()
	zona.radios_umbral = Vector2(z["radios"][0], z["radios"][1]) * R.CASILLA
	zona.ancho_borde = float(z["borde"]) * R.CASILLA
	zona.enemigos_al_cerrar = int(z["enemigos"])
	zona.position = Vector2(casilla) * R.CASILLA + Vector2.ONE * 8
	zona.z_index = -4
	zona.entidades = _entidades.get_path()
	zona.ya_purgada = Estado.zona_purgada(mapa, clave)
	zona.set_meta("clave", clave)
	zona.dibujo = "%s_%s" % [mapa, clave] if not practica else "%s_%s_%d" % [mapa, clave, forma_practica]
	zona.pequena = practica
	zona.jefe = String(z.get("jefe", ""))
	zona.tipos_enemigo = tipos_enemigo
	add_child(zona)
	zona.estado_cambiado.connect(func(e: int) -> void:
		if e == ZONA.Estado.PURGADA:
			Estado.marcar("zona/%s/%s" % [mapa, clave]))
	# estatua del aldeano que Giza dejó de piedra junto a la zona
	var aldeano := String(z.get("aldeano", ""))
	if aldeano != "" and not Estado.rescatado(aldeano):
		var estatua: StaticBody2D = ESTATUA.new()
		estatua.id = aldeano
		if aldeano == viajero and _sitio_viajero != Vector2.INF:
			estatua.se_queda_en = _sitio_viajero          # (no se va a la aldea: vive aquí)
		_poner(estatua, zona.position + Vector2(0, -44))
		zona.estado_cambiado.connect(func(e: int) -> void:
			if e == ZONA.Estado.PURGADA and is_instance_valid(estatua):
				estatua.despertar())


## Puertas a otras escenas. Las casillas con la misma letra forman una sola puerta.
func _crear_puertas(puertas: Dictionary) -> void:
	for letra in puertas:
		var caja := Rect2()
		var hay := false
		for y in _filas.size():
			for x in _filas[y].length():
				if _filas[y][x] == letra:
					var r := Rect2(Vector2(x, y) * R.CASILLA, Vector2.ONE * R.CASILLA)
					caja = r if not hay else caja.merge(r)
					hay = true
		if not hay:
			continue
		var p: Dictionary = puertas[letra]
		if p.has("portal"):
			# un Arco de raíz (en una sola casilla: la base del arco)
			var portal: StaticBody2D = PORTAL.new()
			portal.id = String(p["id"])
			portal.destino = String(p["destino"])
			portal.destino_puerta = String(p["puerta"])
			portal.abierto_si = String(p["portal"])
			_poner(portal, caja.position + Vector2(8, 14))
			continue
		var puerta: Area2D = PUERTA.new()
		puerta.id = String(p["id"])
		puerta.destino = String(p["destino"])
		puerta.destino_puerta = String(p["puerta"])
		puerta.salida = DIRECCIONES.get(String(p["salida"]), Vector2.DOWN)
		puerta.tam = caja.size
		puerta.position = caja.get_center()
		if p.has("cerrada"):
			puerta.cerrada_hasta = String(p["cerrada"])
			_marca_espinas = puerta.cerrada_hasta
			puerta.cerrada.connect(func() -> void:
				var dialogo := get_tree().get_first_node_in_group("dialogo")
				# (si hay un texto para esta puerta en concreto, «..._desde_<mapa>», va ese)
				var charla := "paso_cerrado_" + String(p["destino"])
				if CHARLA.datos().has(charla + "_desde_" + mapa):
					charla += "_desde_" + mapa
				if dialogo and CHARLA.datos().has(charla):
					CHARLA.hablar(self, charla))
		add_child(puerta)


func _poner(nodo: Node2D, pos: Vector2) -> void:
	nodo.position = pos
	_entidades.add_child(nodo)


func _fijo(def: Array, pos: Vector2, semilla := 0) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = pos
	if def[2] > 0.0:
		var sombra := Node2D.new()
		sombra.set_script(SOMBRA)
		sombra.set("ancho", def[2])
		cuerpo.add_child(sombra)
	var sprite := Sprite2D.new()
	sprite.texture = load(def[0])
	var fotogramas: int = def[3] if def.size() > 3 else 1
	sprite.hframes = fotogramas
	sprite.frame = semilla % fotogramas
	sprite.centered = false
	sprite.offset = Vector2(-sprite.texture.get_width() / (2 * fotogramas), -sprite.texture.get_height() + 2)
	cuerpo.add_child(sprite)
	if def.size() > 4:
		# algo que contar al acercarse (ruinas, el pozo, el monumento...)
		var cosa: Node2D = COSA.new()
		cosa.charla = String(def[4])
		cosa.radio_interaccion = float(def[5])
		cosa.altura_bocadillo = float(sprite.texture.get_height()) * 0.6
		cuerpo.add_child(cosa)
	_gestor.aplicar_a(sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = def[1]
	forma.shape = caja
	forma.position = Vector2(0, -def[1].y / 2.0 + 1)
	cuerpo.add_child(forma)
	_entidades.add_child(cuerpo)
	return cuerpo


## El agua no se puede pisar (los puentes sí). Une las casillas seguidas de cada fila en un solo bloque.
func _crear_agua(solida := agua_solida) -> void:
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Agua"
	if solida:
		add_child(cuerpo)
	var centros: Array[Vector2] = []
	for y in _filas.size():
		var x := 0
		var fila := _filas[y]
		while x < fila.length():
			if fila[x] == "~" or fila[x] == "*":
				var inicio_x := x
				while x < fila.length() and (fila[x] == "~" or fila[x] == "*"):
					centros.append(Vector2(x, y) * R.CASILLA + Vector2.ONE * 8)
					x += 1
				if solida:
					var forma := CollisionShape2D.new()
					var caja := RectangleShape2D.new()
					caja.size = Vector2((x - inicio_x) * R.CASILLA - 4, R.CASILLA)
					forma.shape = caja
					forma.position = Vector2((inicio_x + x) * R.CASILLA / 2.0, y * R.CASILLA + 8)
					cuerpo.add_child(forma)
			else:
				x += 1
	if not solida:
		cuerpo.queue_free()
	var ambiente := get_tree().get_first_node_in_group("ambiente")
	if ambiente:
		ambiente.agua = centros
		ambiente.tam_mapa = tam


## Los pretiles de los puentes de piedra («|») no se pueden cruzar
func _crear_pretiles() -> void:
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Pretiles"
	add_child(cuerpo)
	for y in _filas.size():
		var x := 0
		var fila := _filas[y]
		while x < fila.length():
			if fila[x] == "|":
				var inicio_x := x
				while x < fila.length() and fila[x] == "|":
					x += 1
				var forma := CollisionShape2D.new()
				var caja := RectangleShape2D.new()
				caja.size = Vector2((x - inicio_x) * R.CASILLA, 10)
				forma.shape = caja
				forma.position = Vector2((inicio_x + x) * R.CASILLA / 2.0, y * R.CASILLA + 8)
				cuerpo.add_child(forma)
			else:
				x += 1


## Las peñas («0», en el Camino Cobrizo) son roca maciza: no se pueden cruzar
## Los puentes del reflejo: cada grupo de casillas «\» que se tocan es un puente
func _crear_puentes_reflejo() -> void:
	var quedan := {}
	for c in _reflejos:
		quedan[c] = true
	while not quedan.is_empty():
		var inicio: Vector2i = quedan.keys()[0]
		var grupo: Array[Vector2i] = []
		var pendientes: Array[Vector2i] = [inicio]
		quedan.erase(inicio)
		while not pendientes.is_empty():
			var c: Vector2i = pendientes.pop_back()
			grupo.append(c)
			for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
				if quedan.has(c + d):
					quedan.erase(c + d)
					pendientes.append(c + d)
		var puente: Node2D = PUENTE_REFLEJO.new()
		puente.casillas = grupo
		add_child(puente)


func _crear_riscos() -> void:
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Riscos"
	add_child(cuerpo)
	for y in _filas.size():
		var x := 0
		var fila := _filas[y]
		while x < fila.length():
			if fila[x] == "0":
				var inicio_x := x
				while x < fila.length() and fila[x] == "0":
					x += 1
				var forma := CollisionShape2D.new()
				var caja := RectangleShape2D.new()
				caja.size = Vector2((x - inicio_x) * R.CASILLA, R.CASILLA)
				forma.shape = caja
				forma.position = Vector2((inicio_x + x) * R.CASILLA / 2.0, y * R.CASILLA + 8)
				cuerpo.add_child(forma)
			else:
				x += 1


## Paredes invisibles en los bordes del mapa
func _crear_limites() -> void:
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Limites"
	add_child(cuerpo)
	for rect in [Rect2(-16, -16, tam.x + 32, 16), Rect2(-16, tam.y, tam.x + 32, 16),
			Rect2(-16, 0, 16, tam.y), Rect2(tam.x, 0, 16, tam.y)]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = rect.size
		forma.shape = caja
		forma.position = rect.get_center()
		cuerpo.add_child(forma)


func _al_encender_piedra() -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	var piedras := get_tree().get_nodes_in_group("piedras_eco")
	var encendidas := piedras.filter(func(p: Node) -> bool: return p.encendida_ya).size()
	if encendidas < piedras.size():
		if hud:
			hud.mostrar_mensaje("La piedra resuena... (%d/%d)" % [encendidas, piedras.size()])
		return
	for roca in get_tree().get_nodes_in_group("rocas_moviles"):
		roca.apartarse()
	Estado.marcar("escondite/" + mapa)
	if hud:
		hud.mostrar_mensaje("Algo se ha movido entre las rocas del norte")


func _al_recoger_secreto() -> void:
	secretos_encontrados += 1
	secreto_encontrado.emit(secretos_encontrados, secretos_total)
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje("¡Secreto encontrado! (%d/%d)" % [secretos_encontrados, secretos_total])


## Devuelve el tipo de suelo ("hierba", "tierra", "piedra", "madera", "nieve", "agua") según la casilla del mapa
func tipo_suelo(pos_global: Vector2) -> String:
	var x := int(pos_global.x / R.CASILLA)
	var y := int(pos_global.y / R.CASILLA)
	if y < 0 or y >= _filas.size():
		return "hierba"
	var fila: String = _filas[y]
	if x < 0 or x >= fila.length():
		return "hierba"
	var c := fila[x]
	var es_mundo_nieve: bool = mundo == "sigilia" or mapa.begins_with("ruinas") or mapa.begins_with("paso_escarcha")
	match c:
		"=", "[", "]":
			return "madera"
		"#", "/", "b":
			return "tierra"
		"%", "-", "r", "0", "N":
			return "piedra"
		"~", "\\", "'":
			return "agua"
		".", ",", "*":
			return "nieve" if es_mundo_nieve else "hierba"
		_:
			return "nieve" if es_mundo_nieve else "hierba"
