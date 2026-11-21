extends Node2D
## UNA PASARELA DEL ESTANQUE DE LOS REFLEJOS (el Jardín de los Faroles), sobre el agua (casillas `casillas`). Hay
## dos gemelas: la de verdad sostiene (grupo «sostenes» → `firme()`); la otra (`falsa`) es un reflejo y quien la pisa
## se hunde. Se ven iguales hasta que la cruza la luz violeta (ocaso/luz_jardin.gd): entonces la falsa se delata
## (`marca`) y desde ahí se ve como lo que es, un temblor de luz.

var casillas := Rect2i()
var falsa := false
var marca := ""
var _t := 0.0


func _ready() -> void:
	add_to_group("sostenes")
	z_index = -4
	var luz := get_tree().get_first_node_in_group("luz_jardin")
	if luz and falsa:
		luz.cambiada.connect(func() -> void: _mirar(luz))


func delatada() -> bool:
	return Estado.tiene(marca)


func _mirar(luz: Node) -> void:
	if delatada():
		return
	for y in range(casillas.position.y, casillas.end.y):
		for x in range(casillas.position.x, casillas.end.x):
			if luz.tiene(Vector2i(x, y), 2):
				Estado.marcar(marca)
				Sonido.efecto("reflejo_delata", 0.0, Vector2(x, y) * 16.0)
				return


func firme(p: Vector2) -> bool:
	return not falsa and casillas.has_point(Vector2i(floori(p.x / 16.0), floori(p.y / 16.0)))


func _process(delta: float) -> void:
	_t += delta
	if falsa and delatada():
		queue_redraw()


func _draw() -> void:
	var fantasma := falsa and delatada()
	for y in range(casillas.position.y, casillas.end.y):
		for x in range(casillas.position.x, casillas.end.x):
			var r := Rect2(Vector2(x, y) * 16.0, Vector2(16, 16))
			if fantasma:
				var a := 0.18 + sin(_t * 3.0 + x * 0.7) * 0.08
				draw_rect(r.grow(-1.0), Color(0.78, 0.55, 1.0, a))
				draw_line(r.position + Vector2(2, 8), r.position + Vector2(14, 8), Color(1, 0.9, 1, a + 0.15), 1.0)
				continue
			# las tablas, a lo ancho del paso, con su junta y los clavos
			for k in 4:
				var tabla := Rect2(r.position + Vector2(k * 4, 0), Vector2(4, 16))
				draw_rect(tabla, Color(0.48, 0.3, 0.2) if (x + k) % 3 else Color(0.42, 0.26, 0.18))
				draw_line(tabla.position, tabla.position + Vector2(0, 16), Color(0.2, 0.1, 0.08), 1.0)
			draw_rect(Rect2(r.position + Vector2(0, 2), Vector2(16, 1)), Color(0.72, 0.5, 0.32))
	# el borde que da al agua
	var todo := Rect2(Vector2(casillas.position) * 16.0, Vector2(casillas.size) * 16.0)
	if not fantasma:
		draw_rect(Rect2(todo.position + Vector2(0, todo.size.y), Vector2(todo.size.x, 2)), Color(0.12, 0.05, 0.1, 0.8))
