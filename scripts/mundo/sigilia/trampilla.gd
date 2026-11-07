extends StaticBody2D
## UNA TRAMPILLA (o VERJA) DE HIERRO que solo se abre por un lado (Canal de Tinta: la del andén de la Esclusa Hundida
## al muelle sur, y la verja de la Gran Dársena al muelle norte). Tapa un paso de 2 casillas (desde la de arriba a la
## izquierda). El pestillo está del lado `desde` (abajo, o a la derecha): solo se abre desde allí (Acción); desde el
## otro lado, Maisha ve que está echado (conversación `charla_cerrada`). Abierta se queda abierta (marca `marca`).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const HIERRO := [Color("16141c"), Color("2b2a34"), Color("44434f"), Color("6a6978")]

@export var marca := ""
@export var desde := Vector2.DOWN          # (DOWN: una trampilla tumbada; RIGHT: una verja de pie)
@export var charla_cerrada := "canal_trampilla_arriba"
var radio_interaccion := 26.0
var _forma: CollisionShape2D
var _abierta := false


func _ready() -> void:
	add_to_group("interactuables")
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(32, 16) if _tumbada() else Vector2(16, 32)
	_forma.shape = caja
	_forma.position = Vector2(16, 8) if _tumbada() else Vector2(8, 16)
	add_child(_forma)
	if Estado.tiene(marca):
		_abrir(false)


func _tumbada() -> bool:
	return desde.y != 0.0


func punto_interaccion() -> Vector2:
	return global_position + (Vector2(16, 8) if _tumbada() else Vector2(8, 16))


func interactuar() -> void:
	if _abierta:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and (maisha.global_position - punto_interaccion()).dot(desde) > 0.0:
		_abrir(true)
	else:
		await CHARLA.hablar(self, charla_cerrada)


func _abrir(con_sonido: bool) -> void:
	_abierta = true
	Estado.marcar(marca)
	_forma.set_deferred("disabled", true)
	remove_from_group("interactuables")
	if con_sonido:
		Sonido.efecto("puerta", -2.0, global_position)
	queue_redraw()


func _draw() -> void:
	if not _tumbada():
		# (la verja: el mismo dibujo, de pie)
		draw_set_transform(Vector2(16, 0), PI / 2.0)
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
