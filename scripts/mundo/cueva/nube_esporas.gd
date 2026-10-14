extends Node2D
## NUBE DE ESPORAS (cueva de las setas, «ǯ»): una nube violeta de las esporas de Kuvu que late: un rato se hincha
## (activa) y otro se encoge (se puede pasar). Si Maisha la respira, se MAREA: los controles van al revés unos
## segundos (maisha.mareo). El Latido la deshace un rato (grupo «ondas», «disipar»).

const ACTIVA := 3.0
const PAUSA := 1.8
const MAREO := 3.0
const RADIO := 20.0
const TEX_LUZ := preload("res://scripts/mundo/gruta/oscuridad.gd")

var dura := -1.0                # si es más de 0, la nube se deshace sola pasado ese rato (las que lanza Kuvu)
var _t := 0.0
var _apagada := 0.0             # tras el Latido, este rato no hay nube
var _fuerza := 0.0              # 0..1: lo hinchada que está
var _motas: Array[Vector3] = []
var _luz: PointLight2D


func _ready() -> void:
	add_to_group("ondas")
	add_to_group("esporas")
	z_index = 2
	_t = fmod(position.x * 0.13 + position.y * 0.07, ACTIVA + PAUSA)
	for k in 26:
		_motas.append(Vector3(randf() * TAU, randf() * RADIO, randf() * TAU))
	_luz = PointLight2D.new()
	_luz.texture = TEX_LUZ.textura_luz(128)
	_luz.texture_scale = 0.7
	_luz.color = Color(0.7, 0.4, 0.95)
	add_child(_luz)


func activa() -> bool:
	return _fuerza > 0.5


func _process(delta: float) -> void:
	if dura > 0.0:
		dura -= delta
		if dura <= 0.0:
			remove_from_group("ondas")
			remove_from_group("esporas")
			var t := create_tween()
			t.tween_property(self, "modulate:a", 0.0, 0.6)
			t.tween_callback(queue_free)
	_apagada = maxf(0.0, _apagada - delta)
	_t = fmod(_t + delta, ACTIVA + PAUSA)
	var quiere := 1.0 if _t < ACTIVA and _apagada <= 0.0 else 0.0
	_fuerza = move_toward(_fuerza, quiere, delta * 2.5)
	_luz.energy = 0.2 + 0.6 * _fuerza
	queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and activa() and maisha.global_position.distance_to(global_position + Vector2(0, 6)) < RADIO * _fuerza:
		if float(maisha.get("mareo")) < 0.5:
			maisha.set("mareo", MAREO)
			Sonido.efecto("bundi_esfuma", 0.0, global_position)
			if not Estado.tiene("cueva_esporas"):
				Estado.marcar("cueva_esporas")
				load("res://scripts/mundo/charla.gd").hablar(self, "cueva_esporas")


## El Latido la deshace un rato
func disipar() -> void:
	_apagada = 4.0


func _draw() -> void:
	var tiempo := Time.get_ticks_msec() / 1000.0
	var r := RADIO * (0.35 + 0.65 * _fuerza)
	for k in 3:
		draw_circle(Vector2(0, 0), r * (1.0 - k * 0.25), Color(0.62, 0.35, 0.85, (0.10 + 0.05 * k) * (0.3 + 0.7 * _fuerza)))
	for m in _motas:
		var a := m.x + tiempo * 0.6
		var p := Vector2(cos(a), sin(a) * 0.6) * m.y * (0.35 + 0.65 * _fuerza) + Vector2(0, sin(tiempo * 2.0 + m.z) * 2.0)
		draw_rect(Rect2(p.round(), Vector2.ONE), Color(0.94, 0.85, 1.0, 0.4 + 0.5 * _fuerza))
