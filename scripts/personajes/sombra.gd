extends Node2D
## Sombra elíptica bajo los personajes: sigue suavemente la inclinación y altura del sol.
@export var ancho := 7.0
@export var fuerza := 0.35          # lo oscura que es (las casas grandes ya traen su sombra pintada)

var _ultimo_desp := Vector2.ZERO


func _ready() -> void:
	_ultimo_desp = desplazamiento()
	# (sin _process: el reloj avisa cuando la luz cambia, y solo entonces se mira si hay que redibujar)
	Reloj.luz_cambiada.connect(_al_cambiar_luz)


## Hacia dónde se va la sombra con el sol (si cambia lo bastante, hay que redibujarla)
static func desplazamiento() -> Vector2:
	return Vector2(1.2 + Reloj.calidez() * 1.8, 0.3) if Reloj.luz_dia() > 0.25 else Vector2(-0.8, 0.2)


func _al_cambiar_luz() -> void:
	var desp := desplazamiento()
	if desp.distance_squared_to(_ultimo_desp) > 0.02:
		_ultimo_desp = desp
		queue_redraw()


func _draw() -> void:
	dibujar(self, Vector2.ZERO, ancho, fuerza)


## La elipse de una sombra con la luz de ahora
static func dibujar(lienzo: CanvasItem, centro: Vector2, ancho_sombra: float, fuerza_sombra: float) -> void:
	lienzo.draw_colored_polygon(puntos(centro, ancho_sombra), color(fuerza_sombra))


## Los 14 puntos de la elipse (también los usa trozo_sombra.gd, que junta las de los árboles y rocas en una malla)
static func puntos(centro: Vector2, ancho_sombra: float) -> PackedVector2Array:
	var calidez := Reloj.calidez()
	var estira := 1.0 + calidez * 0.22
	var desp := centro + Vector2((1.0 + calidez * 1.4) if Reloj.luz_dia() > 0.25 else -0.6, 0.0)
	var lista := PackedVector2Array()
	for i in 14:
		var a := TAU * i / 14.0
		lista.append(desp + Vector2(cos(a) * ancho_sombra * estira, sin(a) * ancho_sombra * 0.38))
	return lista


static func color(fuerza_sombra: float) -> Color:
	return Color(0.04, 0.06, 0.03, fuerza_sombra * lerpf(0.65, 1.0, Reloj.luz_dia()))
