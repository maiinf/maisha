extends Node2D
## COSA CON LA QUE HABLAR: un punto invisible que muestra un texto al usarlo
## (los libros de una estantería, unas ruinas...). El texto está en datos/dialogos/raiz.json.

const CHARLA := preload("res://scripts/mundo/charla.gd")

@export var charla := ""
@export var radio_interaccion := 24.0
@export var altura_bocadillo := 20.0


func _ready() -> void:
	add_to_group("interactuables")


func interactuar() -> void:
	await CHARLA.hablar(self, charla)
