extends Node2D
## Sombra elíptica bajo los personajes.
@export var ancho := 7.0
@export var fuerza := 0.35          # lo oscura que es (las casas grandes ya traen su sombra pintada)

func _draw() -> void:
	var puntos := PackedVector2Array()
	for i in 14:
		var a := TAU * i / 14.0
		puntos.append(Vector2(cos(a) * ancho, sin(a) * ancho * 0.38))
	draw_colored_polygon(puntos, Color(0.04, 0.06, 0.03, fuerza))
