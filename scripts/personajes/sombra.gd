extends Node2D
## Sombra elíptica bajo los personajes: sigue suavemente la inclinación y altura del sol.
@export var ancho := 7.0
@export var fuerza := 0.35          # lo oscura que es (las casas grandes ya traen su sombra pintada)

var _ultimo_desp := Vector2.ZERO


func _process(_delta: float) -> void:
	var calidez := Reloj.calidez()
	var dia := Reloj.luz_dia()
	var desp := Vector2(1.2 + calidez * 1.8, 0.3) if dia > 0.25 else Vector2(-0.8, 0.2)
	if desp.distance_squared_to(_ultimo_desp) > 0.02:
		_ultimo_desp = desp
		queue_redraw()


func _draw() -> void:
	var calidez := Reloj.calidez()
	var dia := Reloj.luz_dia()
	var estira := 1.0 + calidez * 0.22
	var desp := Vector2((1.0 + calidez * 1.4) if dia > 0.25 else -0.6, 0.0)
	var opacidad := fuerza * lerpf(0.65, 1.0, dia)
	var puntos := PackedVector2Array()
	for i in 14:
		var a := TAU * i / 14.0
		puntos.append(desp + Vector2(cos(a) * ancho * estira, sin(a) * ancho * 0.38))
	draw_colored_polygon(puntos, Color(0.04, 0.06, 0.03, opacidad))

