extends Node2D
## Algo que se LEE con Acción (una estela, un letrero grabado...): no se dibuja (el dibujo lo pone la región),
## solo dice su conversación `charla`.

const CHARLA := preload("res://scripts/mundo/charla.gd")

@export var charla := ""
var radio_interaccion := 24.0


func _ready() -> void:
	add_to_group("interactuables")


func interactuar() -> void:
	await CHARLA.hablar(self, charla)
