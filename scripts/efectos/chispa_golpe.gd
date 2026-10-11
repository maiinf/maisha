extends Node2D
## Donde acierta el cetro: una estrella de luz que se abre y unas chispitas que saltan.

const DURA := 0.22
var direccion := Vector2.RIGHT
var color := Color("fff3c4")
var _t := 0.0
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	z_index = 8
	for i in 7:
		var a := direccion.angle() + randf_range(-1.0, 1.0)
		_chispas.append({"pos": Vector2.ZERO, "vel": Vector2.from_angle(a) * randf_range(60, 130)})


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
		return
	for c in _chispas:
		c["pos"] += c["vel"] * delta
		c["vel"] *= 0.85
	queue_redraw()


func _draw() -> void:
	var k := _t / DURA
	var a := 1.0 - k
	# estrella de 4 puntas que crece y se apaga
	var largo := 3.0 + 9.0 * minf(1.0, k * 3.0)
	for dir in [Vector2.RIGHT, Vector2.DOWN, Vector2(1, 1).normalized(), Vector2(1, -1).normalized()]:
		var l: float = largo * (1.0 if dir.x == 0 or dir.y == 0 else 0.6)
		draw_line((-dir * l).round(), (dir * l).round(), Color(color, a), 1.0)
	draw_rect(Rect2(-1, -1, 3, 3), Color(1, 1, 1, a))
	if k < 0.35:
		draw_circle(Vector2.ZERO, 5.0 - k * 6.0, Color(1, 1, 1, 0.7 * (1.0 - k / 0.35)))
	for c in _chispas:
		draw_rect(Rect2(c["pos"].round(), Vector2.ONE), Color(color, a))
