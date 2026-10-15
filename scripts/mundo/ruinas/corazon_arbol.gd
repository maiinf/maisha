extends Node2D
## El punto que se golpea del corazón de Giza del Primer Árbol (al pie del tronco, delante). Solo cuenta abierto.

var arbol: Node2D


func activar(si: bool) -> void:
	if si:
		add_to_group("golpeables")
		add_to_group("daniables")
	else:
		remove_from_group("golpeables")
		remove_from_group("daniables")


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if arbol == null or not arbol.corazon_abierto:
		return false
	arbol.call("herir_corazon", danio)
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if arbol and arbol.corazon_abierto:
		arbol.call("herir_corazon", 2 if tipo == "explosion" else cantidad)
