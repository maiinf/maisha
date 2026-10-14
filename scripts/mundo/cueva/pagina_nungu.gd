extends Node2D
## UNA PÁGINA DEL DIARIO DE NUNGU, en el suelo de la cueva de las setas («ǹ»). Al leerla (Acción) se oye la
## conversación «nungu_pagina_<n>», que deja la marca «nungu_pagina/<n>». Brilla un poco hasta que se lee.

const DIBUJO := preload("res://arte/mundos/raiz/paso/pagina.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const TEX_LUZ := preload("res://scripts/mundo/gruta/oscuridad.gd")

var numero := 1
var radio_interaccion := 22.0
var altura_bocadillo := 18.0
var _luz: PointLight2D
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("paginas")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.offset = Vector2(0, -4)
	add_child(_sprite)
	_luz = PointLight2D.new()
	_luz.texture = TEX_LUZ.textura_luz(128)
	_luz.texture_scale = 0.35
	_luz.color = Color(1.0, 0.92, 0.7)
	add_child(_luz)
	_actualizar()


func leida() -> bool:
	return Estado.tiene("nungu_pagina/%d" % numero)


func _actualizar() -> void:
	_luz.energy = 0.25 if leida() else 0.8
	if leida():
		remove_from_group("paginas")


func interactuar() -> void:
	await CHARLA.hablar(self, "nungu_pagina_%d" % numero)
	_actualizar()
