extends Node2D
## PUENTE DEL REFLEJO («\» en el Lago Espejo): un puente de tablas de luz que solo existe en el reflejo del agua.
## Mientras el lago no está quieto, apenas se adivina (un brillo tenue que tiembla) y no se puede pisar.
## Cuando el lago se vuelve espejo («calma» = 1, lo decide espejo_lago.gd) se hace real: las tablas se encienden
## una a una desde la orilla y se puede cruzar. Si el agua vuelve a temblar, se apaga poco a poco.
## Se dibuja con código (tablas de luz plateada y verde-agua, con destellos), sin imagen.

const R := preload("res://scripts/combate/reglas_combate.gd")
const CLARO := Color(0.86, 0.96, 0.94)
const VERDE_AGUA := Color(0.43, 0.69, 0.69)

var casillas: Array[Vector2i] = []
var calma := 0.0                  # 0 = agua movida, 1 = espejo (la pone espejo_lago.gd)
var real := false
var _encendido := 0.0             # 0..1: cuánto del puente está encendido (de la orilla hacia dentro)
var _tiempo := 0.0
var _cuerpo: StaticBody2D
var _orden: Array[Vector2i] = []  # las casillas, desde la orilla hacia dentro


func _ready() -> void:
	add_to_group("puentes_reflejo")
	z_index = -6
	_ordenar()
	_cuerpo = StaticBody2D.new()
	add_child(_cuerpo)
	for c in casillas:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(R.CASILLA, R.CASILLA)
		forma.shape = caja
		forma.position = Vector2(c) * R.CASILLA + Vector2.ONE * 8
		_cuerpo.add_child(forma)


## Ordena las casillas desde la que toca tierra hacia dentro del lago (así se encienden en orden)
func _ordenar() -> void:
	var region := get_tree().get_first_node_in_group("region")
	var filas: PackedStringArray = region.get("_filas") if region else PackedStringArray()
	var inicio := casillas[0] if not casillas.is_empty() else Vector2i.ZERO
	for c in casillas:
		for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
			var v: Vector2i = c + d
			if v.y >= 0 and v.y < filas.size() and v.x >= 0 and v.x < filas[v.y].length() and filas[v.y][v.x] in ".,#;$":
				inicio = c
	_orden = casillas.duplicate()
	_orden.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		return Vector2(a - inicio).length() < Vector2(b - inicio).length())


func _physics_process(delta: float) -> void:
	_tiempo += delta
	var antes := real
	real = calma >= 1.0 or (real and calma > 0.05)
	_encendido = move_toward(_encendido, 1.0 if real else 0.0, delta * (0.9 if real else 0.6))
	if real != antes:
		_cuerpo.process_mode = Node.PROCESS_MODE_DISABLED if real else Node.PROCESS_MODE_INHERIT
		if real:
			Sonido.efecto("cristal", 0.0, global_position + Vector2(_orden[0]) * R.CASILLA)
	queue_redraw()


## ¿Está esta posición encima del puente? (para no apagarlo con Maisha encima)
func pisa(p: Vector2) -> bool:
	var c := Vector2i((p / R.CASILLA).floor())
	return c in casillas


func cruzable() -> bool:
	return real and _encendido > 0.5


func _draw() -> void:
	var n := _orden.size()
	for i in n:
		var c: Vector2i = _orden[i]
		var esquina := Vector2(c) * R.CASILLA
		# cuánto se ve esta tabla: un fantasma tenue con el agua movida; encendida, de la orilla hacia dentro
		var encendida := clampf(_encendido * (n + 3) - i, 0.0, 1.0)
		var fantasma := 0.08 + 0.25 * calma
		var a := maxf(fantasma, encendida)
		var tiembla := (1.0 - encendida) * sin(_tiempo * 6.0 + i) * 1.2
		for k in 4:
			var y := esquina.y + 1 + k * 4 + tiembla
			var x0 := esquina.x + (1 if (c.x + k) % 2 == 0 else 2)
			draw_rect(Rect2(Vector2(x0, y + 2), Vector2(14, 1)), Color(0.05, 0.15, 0.16, a * 0.5))
			draw_rect(Rect2(Vector2(x0, y), Vector2(14, 2)), Color(CLARO, a * 0.85))
			draw_rect(Rect2(Vector2(x0, y), Vector2(14, 1)), Color(1, 1, 1, a * 0.6))
		# los bordes del puente, verde-agua, y un destello que recorre las tablas
		draw_rect(Rect2(esquina, Vector2(1, 16)), Color(VERDE_AGUA, a * 0.8))
		draw_rect(Rect2(esquina + Vector2(15, 0), Vector2(1, 16)), Color(VERDE_AGUA, a * 0.8))
		var f := fmod(_tiempo * 0.7 + i * 0.13, 1.0)
		if encendida > 0.9 and f < 0.15:
			draw_rect(Rect2(esquina + Vector2(4 + f * 50, 7), Vector2(2, 2)), Color(1, 1, 1, 0.9))
