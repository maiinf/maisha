extends Node2D
## ESCALA DE CUERDA («"» en la Cañada del Eco): sube por la peña hasta la cornisa del quinto eco.
## Mientras no se pone su «marca», está enrollada arriba, atada a dos estacas, y la peña no deja pasar.
## Cuando Mbuzi la descuelga (al devolverle sus cencerros), se desenrolla tramo a tramo hacia abajo, con el
## golpe seco de cada peldaño contra la roca, y se puede subir por ella.
## Dibujo: arte/mundos/raiz/canada/escala.png (herramientas/pintar_canada.py): 0 enrollada · 1 tramo · 2 el último.

const R := preload("res://scripts/combate/reglas_combate.gd")
const DIBUJO := preload("res://arte/mundos/raiz/canada/escala.png")

var casillas: Array[Vector2i] = []
var marca := ""
var _bajados := 0                 # cuántos tramos cuelgan ya
var _cuerpo: StaticBody2D
var _rollos: Array[Sprite2D] = []
var _tramos: Array[Sprite2D] = []      # uno por fila, de arriba abajo
var _centro_x := 0.0


func _ready() -> void:
	add_to_group("escalas")
	# de arriba abajo: el primer tramo cuelga de la cornisa
	casillas.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y or (a.y == b.y and a.x < b.x))
	var arriba := casillas[0].y if not casillas.is_empty() else 0
	var abajo := casillas[-1].y if not casillas.is_empty() else 0
	# una sola escala por fila, centrada en el hueco (que mide dos casillas de ancho)
	var izquierda := 1 << 30
	var derecha := -(1 << 30)
	for c in casillas:
		izquierda = mini(izquierda, c.x)
		derecha = maxi(derecha, c.x)
	_centro_x = (izquierda + derecha + 1) * R.CASILLA / 2.0
	for y in range(arriba, abajo + 1):
		var tramo := Sprite2D.new()
		tramo.texture = DIBUJO
		tramo.hframes = 3
		tramo.frame = 2 if y == abajo else 1
		tramo.centered = false
		tramo.position = Vector2(_centro_x - 8, y * R.CASILLA)
		tramo.z_index = -4               # sobre el suelo y la peña, bajo Maisha
		add_child(tramo)
		_tramos.append(tramo)
	if Estado.tiene(marca):
		_bajados = _tramos.size()
		return
	for t in _tramos:
		t.visible = false
	# el rollo, en el borde de la cornisa (una casilla por encima de la escala)
	var rollo := Sprite2D.new()
	rollo.texture = DIBUJO
	rollo.hframes = 3
	rollo.frame = 0
	rollo.centered = false
	rollo.position = Vector2(_centro_x - 8, (arriba - 1) * R.CASILLA)
	rollo.z_index = -4
	add_child(rollo)
	_rollos.append(rollo)
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


func descolgada() -> bool:
	return _bajados >= _tramos.size()


## (para las pruebas y el mapa: se puede llamar «arreglada», como a la pasarela rota)
func arreglada() -> bool:
	return descolgada()


func _al_poner_marca(m: String) -> void:
	if m != marca:
		return
	var t := create_tween()
	for r in _rollos:
		t.parallel().tween_property(r, "modulate:a", 0.0, 0.25)
	for s in _tramos:
		t.tween_callback(func() -> void:
			s.visible = true
			s.scale = Vector2(1, 0.2)
			s.create_tween().tween_property(s, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_BACK)
			Sonido.efecto("escala_tramo", 0.0, s.global_position + Vector2(8, 8))
			_bajados += 1)
		t.tween_interval(0.14)
	t.tween_callback(func() -> void:
		for r in _rollos:
			r.queue_free()
		_rollos.clear()
		if _cuerpo:
			_cuerpo.queue_free()
			_cuerpo = null)
