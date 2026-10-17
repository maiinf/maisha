extends "res://scripts/mundo/aldea/aldeano.gd"
## Un vecino de Sigilia: un aldeano con su dibujo («id») y una conversación que puede ser otra («charla»).
## (Por ejemplo, Taa en la ciudad: el dibujo de Taa, pero lo que dice en Maandiko.)

@export var charla := ""


func interactuar() -> void:
	if charla == "":
		await super()
		return
	if _animado:
		_gesto = 1.0
	await CHARLA.hablar(self, charla)
