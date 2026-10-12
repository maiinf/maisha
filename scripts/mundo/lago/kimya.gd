extends Node2D
## KIMYA, EL SILENCIO, en la isla del Lago Espejo. Solo existe en el reflejo: cuando el lago es espejo
## (la «calma» de espejo_lago.gd) aparece en el círculo de piedras, flotando, hecha de luz plateada; si el agua
## tiembla, se desvanece. Con Acción se habla con ella (conversación «kimya» de datos/dialogos/raiz.json).
## Se dibuja con código: una figura alta y estrecha, casi transparente, con la cabeza serena (ojos cerrados),
## dos hilos de luz que ondean hacia atrás y el cuerpo que se deshace en niebla.

const CHARLA := preload("res://scripts/mundo/charla.gd")
const PLATA := Color(0.85, 0.93, 0.92)
const VERDE_AGUA := Color(0.43, 0.69, 0.69)

var radio_interaccion := 30.0
var altura_bocadillo := 44.0
var _visible_por := 0.0           # 0..1: cuánto se ve (sigue a la calma del lago)
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("kimya")
	z_index = 1
	visible = false


func _process(delta: float) -> void:
	_tiempo += delta
	var espejo := get_tree().get_first_node_in_group("espejo_lago")
	var calma: float = espejo.calma if espejo else 0.0
	_visible_por = move_toward(_visible_por, 1.0 if calma > 0.9 else 0.0, delta * (0.6 if calma > 0.9 else 1.5))
	visible = _visible_por > 0.25          # (solo se puede hablar con ella si se ve bien)
	modulate.a = _visible_por
	queue_redraw()


func punto_interaccion() -> Vector2:
	return global_position


func interactuar() -> void:
	await CHARLA.hablar(self, "kimya")


func _draw() -> void:
	var flota := sin(_tiempo * 1.2) * 2.0
	var base := Vector2(0, -10 + flota)
	# el halo
	for k in 4:
		draw_circle(base + Vector2(0, -12), 22.0 - k * 4.0, Color(VERDE_AGUA, 0.06 + k * 0.03))
	# el cuerpo, que se deshace en niebla hacia abajo
	for k in 14:
		var t := k / 13.0
		var c := base + Vector2(sin(t * 3.0 + _tiempo) * 1.5, -20.0 + t * 26.0)
		draw_circle(c, (5.5 - t * 4.0), Color(PLATA, (1.0 - t * 0.85) * 0.75))
	# la cabeza, redonda y serena
	var cabeza := base + Vector2(0, -26)
	draw_circle(cabeza, 6.0, Color(PLATA, 0.9))
	draw_circle(cabeza + Vector2(-1.5, -1.5), 3.0, Color(1, 1, 1, 0.5))
	# los ojos cerrados (mirando abajo)
	for dx in [-2.2, 2.2]:
		var o := cabeza + Vector2(dx, 0.5)
		draw_line(o + Vector2(-1.3, -0.5), o + Vector2(0, 0.4), Color(0.2, 0.38, 0.38, 0.9), 1.0)
		draw_line(o + Vector2(0, 0.4), o + Vector2(1.3, -0.5), Color(0.2, 0.38, 0.38, 0.9), 1.0)
	# los hilos de luz, largos, que caen a los lados ondeando como cintas (no son cuernos)
	for lado in [-1.0, 1.0]:
		var pts := PackedVector2Array()
		for k in 16:
			var t := k / 15.0
			pts.append(cabeza + Vector2(lado * (4.0 + t * 9.0 + sin(t * 5.0 + _tiempo * 1.6 + lado) * 2.0), -1.0 + t * 16.0))
		draw_polyline(pts, Color(1, 1, 1, 0.6), 1.0)
	# motas de luz que suben
	for k in 5:
		var f := fmod(_tiempo * 0.4 + k * 0.2, 1.0)
		var p := base + Vector2(sin(k * 2.1) * 10.0, 4.0 - f * 40.0)
		draw_rect(Rect2(p.round(), Vector2.ONE), Color(1, 1, 1, (1.0 - f) * 0.8))
