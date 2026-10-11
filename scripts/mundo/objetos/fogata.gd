extends Node2D
## FOGATA: un fuego pequeño de campamento (llamas que bailan, resplandor, chispas que suben y un poco de humo).

const LLAMA := [Color("b8420f"), Color("ef8a26"), Color("f9b947"), Color("fde27e")]

var _tiempo := 0.0
var _chispas: Array[Dictionary] = []
var _luz: Node2D


func _ready() -> void:
	_luz = Node2D.new()
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luz.material = suma
	_luz.z_index = -1
	_luz.draw.connect(_dibujar_luz)
	add_child(_luz)
	_tiempo = randf() * 5.0


func _process(delta: float) -> void:
	_tiempo += delta
	if randf() < delta * 7.0:
		_chispas.append({"p": Vector2(randf_range(-2, 2), -5), "v": Vector2(randf_range(-6, 6), randf_range(-26, -14)), "t": 0.0,
			"dura": randf_range(0.5, 1.2), "humo": randf() < 0.3})
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
	_chispas = _chispas.filter(func(c: Dictionary) -> bool: return c["t"] < c["dura"])
	queue_redraw()
	_luz.queue_redraw()


func _dibujar_luz() -> void:
	var temblor := 0.85 + 0.15 * sin(_tiempo * 13.0) * sin(_tiempo * 7.3)
	_luz.draw_circle(Vector2(0, -3), 26.0 * temblor, Color(1.0, 0.5, 0.15, 0.07))
	_luz.draw_circle(Vector2(0, -3), 14.0 * temblor, Color(1.0, 0.6, 0.2, 0.12))


func _draw() -> void:
	# troncos cruzados
	draw_line(Vector2(-4, 0), Vector2(4, -2), Color("3a261d"), 2.0)
	draw_line(Vector2(-4, -2), Vector2(4, 0), Color("492e23"), 2.0)
	# llamas: tres lenguas (roja por fuera, amarilla por dentro)
	for k in 3:
		var x := -2.5 + k * 2.5
		var alto := (6.0 + 3.0 * sin(_tiempo * (9.0 + k * 2.1) + k * 1.9)) * (1.2 if k == 1 else 0.85)
		var vaiven := sin(_tiempo * 7.0 + k) * 1.2
		for capa in 3:
			var f := 1.0 - capa * 0.3
			var ancho := (2.2 - capa * 0.6)
			draw_colored_polygon(PackedVector2Array([Vector2(x - ancho, -1), Vector2(x + vaiven * f, -1 - alto * f).round(), Vector2(x + ancho, -1)]),
				LLAMA[capa + (1 if k == 1 else 0)])
	for c in _chispas:
		var f: float = c["t"] / c["dura"]
		if c["humo"]:
			draw_circle(c["p"] + Vector2(0, -6), 1.5 + f * 2.5, Color(0.6, 0.58, 0.55, 0.25 * (1.0 - f)))
		else:
			draw_rect(Rect2((c["p"] as Vector2).round(), Vector2.ONE), Color(LLAMA[3] if f < 0.4 else LLAMA[1], 1.0 - f))
