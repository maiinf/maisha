extends Node2D
## EL PUENTE DE CRISTAL (las Dunas de Penumbra): el rayo de los espejos funde la arena movediza en cristal (las
## casillas de `casillas`). Desde que está su `marca`, sostiene (grupo «sostenes» → `firme()`) y se dibuja: losas de
## cristal ámbar con su brillo. Antes, nada.

var casillas := Rect2i()
var marca := ""
var _brillo := 0.0


func _ready() -> void:
	add_to_group("sostenes")
	z_index = -4


func hecho() -> bool:
	return Estado.tiene(marca)


func fundir() -> void:
	Estado.marcar(marca)
	_brillo = 1.0
	queue_redraw()


func firme(p: Vector2) -> bool:
	return hecho() and casillas.has_point(Vector2i(floori(p.x / 16.0), floori(p.y / 16.0)))


func _process(delta: float) -> void:
	if _brillo > 0.0:
		_brillo = maxf(0.0, _brillo - delta * 0.6)
		queue_redraw()


func _draw() -> void:
	if not hecho():
		return
	for y in range(casillas.position.y, casillas.end.y):
		for x in range(casillas.position.x, casillas.end.x):
			var r := Rect2(Vector2(x, y) * 16.0, Vector2(16, 16))
			draw_rect(r, Color(0.98, 0.72, 0.4, 0.82))
			draw_rect(r.grow(-2.0), Color(1.0, 0.86, 0.6, 0.5))
			draw_line(r.position + Vector2(3, 3), r.position + Vector2(9, 3), Color(1, 1, 0.9, 0.8), 1.0)
			draw_rect(r, Color(0.55, 0.3, 0.2, 0.7), false, 1.0)
	if _brillo > 0.0:
		var todo := Rect2(Vector2(casillas.position) * 16.0, Vector2(casillas.size) * 16.0)
		draw_rect(todo.grow(6.0 * _brillo), Color(1.0, 0.95, 0.7, 0.5 * _brillo))
