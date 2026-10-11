extends Node2D
## Lo que acompaña a la explosión de una semilla (además de los destellos de cada casilla):
## un fogonazo de luz en el centro, una onda que se abre por el suelo, humo que sube y
## chispas y terrones que saltan y caen.

const DURA := 1.0
var fuerza := 1.0
var _t := 0.0
var _humo: Array[Dictionary] = []
var _chispas: Array[Dictionary] = []
var _luz: Node2D


func _ready() -> void:
	z_index = 4
	for i in 7:
		_humo.append({"pos": Vector2(randf_range(-10, 10), randf_range(-6, 2)), "r": randf_range(3, 6),
			"sube": randf_range(10, 22), "tono": randf_range(0.55, 0.8)})
	for i in int(14 * fuerza):
		var a := randf() * TAU
		_chispas.append({"pos": Vector2(0, -4), "vel": Vector2(cos(a) * randf_range(40, 110), sin(a) * randf_range(30, 70) - 60),
			"tierra": randf() < 0.45})
	# el fogonazo va en una capa que suma luz
	_luz = Node2D.new()
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luz.material = suma
	_luz.draw.connect(_dibujar_luz)
	add_child(_luz)


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
		return
	for h in _humo:
		h["pos"].y -= h["sube"] * delta
		h["r"] += 5.0 * delta
	for c in _chispas:
		c["vel"].y += 260.0 * delta
		c["pos"] += c["vel"] * delta
	queue_redraw()
	_luz.queue_redraw()


func _dibujar_luz() -> void:
	# fogonazo
	if _t < 0.18:
		var k := _t / 0.18
		_luz.draw_circle(Vector2(0, -6), (10.0 + 20.0 * k) * fuerza, Color(1.0, 0.75, 0.35, 0.35 * (1.0 - k)))
		_luz.draw_circle(Vector2(0, -6), (5.0 + 6.0 * k) * fuerza, Color(1.0, 0.95, 0.8, 0.6 * (1.0 - k)))


func _draw() -> void:
	# onda por el suelo: un óvalo que se abre y se desvanece
	if _t < 0.4:
		var k := _t / 0.4
		var r := (8.0 + 38.0 * k) * fuerza
		draw_arc(Vector2.ZERO, r, 0, TAU, 32, Color(1.0, 0.95, 0.75, 0.55 * (1.0 - k)), 1.0)
	# humo
	for h in _humo:
		var a := clampf(1.0 - (_t - 0.1) / 0.9, 0.0, 1.0) * clampf(_t / 0.1, 0.0, 1.0)
		draw_circle(h["pos"].round(), h["r"], Color(h["tono"], h["tono"] * 0.95, h["tono"] * 0.9, 0.35 * a))
	# chispas (doradas) y terrones (de tierra) que caen
	for c in _chispas:
		var a := 1.0 - _t / DURA
		var color := Color("7c5843") if c["tierra"] else Color("fde27e")
		draw_rect(Rect2(c["pos"].round(), Vector2.ONE * (2 if c["tierra"] else 1)), Color(color, a))
