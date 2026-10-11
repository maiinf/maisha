extends Node2D
## Efecto del LATIDO: un anillo de luz ámbar (el color del corazón) que se expande.

const R := preload("res://scripts/combate/reglas_combate.gd")
const DURACION := 0.3
const CLARO := Color("e6a852")
const BRILLO := Color("fff8e8")

var _tiempo := 0.0


func _process(delta: float) -> void:
	_tiempo += delta
	if _tiempo >= DURACION:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var t := _tiempo / DURACION
	var radio := lerpf(4.0, Artes.latido_radio(), t)
	var puntos := int(radio * 1.6)
	for i in puntos:
		var a := TAU * i / puntos
		var p := (Vector2(cos(a), sin(a) * 0.7) * radio).round()
		draw_rect(Rect2(p, Vector2.ONE), BRILLO if t < 0.3 else CLARO)
