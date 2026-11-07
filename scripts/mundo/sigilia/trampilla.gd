extends StaticBody2D
## UNA TRAMPILLA DE HIERRO arriba de una escalerilla (Canal de Tinta: la del andén de la Esclusa Hundida al muelle sur).
## Tapa el paso (2 casillas de ancho, desde la de la izquierda). El pestillo está por DEBAJO: solo se abre desde abajo
## (Acción); desde arriba, Maisha ve que está echado. Abierta se queda abierta (marca `marca`).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const HIERRO := [Color("16141c"), Color("2b2a34"), Color("44434f"), Color("6a6978")]

@export var marca := ""
var radio_interaccion := 26.0
var _forma: CollisionShape2D
var _abierta := false


func _ready() -> void:
	add_to_group("interactuables")
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(32, 16)
	_forma.shape = caja
	_forma.position = Vector2(16, 8)
	add_child(_forma)
	if Estado.tiene(marca):
		_abrir(false)


func punto_interaccion() -> Vector2:
	return global_position + Vector2(16, 8)


func interactuar() -> void:
	if _abierta:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.y > global_position.y + 8.0:
		_abrir(true)
	else:
		await CHARLA.hablar(self, "canal_trampilla_arriba")


func _abrir(con_sonido: bool) -> void:
	_abierta = true
	Estado.marcar(marca)
	_forma.set_deferred("disabled", true)
	remove_from_group("interactuables")
	if con_sonido:
		Sonido.efecto("puerta", -2.0, global_position)
	queue_redraw()


func _draw() -> void:
	if _abierta:
		# abatida contra la pared de la izquierda: solo se ve el canto
		draw_rect(Rect2(-3, -10, 3, 26), HIERRO[1])
		draw_rect(Rect2(-3, -10, 1, 26), HIERRO[3])
		return
	draw_rect(Rect2(0, 2, 32, 14), HIERRO[0])
	draw_rect(Rect2(1, 1, 30, 13), HIERRO[2])
	for x in range(4, 30, 5):                                 # la reja
		draw_rect(Rect2(x, 2, 2, 11), HIERRO[1])
		draw_rect(Rect2(x, 2, 1, 11), HIERRO[3])
	draw_rect(Rect2(1, 7, 30, 2), HIERRO[1])
	draw_rect(Rect2(14, 12, 4, 3), Color("8a6224"))           # el pestillo, por debajo
	draw_rect(Rect2(15, 12, 2, 1), Color("c89a3e"))
