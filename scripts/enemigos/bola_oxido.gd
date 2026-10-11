extends Node2D
## BOLA DE ÓXIDO que escupe Konokono: vuela en arco (con su sombra en el suelo marcando dónde caerá)
## y al caer hace daño si Maisha está debajo y deja un charco de óxido que frena.

const DURA := 1.0
const RADIO := 10.0

var desde := Vector2.ZERO
var hasta := Vector2.ZERO
var al_caer: Callable
var _t := 0.0


func _ready() -> void:
	global_position = hasta
	z_index = 2


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()
	if _t >= DURA:
		Sonido.efecto("semilla_plantar", 0.0, global_position)
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		if maisha and maisha.global_position.distance_to(global_position) < RADIO:
			maisha.call("recibir_danio", 1, global_position, "contacto")
		if al_caer.is_valid():
			al_caer.call(global_position)
		queue_free()


func _draw() -> void:
	var f := clampf(_t / DURA, 0.0, 1.0)
	# la sombra en el suelo (crece)
	for y in range(-2, 3):
		var ancho := int(round(RADIO * f * sqrt(1.0 - (y / 3.0) * (y / 3.0))))
		draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.1, 0.04, 0.02, 0.2 + 0.35 * f))
	draw_arc(Vector2.ZERO, RADIO, 0, TAU, 20, Color(0.9, 0.45, 0.2, 0.3 + 0.4 * f), 1.0)
	# la bola en el aire (en arco desde la boca)
	var p := (desde - hasta).lerp(Vector2.ZERO, f) + Vector2(0, -sin(f * PI) * 60.0)
	draw_circle(p, 4.0, Color("6e3218"))
	draw_circle(p + Vector2(-1, -1), 2.0, Color("c67238"))
	draw_rect(Rect2(p + Vector2(1, 0), Vector2(1, 1)), Color("a855d6"))
