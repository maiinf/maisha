extends Node2D
## LA NIEVE HONDA (Sigilia). Fuera del sendero pisado («#» y las puertas) y lejos de un farol rúnico encendido,
## la nieve es blanda y honda: Maisha se hunde, anda más despacio y no puede correr (maisha.hundirse). Por donde
## ya ha pasado deja un SURCO: la nieve queda apretada y, si vuelve a pasar por él, ya no se hunde (los surcos se
## ven en el suelo y duran un buen rato).

const DURA := 90.0                    # segundos que dura un surco antes de que la nieve lo tape
const PISADO := "#^_"

var region: Node2D
var _surcos := {}                     # casilla (Vector2i) -> segundos que le quedan
var _ultima := Vector2i(-99, -99)
var _tiempo := 0.0


func _ready() -> void:
	z_index = -9


func _process(delta: float) -> void:
	_tiempo += delta
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or region == null:
		return
	var casilla := Vector2i((maisha.global_position / 16.0).floor())
	if es_honda(casilla) and not _surcos.has(casilla) and not _junto_a_farol(maisha.global_position):
		maisha.call("hundirse", 0.15)
	# al salir de una casilla de nieve honda, queda un surco
	if casilla != _ultima:
		if es_honda(_ultima):
			_surcos[_ultima] = DURA
		_ultima = casilla
	# los surcos se van tapando
	for c in _surcos.keys():
		_surcos[c] -= delta
		if _surcos[c] <= 0.0:
			_surcos.erase(c)
	queue_redraw()


## Junto a un farol rúnico encendido, la nieve se ablanda (no se hunde)
func _junto_a_farol(punto: Vector2) -> bool:
	for f in get_tree().get_nodes_in_group("faroles_runicos"):
		if f.call("abriga", punto):
			return true
	return false


func es_honda(c: Vector2i) -> bool:
	var filas: PackedStringArray = region._filas
	if c.y < 0 or c.y >= filas.size() or c.x < 0 or c.x >= filas[c.y].length():
		return false
	return not PISADO.contains(filas[c.y][c.x])


func tiene_surco(c: Vector2i) -> bool:
	return _surcos.has(c)


func _draw() -> void:
	# el surco: nieve apretada, más oscura, con el borde de nieve levantada (se aclara al irse tapando)
	for c in _surcos:
		var a: float = clampf(_surcos[c] / 20.0, 0.0, 1.0)
		var o := Vector2(c) * 16.0
		draw_rect(Rect2(o + Vector2(2, 3), Vector2(12, 11)), Color(0.36, 0.32, 0.52, 0.55 * a))
		draw_rect(Rect2(o + Vector2(4, 5), Vector2(8, 7)), Color(0.3, 0.27, 0.46, 0.5 * a))
		draw_rect(Rect2(o + Vector2(2, 2), Vector2(12, 1)), Color(0.96, 0.95, 1.0, 0.7 * a))     # la nieve levantada del borde
		draw_rect(Rect2(o + Vector2(2, 14), Vector2(12, 1)), Color(0.96, 0.95, 1.0, 0.5 * a))
