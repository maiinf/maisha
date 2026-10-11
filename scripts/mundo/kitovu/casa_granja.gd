extends StaticBody2D
## LA CASA DE MZEE SHAMBA: la única que sigue en pie en el Kitovu. Su puerta lleva dentro.
## Grande, de troncos sobre piedra, con molino de agua, porche y buhardilla encendida.
## De la chimenea sale humo y la rueda del molino gira: es lo primero que ve Maisha.

const TEXTURA := preload("res://arte/mundos/kitovu/casa_granja.png")
const MOLINO := preload("res://arte/mundos/kitovu/molino.png")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const HUMO := [Color("a0a596"), Color("7a806d"), Color("c9b07e")]

var _humo: Array[Dictionary] = []
var _molino: Sprite2D
var _tiempo := 0.0
var _azar := RandomNumberGenerator.new()


func _ready() -> void:
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 84.0)
	sombra.set("fuerza", 0.14)
	add_child(sombra)
	var sprite := Sprite2D.new()
	sprite.texture = TEXTURA
	sprite.centered = false
	sprite.offset = Vector2(-100, -138)
	add_child(sprite)
	# la rueda del molino, detrás de la casa (a la izquierda)
	_molino = Sprite2D.new()
	_molino.texture = MOLINO
	_molino.hframes = 2
	_molino.position = Vector2(-80, -34)
	add_child(_molino)
	move_child(_molino, sprite.get_index())
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(sprite)
		gestor.aplicar_a(_molino)
	for r in [Rect2(-76, -26, 66, 26), Rect2(10, -26, 66, 26), Rect2(-10, -26, 20, 16), Rect2(-98, -22, 24, 22)]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = r.size
		forma.shape = caja
		forma.position = r.get_center()
		add_child(forma)
	var puerta: Area2D = PUERTA.new()
	puerta.id = "casa_shamba"
	puerta.destino = "casa_shamba"
	puerta.destino_puerta = "salida"
	puerta.salida = Vector2.DOWN
	puerta.tam = Vector2(14, 8)
	puerta.position = Vector2(0, -6)
	add_child(puerta)


func _process(delta: float) -> void:
	_tiempo += delta
	_molino.frame = int(_tiempo * 4.0) % 2
	if _azar.randf() < delta * 3.0:
		_humo.append({"pos": Vector2(46, -140), "vida": 0.0, "color": HUMO[_azar.randi() % 3]})
	for h in _humo:
		h["vida"] += delta
		h["pos"] += Vector2(4.0 + sin(h["vida"] * 2.0) * 3.0, -9.0) * delta
	_humo = _humo.filter(func(h: Dictionary) -> bool: return h["vida"] < 3.0)
	queue_redraw()


func _draw() -> void:
	for h in _humo:
		var r: float = 1.5 + h["vida"] * 1.3
		draw_circle(h["pos"].round(), r, Color(h["color"], 0.5 * (1.0 - h["vida"] / 3.0)))
