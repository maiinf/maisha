extends StaticBody2D
## EL ARMARIO DE NUNGU: al fondo de su casa. Cerrado con una cerradura de hierro de Corteza (lleva su marca). Con la
## llave («llave_nungu») se abre (marca «armario_abierto»): dentro hay una trampilla con una escalera que baja a la cueva
## de las setas. Dibujo: arte/mundos/raiz/paso/armario.png (0 cerrado, 1 abierto).

const DIBUJO := preload("res://arte/mundos/raiz/paso/armario.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")

var radio_interaccion := 30.0
var altura_bocadillo := 66.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("armario")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-28, -62)
	add_child(_sprite)
	actualizar()


func actualizar() -> void:
	_sprite.frame = 1 if Estado.tiene("armario_abierto") else 0


func punto_interaccion() -> Vector2:
	return global_position + Vector2(0, 10)


func interactuar() -> void:
	if not Estado.tiene("armario_abierto") and Estado.tiene("llave_nungu"):
		Sonido.efecto("puerta", 0.0, global_position)
		Estado.marcar("armario_abierto")
		actualizar()
	await CHARLA.hablar(self, "nungu_armario")
