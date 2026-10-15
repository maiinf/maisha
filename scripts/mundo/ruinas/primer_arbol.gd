extends Node2D
## EL PRIMER ÁRBOL, en el centro de la plaza de las Ruinas. Enfermo de miedo a acabarse: Giza es su miedo.
## No se le pelea a él: se pelea contra su miedo (ruinas/miedo.gd). Cuando las nueve piedras del recuerdo despiertan,
## se le abre el hueco del tronco y queda al aire el CORAZÓN DE GIZA (una masa violeta que late): ese sí se rompe
## (4 golpes de cetro; una semilla, 2). Al romperlo, el árbol se cura (la copa se vuelve dorada) y suelta las hojas.

signal corazon_roto

const DIBUJO := preload("res://arte/mundos/raiz/ruinas/primer_arbol.png")
const VIDA_CORAZON := 4

var corazon_abierto := false
var curado := false
var vida_corazon := VIDA_CORAZON
var _sprite: Sprite2D
var _corazon: Node2D
var _tiempo := 0.0
var _temblor := 0.0
var _destello := 0.0
var _hojas: Array[Dictionary] = []


func _ready() -> void:
	add_to_group("primer_arbol")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.centered = false
	_sprite.offset = Vector2(-88, -196)
	add_child(_sprite)
	var cuerpo := StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(56, 16)
	forma.shape = caja
	forma.position = Vector2(0, -8)
	cuerpo.add_child(forma)
	add_child(cuerpo)
	# el corazón: se golpea desde delante del tronco (su punto está al pie), se dibuja en el hueco
	_corazon = Node2D.new()
	_corazon.set_script(preload("res://scripts/mundo/ruinas/corazon_arbol.gd"))
	_corazon.position = Vector2(2, 10)
	add_child(_corazon)
	_corazon.set("arbol", self)


func abrir_corazon() -> void:
	if corazon_abierto or curado:
		return
	corazon_abierto = true
	_sprite.frame = 1
	_temblor = 0.8
	Sonido.efecto("mascara_cruje", 0.0, global_position)
	_corazon.call("activar", true)


func herir_corazon(cantidad: int) -> void:
	if not corazon_abierto or curado:
		return
	vida_corazon -= cantidad
	_destello = 0.15
	_temblor = 0.3
	Sonido.efecto("corazon_golpeado", 0.0, global_position)
	if vida_corazon <= 0:
		corazon_abierto = false
		_corazon.call("activar", false)
		Sonido.efecto("corazon_roto", 0.0, global_position)
		corazon_roto.emit()


## Se cura: la corteza viva y la copa dorada; empiezan a caer las hojas
func curar() -> void:
	curado = true
	corazon_abierto = false
	_corazon.call("activar", false)
	_sprite.frame = 2
	_temblor = 0.6


func temblar(segundos := 0.4) -> void:
	_temblor = maxf(_temblor, segundos)


func _process(delta: float) -> void:
	_tiempo += delta
	_temblor = maxf(0.0, _temblor - delta)
	_destello = maxf(0.0, _destello - delta)
	_sprite.position = Vector2(randf_range(-1, 1), 0).round() if _temblor > 0.0 else Vector2.ZERO
	_sprite.modulate = Color(1.6, 1.4, 1.8) if _destello > 0.0 else Color.WHITE
	if curado and randf() < delta * 6.0:
		_hojas.append({"p": Vector2(randf_range(-70, 70), randf_range(-170, -120)), "v": Vector2(randf_range(-6, 6), randf_range(10, 20)), "t": 0.0, "fase": randf() * TAU})
	for h in _hojas:
		h["t"] += delta
		h["p"] += (h["v"] + Vector2(sin(_tiempo * 2.0 + h["fase"]) * 10.0, 0)) * delta
	_hojas = _hojas.filter(func(h: Dictionary) -> bool: return h["t"] < 9.0 and h["p"].y < 10.0)
	queue_redraw()


func _draw() -> void:
	# el corazón de Giza en el hueco del tronco: una masa violeta que late, con hilos que se agarran a la madera
	if corazon_abierto:
		var c := Vector2(2, -62)
		var late := 0.5 + 0.5 * sin(_tiempo * 5.0)
		for i in 3:
			draw_circle(c, 9.0 - i * 2.5 + late * 1.5, Color(0.35 + i * 0.15, 0.12 + i * 0.08, 0.55 + i * 0.12, 0.9))
		draw_circle(c + Vector2(-2, -3), 2.0, Color(0.95, 0.8, 1.0, 0.8))
		for k in 6:
			var a := k * TAU / 6.0 + _tiempo * 0.5
			draw_line(c, c + Vector2(cos(a) * 13.0, sin(a) * 17.0), Color(0.55, 0.25, 0.85, 0.7), 1.0)
		# cuánta vida le queda: puntitos bajo el hueco
		for k in vida_corazon:
			draw_rect(Rect2(Vector2(-6 + k * 4, -40), Vector2(2, 2)), Color("c890ff"))
	# las hojas doradas que caen cuando se cura
	for h in _hojas:
		var p: Vector2 = (h["p"] as Vector2).floor()
		var giro := int(h["t"] * 4.0 + h["fase"]) % 2
		draw_rect(Rect2(p, Vector2(2 - giro, 1 + giro)), Color("f0cc60"))
		draw_rect(Rect2(p + Vector2(1, 0), Vector2.ONE), Color("fbe49a"))
