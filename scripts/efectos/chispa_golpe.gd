extends Node2D
## Donde acierta el cetro: una estrella de luz que se abre y unas chispitas que saltan.

const DURA := 0.24
var direccion := Vector2.RIGHT
var color := Color("fff3c4")
var escala := 1.0
var _t := 0.0
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	z_index = 8
	var dir := direccion.normalized() if direccion.length_squared() > 0.001 else Vector2.RIGHT
	for i in 10:
		var a := dir.angle() + randf_range(-1.25, 1.25)
		_chispas.append({"pos": Vector2.ZERO, "vel": Vector2.from_angle(a) * randf_range(75, 155) * escala,
			"largo": randf_range(2.2, 4.2) * escala})


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
		return
	for c in _chispas:
		c["pos"] += c["vel"] * delta
		c["vel"] *= 0.84
	queue_redraw()


func _draw() -> void:
	var k := clampf(_t / DURA, 0.0, 1.0)
	var a := 1.0 - k * k
	var dir := direccion.normalized() if direccion.length_squared() > 0.001 else Vector2.RIGHT
	var perp := Vector2(-dir.y, dir.x)
	# Halo expansivo breve
	if k < 0.6:
		var rk := k / 0.6
		draw_arc(Vector2.ZERO, (3.0 + 13.0 * rk) * escala, 0.0, TAU, 20, Color(color, 0.72 * (1.0 - rk)), 1.5)
	# Arco de tajo direccional en dirección del golpe
	if k < 0.72:
		var ak := k / 0.72
		var ang0 := dir.angle() - 0.85
		var ang1 := dir.angle() + 0.85
		draw_arc(dir * (2.0 * escala * ak), (7.0 + 9.0 * ak) * escala, ang0, ang1, 10, Color(color, 0.9 * (1.0 - ak)), 1.5)
	# Estrella romboidal de 4 puntas orientada + destello central blanco
	var largo := (4.0 + 11.0 * minf(1.0, k * 3.4)) * escala
	var corto := largo * 0.55
	var rombo := PackedVector2Array([
		dir * largo,
		(dir + perp) * (1.5 * escala),
		perp * corto,
		(-dir + perp) * (1.5 * escala),
		-dir * (largo * 0.75),
		(-dir - perp) * (1.5 * escala),
		-perp * corto,
		(dir - perp) * (1.5 * escala),
	])
	draw_colored_polygon(rombo, Color(color, 0.85 * a))
	for d in [dir, perp, (dir + perp).normalized(), (dir - perp).normalized()]:
		var l: float = largo * (1.05 if d == dir or d == perp else 0.58)
		draw_line((-d * l).round(), (d * l).round(), Color(1.0, 0.98, 0.9, a), 1.0)
	draw_rect(Rect2(-1.5, -1.5, 3, 3), Color(1, 1, 1, a))
	if k < 0.38:
		draw_circle(Vector2.ZERO, (6.0 - k * 8.0) * escala, Color(1, 1, 1, 0.75 * (1.0 - k / 0.38)))
	# Estelas cinéticas de chispas
	for c in _chispas:
		var vel: Vector2 = c["vel"]
		var d_v := vel.normalized() if vel.length_squared() > 1.0 else dir
		var len_s: float = c["largo"] * (1.0 - 0.65 * k)
		var p: Vector2 = c["pos"]
		draw_line(p.round(), (p - d_v * len_s).round(), Color(color, a), 1.0)
