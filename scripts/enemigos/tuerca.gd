extends Node2D
## TUERCA que lanza la Cosechadora: vuela en arco (con su sombra en el suelo marcando dónde caerá),
## hace daño si Maisha está debajo y deja un BLOQUE DE CHATARRA en esa casilla.
## Con el techo de la Cosechadora roto (de_fuego), cae como una bola de fuego que prende tres casillas.

const R := preload("res://scripts/combate/reglas_combate.gd")
const TEXTURA := preload("res://arte/mundos/raiz/campo/tuerca.png")
const CHATARRA := preload("res://scripts/enemigos/chatarra.gd")
const DURA := 1.1
const RADIO := 9.0

var desde := Vector2.ZERO
var hasta := Vector2.ZERO
var de_fuego := false
var _t := 0.0


func _ready() -> void:
	add_to_group("tuercas")
	hasta = R.centro_de(R.casilla_de(hasta)) + Vector2(0, 6)
	global_position = hasta
	z_index = 2


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()
	if _t >= DURA:
		Sonido.efecto("cosechadora_tuerca", 0.0, global_position)
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		var debajo := maisha != null and maisha.global_position.distance_to(global_position) < RADIO + 4.0
		if de_fuego:
			var fuego := get_tree().get_first_node_in_group("fuego_giza")
			var c := R.casilla_de(global_position)
			if fuego:
				for dx in [-1, 0, 1]:
					fuego.call("encender", c + Vector2i(dx, 0), 4.0)
			Sonido.efecto("cosechadora_fuego", -4.0, global_position)
		elif debajo:
			maisha.call("recibir_danio", 1, global_position, "contacto")
		else:
			var bloque: StaticBody2D = CHATARRA.new()
			bloque.position = global_position
			get_parent().add_child(bloque)
		queue_free()


func _draw() -> void:
	var f := clampf(_t / DURA, 0.0, 1.0)
	for y in range(-2, 3):
		var ancho := int(round(RADIO * f * sqrt(1.0 - (y / 3.0) * (y / 3.0))))
		draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.05, 0.04, 0.05, 0.2 + 0.4 * f))
	draw_arc(Vector2.ZERO, RADIO, 0, TAU, 18, Color(0.85, 0.3, 0.3, 0.25 + 0.45 * f), 1.0)
	var p := (desde - hasta).lerp(Vector2.ZERO, f) + Vector2(0, -sin(f * PI) * 70.0)
	var giro := int(_t * 12.0) % 2
	if de_fuego:
		draw_circle(p, 6.0, Color(0.94, 0.54, 0.15, 0.35))
		draw_circle(p, 4.0, Color("ef8a26"))
		draw_circle(p + Vector2(-1, -1), 2.0, Color("fde27e"))
		draw_rect(Rect2((p + Vector2(0, 4)).round(), Vector2(1, 1)), Color("a855d6"))
		return
	draw_texture_rect_region(TEXTURA, Rect2(p.round() - Vector2(4, 4), Vector2(8, 8)), Rect2(giro * 8, 0, 8, 8))
