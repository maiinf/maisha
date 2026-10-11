extends Node2D
## PASARELA ROTA («"» en el mapa): un tramo de pasarela que se ha hundido. Solo quedan los pilotes y alguna tabla
## colgando; no se puede pasar (es agua). Cuando se pone su «marca» (Korongo la arregla al devolverle sus nasas),
## las tablas nuevas aparecen una a una, a martillazos, y ya se puede cruzar.

const R := preload("res://scripts/combate/reglas_combate.gd")
const MADERA := [Color("251812"), Color("3a261d"), Color("5b392b"), Color("6d4534"), Color("905c45"), Color("b88a62")]

var casillas: Array[Vector2i] = []
var marca := ""
var _puestas := 0.0               # cuántas casillas tienen ya tablas (se anima al arreglarla)
var _cuerpo: StaticBody2D
var _tiempo := 0.0


func _ready() -> void:
	z_index = -6
	add_to_group("pasarelas_rotas")
	if Estado.tiene(marca):
		_puestas = casillas.size()
	else:
		_cuerpo = StaticBody2D.new()
		add_child(_cuerpo)
		for c in casillas:
			var forma := CollisionShape2D.new()
			var caja := RectangleShape2D.new()
			caja.size = Vector2(R.CASILLA, R.CASILLA)
			forma.shape = caja
			forma.position = Vector2(c) * R.CASILLA + Vector2.ONE * 8
			_cuerpo.add_child(forma)
		Estado.marca_puesta.connect(_al_poner_marca)
	queue_redraw()


func arreglada() -> bool:
	return _puestas >= casillas.size()


func _al_poner_marca(m: String) -> void:
	if m != marca:
		return
	# las casillas se ordenan de oeste a este y las tablas se ponen una a una
	casillas.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x or (a.x == b.x and a.y < b.y))
	var t := create_tween()
	for k in casillas.size():
		t.tween_callback(func() -> void:
			_puestas = k + 1
			Sonido.efecto("cerca_martillo", 0.0, global_position + Vector2(casillas[k]) * R.CASILLA)
			queue_redraw())
		t.tween_interval(0.18)
	t.tween_callback(func() -> void:
		if _cuerpo:
			_cuerpo.queue_free()
			_cuerpo = null
		Sonido.efecto("construir"))


func _process(delta: float) -> void:
	_tiempo += delta
	if not arreglada():
		queue_redraw()


func _draw() -> void:
	for k in casillas.size():
		var c: Vector2i = casillas[k]
		var o := Vector2(c) * R.CASILLA
		if k < _puestas:
			# tablas nuevas, más claras (de través), con sus clavos
			for i in 4:
				var x := o.x + i * 4
				draw_rect(Rect2(x, o.y, 4, 16), MADERA[5] if i % 2 else MADERA[4])
				draw_rect(Rect2(x, o.y, 1, 16), MADERA[1])
				draw_rect(Rect2(x + 2, o.y + 2, 1, 1), Color("a0a596"))
				draw_rect(Rect2(x + 2, o.y + 13, 1, 1), Color("a0a596"))
			continue
		# roto: dos pilotes que asoman del agua (con su ondita) y, en algunas casillas, una tabla torcida que flota
		var onda := sin(_tiempo * 2.0 + c.x * 1.3) * 0.5
		for p in [Vector2(3, 3 + (c.x % 2) * 8), Vector2(12, 11 - (c.x % 2) * 6)]:
			var pie: Vector2 = o + p
			draw_rect(Rect2(pie + Vector2(-2, 1 + onda), Vector2(5, 1)), Color(0.62, 0.82, 0.82, 0.6))
			draw_rect(Rect2(pie + Vector2(-1, -4), Vector2(3, 5)), MADERA[2])
			draw_rect(Rect2(pie + Vector2(-1, -4), Vector2(1, 5)), MADERA[3])
			draw_rect(Rect2(pie + Vector2(-1, -5), Vector2(3, 1)), MADERA[4])
		if (c.x + c.y) % 3 == 0:
			var centro := o + Vector2(8, 8 + onda)
			var pts := PackedVector2Array([centro + Vector2(-6, -2), centro + Vector2(5, -4), centro + Vector2(6, -1), centro + Vector2(-5, 1)])
			draw_colored_polygon(pts, MADERA[3])
			draw_line(pts[0], pts[1], MADERA[4], 1.0)
