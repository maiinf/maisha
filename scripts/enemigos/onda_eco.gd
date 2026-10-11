extends Node2D
## ONDA DE ECO: el grito del murciélago de eco. Tres arcos de sonido (violeta de Giza y blanco) que van en línea
## recta hasta su «alcance» (o hasta el borde de la zona, donde «rebota en la peña») y luego VUELVEN a quien gritó,
## persiguiéndolo. Hace daño a Maisha si la pilla, a la ida y a la vuelta (una vez en cada viaje).
## Al llegar de vuelta al murciélago, este se la traga y se marea. El Latido de Maisha la deshace («disipar»).

const R := preload("res://scripts/combate/reglas_combate.gd")
const VIOLETA := Color("a855d6")
const CLARO := Color(0.85, 0.95, 1.0)

var direccion := Vector2.RIGHT
var dueno: Node2D = null
var alcance := 120.0
var zona: Node = null
var volviendo := false
var _recorrido := 0.0
var _tiempo := 0.0
var _pillo_ida := false
var _pillo_vuelta := false
var _apagandose := false
var _mira := Vector2.RIGHT          # hacia dónde se dibujan los arcos (por dónde avanza)


func _ready() -> void:
	add_to_group("ondas")
	z_index = 2
	_mira = direccion


func _physics_process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()
	if _apagandose:
		return
	var paso := R.MURCIELAGO_ONDA * delta
	if not volviendo:
		var antes := global_position
		global_position += direccion * paso
		_recorrido += paso
		# el borde de la zona hace de pared de peña: ahí rebota
		var dentro: Vector2 = zona.call("limitar", global_position) if zona else global_position
		if _recorrido >= alcance or dentro.distance_to(global_position) > 0.5:
			global_position = dentro if zona else global_position
			volviendo = true
			Sonido.efecto("eco_voz", 0.0, global_position, 0.25)
		_mira = (global_position - antes).normalized() if global_position != antes else _mira
	else:
		if not is_instance_valid(dueno):
			disipar()
			return
		var meta := dueno.global_position
		_mira = (meta - global_position).normalized() if meta != global_position else _mira
		global_position = global_position.move_toward(meta, paso * 1.1)
		if global_position.distance_to(meta) < 4.0:
			dueno.call("tragar_eco")
			_apagar(0.15)
			return
	_tocar_a_maisha()


func _tocar_a_maisha() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	if (volviendo and _pillo_vuelta) or (not volviendo and _pillo_ida):
		return
	if maisha.global_position.distance_to(global_position) < R.MURCIELAGO_ONDA_RADIO:
		if volviendo:
			_pillo_vuelta = true
		else:
			_pillo_ida = true
		maisha.call("recibir_danio", 1, global_position - _mira * 8.0, "contacto")


## El Latido la deshace: se abre y se desvanece
func disipar() -> void:
	if _apagandose:
		return
	_apagar(0.25)


func _apagar(segundos: float) -> void:
	_apagandose = true
	remove_from_group("ondas")
	var t := create_tween().set_parallel(true)
	t.tween_property(self, "scale", Vector2(1.6, 1.6), segundos)
	t.tween_property(self, "modulate:a", 0.0, segundos)
	t.chain().tween_callback(queue_free)


func _draw() -> void:
	# un halo suave y tres arcos que avanzan (blanco brillante por dentro, violeta de Giza por fuera)
	var ang := _mira.angle()
	draw_circle(Vector2.ZERO, 12.0, Color(VIOLETA, 0.12))
	for k in 3:
		var r := 7.0 + k * 4.0 + sin(_tiempo * 20.0 + k) * 0.7
		var centro := -_mira * (k * 4.0)
		var a := 1.0 - k * 0.25
		draw_arc(centro, r, ang - 1.0, ang + 1.0, 12, Color(0.05, 0.03, 0.08, a * 0.5), 3.5)
		draw_arc(centro, r, ang - 1.0, ang + 1.0, 12, Color(VIOLETA, a), 2.4)
		draw_arc(centro, r, ang - 0.8, ang + 0.8, 10, Color(1.0, 1.0, 1.0, a * 0.9), 1.0)
	# motas que se quedan atrás
	for i in 4:
		var f := fmod(_tiempo * 3.0 + i * 0.25, 1.0)
		var p := -_mira * (10.0 + f * 12.0) + Vector2(-_mira.y, _mira.x) * (i - 1.5) * 5.0
		draw_rect(Rect2(p.round(), Vector2.ONE * 2), Color(CLARO, (1.0 - f) * 0.8))
