extends Node2D
## LA CASA SELLADA DE BATA (Embarcadero Junco). Bata, el pato barquero, está encerrado VIVO en su casa: raíces de
## piedra de Giza tapan la puerta y la ventana (habla con Maisha a través de la puerta). De las raíces salen unas VENAS
## violetas que cruzan el pueblo por el suelo, con pulsos de luz que van hacia la casa: siguiéndolas al revés se llega
## a su origen, un NUDO de Giza escondido entre los SACOS del almacén.
##   - Los sacos tapan el nudo: el cetro no los mueve, el LATIDO sí (los aparta).
##   - Destapado, el cetro rebota en el nudo; una SEMILLA lo revienta.
##   - Entonces las venas se secan una tras otra, como una mecha, desde el nudo hasta la casa; las raíces de la puerta
##     se resquebrajan y se deshacen, y Bata sale y se va a su muelle (marca «casa_bata_abierta»).
## Lo crea scripts/mundo/embarcadero_junco.gd con las posiciones de la casa («{») y del almacén («œ»).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const ALDEANO := preload("res://scripts/mundo/aldea/aldeano.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const SELLO := preload("res://arte/mundos/raiz/embarcadero/sello_raices.png")
const NUDO := preload("res://arte/mundos/raiz/embarcadero/nudo_giza.png")
const SACO := preload("res://arte/mundos/raiz/embarcadero/saco.png")
const MARCA := "casa_bata_abierta"
const VIOLETA := Color("a855d6")
const VIOLETA_CLARO := Color("d6a8f0")

var casa := Vector2.ZERO                 # la base de la casa (donde se apoya su dibujo)
var almacen := Vector2.ZERO              # la base del almacén
var sitio_bata := Vector2.ZERO           # dónde se queda Bata (en su muelle)

var _sello: Sprite2D
var _nudo: Node2D
var _sacos: Array[Node2D] = []
var _venas: PackedVector2Array = []
var _seca := -1.0                        # -1: viva; 0..1: secándose desde el nudo hacia la casa
var _tiempo := 0.0
var _abriendo := false


func _ready() -> void:
	z_index = -4
	if Estado.tiene(MARCA):
		return
	# las raíces que sellan la puerta y la ventana (encima del dibujo de la casa, alineadas con él)
	_sello = Sprite2D.new()
	_sello.texture = SELLO
	_sello.hframes = 2
	_sello.centered = false
	_sello.offset = Vector2(-50, -90)
	_sello.position = casa + Vector2(0, 0.5)
	_sello.z_index = 4
	add_child(_sello)
	# el nudo, delante del portón del almacén, y los sacos que lo tapan
	var nudo_pos := almacen + Vector2(-23, 10)
	_nudo = _Nudo.new()
	_nudo.casa_sellada = self
	_nudo.position = nudo_pos
	get_parent().get_node("Entidades").add_child.call_deferred(_nudo)
	for i in 4:
		var saco := _Saco.new()
		saco.position = nudo_pos + [Vector2(-11, 0), Vector2(11, 1), Vector2(0, 9), Vector2(-4, -4)][i]
		saco.variante = i % 2
		saco.nudo_pos = nudo_pos
		_sacos.append(saco)
		get_parent().get_node("Entidades").add_child.call_deferred(saco)
	_trazar_venas(casa + Vector2(-14, 2), nudo_pos + Vector2(0, 2))


## Un camino que serpentea de la casa al nudo, siguiendo más o menos el camino del pueblo
func _trazar_venas(desde: Vector2, hasta: Vector2) -> void:
	var codo := Vector2(lerpf(desde.x, hasta.x, 0.45), lerpf(desde.y, hasta.y, 0.3) + 30.0)
	var n := 70
	for i in n + 1:
		var t := float(i) / n
		var p := (1.0 - t) * (1.0 - t) * desde + 2.0 * (1.0 - t) * t * codo + t * t * hasta
		var lado := Vector2(-(hasta - desde).y, (hasta - desde).x).normalized()
		p += lado * (sin(t * 23.0) * 3.0 + sin(t * 7.0 + 1.0) * 5.0) * sin(t * PI)
		_venas.append(p.round())


func nudo_tapado() -> bool:
	for saco in _sacos:
		if is_instance_valid(saco) and saco.global_position.distance_to(_nudo.global_position) < 15.0:
			return true
	return false


func _process(delta: float) -> void:
	_tiempo += delta
	if _seca >= 0.0 and _seca < 1.0:
		_seca = minf(1.0, _seca + delta / 2.6)
		if _seca >= 1.0:
			_romper_sello()
	queue_redraw()


func _draw() -> void:
	if _venas.size() < 2:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var n := _venas.size()
	for i in n - 1:
		var t := 1.0 - float(i) / (n - 1)               # 0 en el nudo, 1 en la casa
		var a := _venas[i]
		var b := _venas[i + 1]
		if _seca >= 0.0 and t <= _seca:
			# seca: gris y cada vez más tenue
			draw_line(a, b, Color(0.35, 0.33, 0.38, 0.5 * (1.0 - _seca * 0.6)), 2.0)
			continue
		# viva: oscura con un pulso de luz que viaja del nudo a la casa (seguirlo al revés lleva al nudo)
		var pulso := pow(maxf(0.0, sin(t * 18.0 - _tiempo * 4.0)), 6.0)
		var cerca := 0.0
		if maisha:
			cerca = clampf(1.0 - a.distance_to(maisha.global_position) / 90.0, 0.0, 1.0)
		draw_line(a, b, Color(0.12, 0.04, 0.18, 0.75), 3.0)
		draw_line(a, b, VIOLETA.lerp(VIOLETA_CLARO, pulso), 1.0 + pulso)
		if pulso > 0.5 or cerca > 0.3:
			draw_line(a, b, Color(VIOLETA_CLARO, 0.25 * maxf(pulso, cerca)), 5.0)


## El nudo ha reventado: las venas se secan hacia la casa
func nudo_reventado() -> void:
	_seca = 0.0
	Sonido.efecto("brotes")
	Impacto.temblar(2.0, 0.4)
	for saco in _sacos:
		if is_instance_valid(saco):
			saco.remove_from_group("golpeables")


func _romper_sello() -> void:
	if _abriendo:
		return
	_abriendo = true
	Sonido.efecto("estatua_despierta", 0.0, casa)
	Impacto.temblar(3.0, 0.5)
	_sello.frame = 1
	var t := create_tween()
	for i in 8:
		t.tween_property(_sello, "position:x", casa.x + (1.0 if i % 2 == 0 else -1.0), 0.05)
	t.tween_property(_sello, "modulate:a", 0.0, 0.8)
	await t.finished
	for i in 3:
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 10
		astillas.fuerza = 80.0
		astillas.position = casa + Vector2(-20 + i * 14, -40)
		get_parent().get_node("Entidades").add_child(astillas)
	Estado.marcar(MARCA)
	_venas.clear()
	# Bata sale por la puerta, cuenta, y se va a su muelle
	var bata: StaticBody2D = ALDEANO.new()
	bata.id = "bata"
	bata.position = casa + Vector2(-18, 10)
	get_parent().get_node("Entidades").add_child(bata)
	await get_tree().create_timer(0.6).timeout
	await CHARLA.hablar(bata, "bata_libre")
	var camino := create_tween()
	camino.tween_property(bata, "position", sitio_bata, bata.position.distance_to(sitio_bata) / 55.0)


# --- el nudo y los sacos ---------------------------------------------------------------

class _Nudo:
	extends Node2D
	var casa_sellada: Node2D
	var _sprite: Sprite2D
	var _t := 0.0
	var _roto := false

	func _ready() -> void:
		add_to_group("golpeables")
		add_to_group("daniables")
		add_to_group("interactuables")
		_sprite = Sprite2D.new()
		_sprite.texture = NUDO
		_sprite.hframes = 2
		_sprite.offset = Vector2(0, -11)
		add_child(_sprite)

	func _process(delta: float) -> void:
		_t += delta
		_sprite.frame = 1 if fmod(_t, 0.9) < 0.3 else 0

	func interactuar() -> void:
		await CHARLA.hablar(self, "embarcadero_nudo_tapado" if casa_sellada.nudo_tapado() else "embarcadero_nudo")

	func recibir_golpe(_danio: int, _dir: Vector2) -> bool:
		Sonido.efecto("clinc", 0.0, global_position)
		return false

	func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
		if _roto or tipo != "explosion" or casa_sellada.nudo_tapado():
			return
		_roto = true
		remove_from_group("golpeables")
		remove_from_group("daniables")
		remove_from_group("interactuables")
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 16
		astillas.chispas = 6
		astillas.fuerza = 90.0
		astillas.position = global_position + Vector2(0, -10)
		get_parent().add_child(astillas)
		casa_sellada.nudo_reventado()
		var t := create_tween().set_parallel(true)
		t.tween_property(_sprite, "scale", Vector2(1.5, 0.2), 0.3)
		t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
		t.chain().tween_callback(queue_free)


class _Saco:
	extends StaticBody2D
	var variante := 0
	var nudo_pos := Vector2.INF
	var _sprite: Sprite2D

	func _ready() -> void:
		add_to_group("golpeables")
		collision_layer = 1
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(12, 6)
		forma.shape = caja
		forma.position = Vector2(0, -3)
		add_child(forma)
		_sprite = Sprite2D.new()
		_sprite.texture = SACO
		_sprite.hframes = 2
		_sprite.frame = variante
		_sprite.offset = Vector2(0, -8)
		add_child(_sprite)

	## El cetro no lo mueve (es grano: pesa)
	func recibir_golpe(_danio: int, _dir: Vector2) -> bool:
		var t := create_tween()
		t.tween_property(_sprite, "position:x", 1.0, 0.04)
		t.tween_property(_sprite, "position:x", 0.0, 0.04)
		return false

	## El Latido sí: lo aparta rodando un poco
	func empujar(fuerza: Vector2) -> void:
		var dir := fuerza.normalized()
		# (si fuera a quedar encima del nudo, rueda hacia un lado)
		var destino := position + dir * 26.0
		if nudo_pos != Vector2.INF and destino.distance_to(nudo_pos) < 22.0:
			var lado := Vector2(-dir.y, dir.x)
			if (position - nudo_pos).dot(lado) < 0.0:
				lado = -lado
			destino = position + lado * 30.0
		var t := create_tween().set_parallel(true)
		t.tween_property(self, "position", destino, 0.35).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		t.tween_property(_sprite, "rotation", signf(fuerza.x if fuerza.x != 0.0 else 1.0) * TAU, 0.35)
		Sonido.efecto("tablas_coger", -6.0, global_position)
