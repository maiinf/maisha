extends Node2D
## BROTES que dejan las explosiones. Maisha los atraviesa; los enemigos no pueden entrar.
## Se dibujan todos desde aquí, a ras de suelo.

const R := preload("res://scripts/combate/reglas_combate.gd")
const TEXTURA := preload("res://arte/efectos/brote.png")

var _brotes: Dictionary = {}   # casilla (Vector2i) -> segundos que le quedan
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("registro_brotes")


func plantar(casilla: Vector2i) -> void:
	_brotes[casilla] = R.BROTES_DURAN
	queue_redraw()


func hay_brote(casilla: Vector2i) -> bool:
	return _brotes.has(casilla)


func limpiar() -> void:
	_brotes.clear()
	queue_redraw()


func _process(delta: float) -> void:
	_tiempo += delta
	if _brotes.is_empty():
		return
	for c in _brotes.keys():
		_brotes[c] -= delta
		if _brotes[c] <= 0.0:
			_brotes.erase(c)
	queue_redraw()


func _draw() -> void:
	var fotograma := int(_tiempo * 2.0) % 2
	for c in _brotes:
		var restante: float = _brotes[c]
		var origen := Vector2(c) * R.CASILLA
		# crecen al aparecer y se marchitan (parpadean) en el último segundo
		if restante < 1.0 and int(restante * 8.0) % 2 == 0:
			continue
		var alto := 16
		if R.BROTES_DURAN - restante < 0.15:
			alto = 8
		draw_texture_rect_region(TEXTURA, Rect2(origen + Vector2(0, 16 - alto), Vector2(16, alto)),
			Rect2(fotograma * 16, 16 - alto, 16, alto))
