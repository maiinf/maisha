extends Node2D
## Voluta breve de polvo al correr: se dibuja en el suelo bajo las botas.

const DURA := 0.34
var color := Color(0.86, 0.80, 0.66, 0.55)
var _t := 0.0
var _motas: Array[Dictionary] = []


func _ready() -> void:
	z_index = -1
	for i in 3:
		_motas.append({
			"p": Vector2(randf_range(-3.5, 3.5), randf_range(-1.5, 1.5)),
			"v": Vector2(randf_range(-10.0, 10.0), randf_range(-12.0, -3.0)),
			"r": randf_range(1.2, 2.3),
		})


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
		return
	for m in _motas:
		m["p"] = (m["p"] as Vector2) + (m["v"] as Vector2) * delta
	queue_redraw()


func _draw() -> void:
	var k := clampf(_t / DURA, 0.0, 1.0)
	var a := (1.0 - k * k) * color.a
	for m in _motas:
		var r := float(m["r"]) * (0.75 + 0.65 * k)
		draw_circle((m["p"] as Vector2).round(), r, Color(color.r, color.g, color.b, a))
