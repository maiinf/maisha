extends "res://scripts/mundo/escena_mundo.gd"
## LA FUNDICIÓN DE ESCORIA (Asterhaul, el camino del este de Mji-Jiwe): cinco islas de piedra en un lago de escoria
## fundida («≈»: no se pisa). No hay puentes: se cruza en BARCAZAS DE HIERRO (asterhaul/barcaza.gd).
##   - LA CASETA DE MOTO (oeste): MOTO, el maestro gruista, en gris (sigilia/escriba.gd; su Esquirla está en el
##     Crisol Norte). La primera barcaza tiene CABRESTANTE (un golpe, y sale): es la única que se mueve sin Pulso.
##     Con su pulso, Moto enseña el PULSO MAGNÉTICO (O). La ESTELA se lee.
##   - EL CRISOL NORTE: la Esquirla de Moto y un KOVU (enemigos/kovu.gd) al que aún no se le puede hacer nada.
##   - LA PLATAFORMA DE LOS IMANES (centro): dos BLOQUES-IMÁN (asterhaul/bloque_iman.gd) y dos PLACAS; con un
##     bloque en cada placa se abre la COMPUERTA del este («fundicion/compuerta_este»).
##   - LA NAVE DE LAS GRÚAS (sur): otro bloque y otra placa abren la compuerta de su mitad este
##     («fundicion/compuerta_nave»): una Esquirla de Estrella.
##   - LA GRAN FRAGUA DEL ESTE: NYUNDO, EL HERRERO DE 4 TENAZAS (enemigos/nyundo.gd). Despierta al entrar. Al
##     vencerlo se rompe la Cadena del Este («cadena_este_rota»).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const BARCAZA := preload("res://scripts/mundo/asterhaul/barcaza.gd")
const CABRESTANTE := preload("res://scripts/mundo/asterhaul/cabrestante.gd")
const BLOQUE := preload("res://scripts/mundo/asterhaul/bloque_iman.gd")
const COMPUERTA := preload("res://scripts/mundo/asterhaul/compuerta.gd")
const PLACA := preload("res://arte/mundos/asterhaul/fundicion/placa.png")
const KOVU := preload("res://scripts/enemigos/kovu.gd")
const NYUNDO := preload("res://scripts/enemigos/nyundo.gd")
const ARTE := "res://arte/mundos/asterhaul/"
## (todo en casillas)
const MOTO := Vector2i(15, 24)
const CASETA := Vector2i(8, 25)
const ESTELA := Vector2i(12, 34)
## barcaza: [nombre, muelle de salida, el otro muelle] (la esquina de arriba a la izquierda de cada hueco de 3×3)
const BARCAZAS := [
	["norte", Vector2i(19, 19), Vector2i(19, 16)],
	["oeste", Vector2i(23, 28), Vector2i(31, 28)],
	["sur", Vector2i(40, 37), Vector2i(40, 41)],
	["este", Vector2i(49, 28), Vector2i(54, 28)],
]
## los dos cabrestantes de la barcaza del norte (uno en cada orilla)
const CABRESTANTES := [Vector2i(22, 22), Vector2i(22, 15)]
## juego de imanes: [marca de su compuerta, casilla de la compuerta (la de abajo), [[bloque, placa], ...]]
const IMANES := [
	["fundicion/compuerta_este", Vector2i(48, 30), [[Vector2i(38, 30), Vector2i(38, 25)], [Vector2i(44, 26), Vector2i(44, 32)]]],
	["fundicion/compuerta_nave", Vector2i(52, 50), [[Vector2i(36, 49), Vector2i(46, 49)]]],
]
## Kovu: por dónde nada (casillas de escoria)
const KOVUS := [[Vector2i(37, 8), Vector2i(37, 14)], [Vector2i(28, 33), Vector2i(28, 36)], [Vector2i(34, 40), Vector2i(38, 40)]]
## esquirla: [objeto, casilla, marca]
const ESQUIRLAS := [["esquirla_moto", Vector2i(30, 9), "esquirla/moto"], ["esquirla_estrella", Vector2i(57, 49), "esquirla/nave"]]
## la Gran Fragua: su centro (px) y su radio (px)
const FRAGUA := Vector2(68.5, 29.5) * 16.0
const RADIO := 184.0

var _nyundo: Node2D = null
var _despertando := false
## placa → [su dibujo, la marca de su compuerta]
var _placas := {}


func _ready() -> void:
	super()
	Estado.marcar("fundicion_escoria")
	_poner_escoria()
	_poner_cosas()
	if not Estado.tiene("fundicion_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


## La escoria («≈») no se pisa: un choque por cada tira de casillas seguidas
func _poner_escoria() -> void:
	var filas: PackedStringArray = $Region._filas
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Escoria"
	add_child(cuerpo)
	for y in filas.size():
		var x := 0
		while x < filas[y].length():
			if filas[y][x] != "≈":
				x += 1
				continue
			var x0 := x
			while x < filas[y].length() and filas[y][x] == "≈":
				x += 1
			var forma := CollisionShape2D.new()
			var caja := RectangleShape2D.new()
			caja.size = Vector2((x - x0) * 16.0 - 4.0, 16.0)
			forma.shape = caja
			forma.position = Vector2((x0 + x) * 8.0, y * 16.0 + 8.0)
			cuerpo.add_child(forma)


func _poner_cosas() -> void:
	_poner_adorno("mji_jiwe/casa", CASETA, 58, 14, 1)
	_poner_adorno("fundicion/estela", ESTELA, 12, 6, -1)
	_leer("estela_pulso", _sitio(ESTELA) + Vector2(0, 6))
	var moto: StaticBody2D = ESCRIBA.new()
	moto.nombre = "moto"
	moto.dibujo = "moto"
	moto.sufijo_apagado = "_gris"
	moto.sufijo_marca = "_pulso"
	moto.position = _sitio(MOTO)
	$Entidades.add_child(moto)
	var norte: Node2D = null
	for b in BARCAZAS:
		var barcaza: Node2D = BARCAZA.new()
		barcaza.name = "Barcaza_" + String(b[0])
		barcaza.muelle_a = b[1]
		barcaza.muelle_b = b[2]
		add_child(barcaza)
		if b[0] == "norte":
			norte = barcaza
	for c in CABRESTANTES:
		var torno: StaticBody2D = CABRESTANTE.new()
		torno.barcaza = norte
		torno.position = _sitio(c)
		$Entidades.add_child(torno)
	for juego in IMANES:
		var compuerta: StaticBody2D = COMPUERTA.new()
		compuerta.marca = juego[0]
		compuerta.position = _sitio(juego[1])
		$Entidades.add_child(compuerta)
		var casillas: Array[Vector2i] = []
		for par in juego[2]:
			casillas.append(par[1])
		for par in juego[2]:
			var placa := Sprite2D.new()
			placa.texture = PLACA
			placa.hframes = 2
			placa.z_index = -3
			placa.position = _sitio(par[1]) + Vector2(0, -5)
			add_child(placa)
			_placas[par[1]] = [placa, juego[0]]
			var bloque: StaticBody2D = BLOQUE.new()
			bloque.placas = casillas
			# (si su compuerta ya está abierta, el bloque está en su placa)
			bloque.position = _sitio(par[1] if Estado.tiene(juego[0]) else par[0])
			$Entidades.add_child(bloque)
			bloque.parado.connect(func(_c: Vector2i) -> void: _mirar_placas())
	_mirar_placas.call_deferred()
	for k in KOVUS:
		var kovu: Node2D = KOVU.new()
		for c: Vector2i in k:
			kovu.nado.append(_sitio(c))
		kovu.position = _sitio(k[0])
		$Entidades.add_child(kovu)
	for e in ESQUIRLAS:
		var esquirla: Node2D = RECOGIBLE.new()
		esquirla.objeto = e[0]
		esquirla.marca = e[2]
		esquirla.dibujo = ARTE + "desfiladero/esquirla.png"
		esquirla.color_halo = Color(1.0, 0.75, 0.3)
		esquirla.position = _sitio(e[1])
		$Entidades.add_child(esquirla)
	if not Estado.tiene("nyundo_vencido"):
		_nyundo = NYUNDO.new()
		_nyundo.position = FRAGUA + Vector2(0, 6)
		$Entidades.add_child(_nyundo)
		_nyundo.destruido.connect(_al_vencer_nyundo)


## Qué placas tienen un bloque encima; si las de un juego lo tienen todas, se abre su compuerta
func _mirar_placas() -> void:
	var con_peso := {}
	for b in get_tree().get_nodes_in_group("bloques_iman"):
		con_peso[b.casilla()] = true
	var faltan := {}
	for casilla: Vector2i in _placas:
		var pisada: bool = con_peso.has(casilla)
		(_placas[casilla][0] as Sprite2D).frame = 1 if pisada else 0
		if not pisada:
			faltan[_placas[casilla][1]] = true
	for juego in IMANES:
		if not faltan.has(juego[0]) and not Estado.tiene(juego[0]):
			Estado.marcar(juego[0])


## Un adorno que no se atraviesa: su dibujo de pie (o un fotograma de su tira de dos) y una caja en la base
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fondo: float, fotograma: int) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = _sitio(casilla)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	if fotograma >= 0:
		sprite.hframes = 2
		sprite.frame = fotograma
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cuerpo.add_child(sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(ancho, fondo)
	forma.shape = caja
	forma.position = Vector2(0, -fondo / 2.0)
	cuerpo.add_child(forma)
	$Entidades.add_child(cuerpo)
	return cuerpo


func _leer(charla: String, donde: Vector2) -> void:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)


## Al entrar en la Gran Fragua, despierta Nyundo; mientras pelean, la cámara se va hacia la mitad entre Maisha y él
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_nyundo) and not Estado.tiene("nyundo_vencido"):
		hacia = ((_nyundo.global_position + Vector2(0, -40) - maisha.global_position) * 0.5).clamp(Vector2(-140, -80), Vector2(140, 80))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_nyundo) or Estado.tiene("nyundo_vencido"):
		return
	if maisha.global_position.distance_to(FRAGUA) < RADIO * 0.8:
		_despertando = true
		if not Estado.tiene("nyundo_visto"):
			Estado.marcar("nyundo_visto")
			await CHARLA_SCRIPT.hablar(self, "nyundo_encuentro")
		if is_instance_valid(_nyundo):
			_nyundo.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


func _al_vencer_nyundo() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica("fundicion_escoria")
	await CHARLA_SCRIPT.hablar(self, "nyundo_vencido")


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "pulso_magnetico":
		_hud.mostrar_mensaje("Pulso Magnético (O): lo quieto viene, lo que viene se va")
	elif marca.begins_with("fundicion/compuerta_"):
		_hud.mostrar_mensaje("Una compuerta de crisol se abre")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("fundicion_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "fundicion_llegada")
	Estado.marcar("fundicion_llegada")
