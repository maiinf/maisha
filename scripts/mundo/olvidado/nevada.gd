extends Node2D
## LA NEVADA del Sendero Olvidado: copos que caen en diagonal con el viento, delante de todo (cerca de la cámara),
## de tres tamaños (los grandes, más rápidos: están más cerca). Se dibuja todo aquí para que sea ligero.

const COPOS := 140
var _copos: Array[Dictionary] = []
var _tiempo := 0.0


func _ready() -> void:
	z_index = 4
	for i in COPOS:
		_copos.append(_nuevo(true))


func _nuevo(en_cualquier_sitio: bool) -> Dictionary:
	var capa := randi() % 3
	return {"p": Vector2(randf() * 700.0 - 30.0, randf() * 400.0 if en_cualquier_sitio else -10.0),
		"v": Vector2(randf_range(8, 18), [14.0, 24.0, 38.0][capa]), "capa": capa, "fase": randf() * TAU}


func _process(delta: float) -> void:
	_tiempo += delta
	for c in _copos:
		c["p"] += (c["v"] + Vector2(sin(_tiempo * 1.3 + c["fase"]) * 8.0, 0)) * delta
		if c["p"].y > 370.0 or c["p"].x > 680.0:
			var n := _nuevo(false)
			c["p"] = n["p"]
	# los copos van con la pantalla (no con el mundo): se colocan respecto a la cámara
	var cam := get_viewport().get_camera_2d()
	if cam:
		global_position = cam.get_screen_center_position() - Vector2(320, 180)
	queue_redraw()


func _draw() -> void:
	for c in _copos:
		var capa: int = c["capa"]
		var p: Vector2 = (c["p"] as Vector2).floor()
		var a: float = [0.45, 0.65, 0.85][capa]
		draw_rect(Rect2(p, Vector2.ONE * (1 + (1 if capa == 2 else 0))), Color(0.95, 0.97, 1.0, a))
