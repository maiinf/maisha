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
	for i in 8:
		_humo.append({"pos": Vector2(randf_range(-11, 11), randf_range(-6, 3)) * fuerza, "r": randf_range(3.5, 6.5) * fuerza,
			"sube": randf_range(12, 24), "tono": randf_range(0.55, 0.82)})
	for i in int(18 * fuerza):
		var a := randf() * TAU
		_chispas.append({"pos": Vector2(0, -4), "vel": Vector2(cos(a) * randf_range(45, 125) * fuerza, sin(a) * randf_range(32, 74) * fuerza - 65),
			"tierra": randf() < 0.42})
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
		h["r"] += 5.5 * delta
	for c in _chispas:
		c["vel"].y += 260.0 * delta
		c["pos"] += c["vel"] * delta
		if c["tierra"] and c["pos"].y > 4.0 and c["vel"].y > 0.0:
			c["pos"].y = 4.0
			c["vel"].y *= -0.32
			c["vel"].x *= 0.65
	queue_redraw()
	_luz.queue_redraw()


func _dibujar_luz() -> void:
	# fogonazo aditivo multicapa + rayos radiales breves
	if _t < 0.22:
		var k := _t / 0.22
		var inv := 1.0 - k
		_luz.draw_circle(Vector2(0, -6), (13.0 + 24.0 * k) * fuerza, Color(1.0, 0.68, 0.28, 0.36 * inv))
		_luz.draw_circle(Vector2(0, -6), (6.0 + 8.0 * k) * fuerza, Color(1.0, 0.95, 0.82, 0.68 * inv))
		if k < 0.65:
			var rk := (12.0 + 18.0 * k) * fuerza
			for ang in [0.4, 1.15, 2.0, 2.75]:
				var d := Vector2.from_angle(ang)
				_luz.draw_line(Vector2(0, -6) - d * rk, Vector2(0, -6) + d * rk, Color(1.0, 0.92, 0.70, 0.55 * (1.0 - k / 0.65)), 1.0)


func _anillo_suelo(radio: float, col: Color, grosor: float) -> void:
	var pts := PackedVector2Array()
	for i in 33:
		var ang := TAU * float(i) / 32.0
		pts.append(Vector2(cos(ang) * radio, sin(ang) * radio * 0.68))
	draw_polyline(pts, col, grosor)


func _draw() -> void:
	# doble onda expansiva elíptica por el suelo
	if _t < 0.42:
		var k := _t / 0.42
		var e := 1.0 - pow(1.0 - k, 2.0)
		var r := (8.0 + 40.0 * e) * fuerza
		_anillo_suelo(r, Color(1.0, 0.85, 0.45, 0.42 * (1.0 - k)), 2.5)
		_anillo_suelo(r, Color(1.0, 0.98, 0.82, 0.72 * (1.0 - k)), 1.0)
	if _t > 0.08 and _t < 0.48:
		var k2 := (_t - 0.08) / 0.40
		var r2 := (6.0 + 28.0 * (1.0 - pow(1.0 - k2, 2.0))) * fuerza
		_anillo_suelo(r2, Color(0.95, 0.70, 0.32, 0.35 * (1.0 - k2)), 1.2)
	# humo con sombra inferior y volumen cálido
	for h in _humo:
		var a := clampf(1.0 - (_t - 0.1) / 0.9, 0.0, 1.0) * clampf(_t / 0.08, 0.0, 1.0)
		var p: Vector2 = h["pos"].round()
		var r: float = h["r"]
		draw_circle(p + Vector2(0, 1.5), r, Color(h["tono"] * 0.68, h["tono"] * 0.60, h["tono"] * 0.56, 0.32 * a))
		draw_circle(p, r * 0.88, Color(h["tono"], h["tono"] * 0.94, h["tono"] * 0.88, 0.34 * a))
	# chispas (estelas doradas) y terrones (rebotan al caer)
	for c in _chispas:
		var a := 1.0 - _t / DURA
		var p: Vector2 = c["pos"]
		if c["tierra"]:
			draw_rect(Rect2(p.round(), Vector2(2, 2)), Color("7c5843", a))
		else:
			var vel: Vector2 = c["vel"]
			draw_line(p.round(), (p - vel * 0.025).round(), Color("fde27e", a), 1.0)
			draw_rect(Rect2(p.round(), Vector2.ONE), Color(1.0, 0.98, 0.88, a))
