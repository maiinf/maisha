extends Node2D
## TROZO DE ASTA QUE CAE (Pembe, fase 2): primero una sombra que crece en el suelo (el aviso)
## y luego cae una astilla de hierro que hace daño si Maisha está debajo.

const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const AVISO := 1.0
const RADIO := 11.0

var _t := 0.0
var _caido := false


func _ready() -> void:
	z_index = 1


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()
	if not _caido and _t >= AVISO:
		_caido = true
		Sonido.efecto("piedra_rompe", 0.0, global_position)
		Impacto.temblar(1.5, 0.12)
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 8
		astillas.position = global_position
		get_parent().add_child(astillas)
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		if maisha and maisha.global_position.distance_to(global_position) < RADIO:
			maisha.call("recibir_danio", 1, global_position, "contacto")
	if _t >= AVISO + 0.35:
		queue_free()


func _draw() -> void:
	if not _caido:
		var f := _t / AVISO
		# la sombra crece y se oscurece; un círculo rojizo marca dónde caerá
		for y in range(-3, 4):
			var ancho := int(round(RADIO * f * sqrt(1.0 - (y / 4.0) * (y / 4.0))))
			draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.05, 0.02, 0.08, 0.25 + 0.35 * f))
		draw_arc(Vector2.ZERO, RADIO, 0, TAU, 24, Color(0.9, 0.35, 0.3, 0.35 + 0.4 * f), 1.0)
		# el trozo de hierro cayendo
		var alto := (1.0 - f) * 140.0
		var p := Vector2(0, -alto - 6)
		draw_rect(Rect2(p + Vector2(-1, -6), Vector2(3, 9)), Color("7a8086"))
		draw_rect(Rect2(p + Vector2(-1, -6), Vector2(1, 9)), Color("a3a8ab"))
		draw_rect(Rect2(p + Vector2(0, 2), Vector2(1, 2)), Color("c27ce6"))
	else:
		var f := (_t - AVISO) / 0.35
		draw_rect(Rect2(-1, -8, 3, 9), Color(0.48, 0.5, 0.53, 1.0 - f))
