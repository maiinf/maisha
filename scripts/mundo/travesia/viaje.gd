extends Node2D
## EL VIAJE EN EL TRANSBORDADOR (La Travesía). La barca sube sola por el centro del río, del Embarcadero Junco (sur)
## al muelle de piedra de la Gruta de las Raíces (norte). Maisha va en la cubierta (se puede mover por ella, pero no
## salir) y Bata lleva la pértiga en la popa. Detrás, la estela en el agua. Al llegar, Maisha baja al muelle (marca
## «travesia_hecha»); desde la barca se puede volver al Embarcadero.
## El río sigue la misma fórmula que crear_travesia (herramientas/construir_mapa.py).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const CUBIERTA := preload("res://arte/mundos/raiz/embarcadero/cubierta.png")
const BATA := preload("res://arte/personajes/aldeanos/bata_frente.png")
const CASILLA := 16.0
const PISABLE := Rect2(-58, -40, 118, 62)       # la cubierta que se pisa (desde el centro de la barca)
const VELOCIDAD := 34.0                           # píxeles por segundo, río arriba
const Y_SALIDA := 160.0                           # (en casillas) dónde zarpa
const Y_LLEGADA := 14.0                           # y dónde atraca, junto al muelle de piedra

enum Fase { ZARPA, NAVEGA, ATRACADA }

var fase: int = Fase.ZARPA
var recorrido := 0.0                              # píxeles navegados
var _camino: PackedVector2Array = []
var _largo := 0.0
var _t := 0.0
var _tiempo := 0.0
var _sprite: Sprite2D
var _bata: Sprite2D
var _maisha: Node2D
var _sujeta := true                               # Maisha va sujeta a la cubierta
var _pertiga: Node2D


static func centro_rio(y: float) -> float:
	return 24.0 + 5.0 * sin(y * 0.045) + 2.0 * sin(y * 0.11 + 1.0)


func _ready() -> void:
	process_physics_priority = 10                 # (después de que Maisha se mueva)
	z_index = -3
	_sprite = Sprite2D.new()
	_sprite.texture = CUBIERTA
	add_child(_sprite)
	_bata = Sprite2D.new()
	_bata.texture = BATA
	_bata.offset = Vector2(0, -16)
	_bata.position = Vector2(48, 34)
	_bata.z_index = 4
	add_child(_bata)
	_pertiga = Node2D.new()
	_pertiga.z_index = 5
	_pertiga.draw.connect(_dibujar_pertiga)
	add_child(_pertiga)
	_trazar()
	_maisha = get_tree().get_first_node_in_group("maisha") as Node2D
	if Estado.tiene("travesia_hecha"):
		recorrido = _largo
		_atracar(true)
	position = _punto(recorrido)
	if fase != Fase.ATRACADA:
		_maisha.global_position = position + Vector2(0, -6)


## El camino de la barca: por el centro del río y, al final, de lado hacia el muelle de piedra
func _trazar() -> void:
	var y := Y_SALIDA
	while y > Y_LLEGADA + 10.0:
		_camino.append(Vector2(centro_rio(y), y) * CASILLA + Vector2(8, 8))
		y -= 1.0
	var muelle := Vector2(centro_rio(12.0) + 1.3, Y_LLEGADA) * CASILLA + Vector2(8, 8)
	_camino.append((_camino[_camino.size() - 1] + muelle) / 2.0)
	_camino.append(muelle)
	for i in _camino.size() - 1:
		_largo += _camino[i].distance_to(_camino[i + 1])


func _punto(d: float) -> Vector2:
	var resto := clampf(d, 0.0, _largo)
	for i in _camino.size() - 1:
		var tramo := _camino[i].distance_to(_camino[i + 1])
		if resto <= tramo:
			return _camino[i].lerp(_camino[i + 1], resto / maxf(tramo, 0.001))
		resto -= tramo
	return _camino[_camino.size() - 1]


func _physics_process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	var antes := position
	match fase:
		Fase.ZARPA:
			if _t > 2.0:
				fase = Fase.NAVEGA
				_t = 0.0
				Sonido.efecto("tablas_coger", -2.0, position)
		Fase.NAVEGA:
			recorrido = minf(_largo, recorrido + VELOCIDAD * delta)
			position = _punto(recorrido)
			if recorrido >= _largo:
				_atracar(false)
	# la barca se mece un poco
	_sprite.position.y = sin(_tiempo * 1.6) * 1.0
	_sprite.rotation = sin(_tiempo * 1.1) * 0.012
	_bata.position.y = 34.0 + sin(_tiempo * 1.6) * 1.0
	_pertiga.queue_redraw()
	# Maisha va encima: se mueve con la barca y no sale de la cubierta
	if _sujeta and is_instance_valid(_maisha):
		var p := _maisha.global_position + (position - antes)
		var local := p - position
		local.x = clampf(local.x, PISABLE.position.x, PISABLE.end.x)
		local.y = clampf(local.y, PISABLE.position.y, PISABLE.end.y)
		_maisha.global_position = position + local
	queue_redraw()


func _draw() -> void:
	# la estela: dos ondas en V detrás de la popa (si navega) y la pértiga de Bata
	if fase == Fase.NAVEGA:
		for k in 4:
			var f := fmod(_tiempo * 0.8 + k * 0.25, 1.0)
			var y0 := 60.0 + f * 70.0
			var a := (1.0 - f) * 0.5
			draw_line(Vector2(-70 - f * 30, y0), Vector2(-40, 58), Color(0.82, 0.94, 0.92, a), 1.0)
			draw_line(Vector2(70 + f * 30, y0), Vector2(40, 58), Color(0.82, 0.94, 0.92, a), 1.0)


## La pértiga de Bata, por encima de todo: la clava en el agua al ritmo de la barca
func _dibujar_pertiga() -> void:
	var mano := Vector2(55, 18) + Vector2(0, sin(_tiempo * 1.6))
	var empuje := sin(_tiempo * 1.2) * 6.0 if fase == Fase.NAVEGA else 0.0
	var punta := mano + Vector2(18, 44 + empuje)
	_pertiga.draw_line(mano + Vector2(-6, -14), punta, Color("3a2414"), 2.0)
	_pertiga.draw_line(mano + Vector2(-6, -14), punta, Color("8a6440"), 1.0)


func _atracar(ya_estaba: bool) -> void:
	fase = Fase.ATRACADA
	position = _punto(_largo)
	if ya_estaba:
		_sujeta = false
		_crear_agua_y_vuelta()
		return
	Sonido.efecto("tablas_coger", 0.0, position)
	Impacto.temblar(1.5, 0.3)
	await get_tree().create_timer(0.6).timeout
	await CHARLA.hablar(self, "travesia_llegada")
	# Maisha baja al muelle de piedra
	_sujeta = false
	_maisha.set("puede_actuar", false)
	var muelle := Vector2(centro_rio(12.0) - 6.0, 12.0) * CASILLA + Vector2(8, 10)
	var t := create_tween()
	t.tween_property(_maisha, "global_position", position + Vector2(-56, 0), 0.4)
	t.tween_property(_maisha, "global_position", muelle, 0.6)
	await t.finished
	_maisha.set("puede_actuar", true)
	Estado.marcar("travesia_hecha")
	_crear_agua_y_vuelta()


## Atracada: el agua vuelve a ser agua, y desde la barca se puede volver al Embarcadero
func _crear_agua_y_vuelta() -> void:
	var region := get_tree().get_first_node_in_group("region")
	if region:
		region.call("_crear_agua", true)
	var vuelta := _Vuelta.new()
	vuelta.position = Vector2(-60, 6)
	add_child(vuelta)


class _Vuelta:
	extends Node2D
	var radio_interaccion := 34.0
	var altura_bocadillo := 30.0

	func _ready() -> void:
		add_to_group("interactuables")

	func interactuar() -> void:
		await CHARLA.hablar(self, "travesia_volver")
		Estado.ir_a("embarcadero_junco", "travesia")
