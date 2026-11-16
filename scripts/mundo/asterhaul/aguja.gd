extends Node2D
## UN CAMBIO DE AGUJAS (Asterhaul, las Galerías de Ámbar): una palanca junto a un desvío de la vía. Un golpe de
## cetro la gira al siguiente ramal (`ramales`, en orden). Lo que rueda por la vía y llega a su `casilla` sale por
## donde ella manda (asterhaul/via.gd). Su posición se guarda (`marca` + el número del ramal en Estado.extra).
## Dibujo: arte/mundos/asterhaul/galerias/aguja.png, 0 oeste · 1 norte · 2 sur.

signal cambiada

const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/aguja.png")
const FOTOGRAMA := {Vector2i.LEFT: 0, Vector2i.UP: 1, Vector2i.DOWN: 2}

## la casilla del desvío (la palanca se dibuja al lado)
var casilla := Vector2i.ZERO
var ramales: Array[Vector2i] = [Vector2i.LEFT, Vector2i.UP]
var marca := ""
var _cual := 0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("agujas")
	add_to_group("golpeables")
	if marca != "":
		_cual = int(Estado.extra.get("agujas", {}).get(marca, 0)) % ramales.size()
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.offset = Vector2(0, -13)
	add_child(_sprite)
	_sprite.frame = FOTOGRAMA[direccion()]


func direccion() -> Vector2i:
	return ramales[_cual]


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	_cual = (_cual + 1) % ramales.size()
	_sprite.frame = FOTOGRAMA[direccion()]
	if marca != "":
		var agujas: Dictionary = Estado.extra.get("agujas", {}).duplicate()
		agujas[marca] = _cual
		Estado.extra["agujas"] = agujas
		Estado.guardar_pronto()
	Sonido.efecto("aguja_cambiar", 0.0, global_position)
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje("Desvío: " + {Vector2i.LEFT: "al oeste", Vector2i.UP: "al norte", Vector2i.DOWN: "al sur"}[direccion()])
	cambiada.emit()
	return true
