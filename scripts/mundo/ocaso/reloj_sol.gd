extends StaticBody2D
## UN RELOJ DE SOL (el Valle del Ocaso): un golpe de cetro gira el atardecer a la hora siguiente (oeste → sur →
## este → oeste; ocaso/sol.gd). Mientras no esté puesta su marca `requiere` (Mwanga enseña a girarlos), está
## atascado: el golpe rebota. Dibujo: arte/mundos/ocaso/mirador/reloj.png (0 oeste · 1 sur · 2 este).

signal atascado

const DIBUJO := preload("res://arte/mundos/ocaso/mirador/reloj.png")

var requiere := ""
var _sprite: Sprite2D
var _sol: Node


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("relojes_sol")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.offset = Vector2(0, -17)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(18, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)
	_sol = get_tree().get_first_node_in_group("sol")
	_sol.cambiada.connect(func(h: int) -> void: _sprite.frame = h)
	_sprite.frame = _sol.hora


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if requiere != "" and not Estado.tiene(requiere):
		atascado.emit()
		return false
	_sol.girar()
	Sonido.efecto("aguja_cambiar", 0.0, global_position, 0.1)
	Impacto.temblar(1.5, 0.3)
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje("El sol, " + _sol.NOMBRE[_sol.hora])
	return true
