extends Node2D
## PANTALLA DE COMPROBACIÓN DEL PROYECTO BASE
## Si al pulsar F5 ves la paleta de Raíz y este texto, todo está bien instalado.
## Se sustituirá por el juego de verdad a partir de la Fase 3.

var _paleta: Array[Color] = []
var _tiempo := 0.0


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("140e18"))
	_paleta = _leer_paleta("res://arte/paletas/raiz.gpl")


## Lee un archivo de paleta .gpl (el mismo que usas en Pixelorama).
func _leer_paleta(ruta: String) -> Array[Color]:
	var colores: Array[Color] = []
	var f := FileAccess.open(ruta, FileAccess.READ)
	if f == null:
		return colores
	while not f.eof_reached():
		var linea := f.get_line().strip_edges()
		var partes := linea.split_floats(" ", false)
		if partes.size() >= 3 and linea[0].is_valid_int():
			colores.append(Color8(int(partes[0]), int(partes[1]), int(partes[2])))
	return colores


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()


func _draw() -> void:
	var fuente := ThemeDB.fallback_font
	draw_string(fuente, Vector2(24, 40), "MAISHA  -  proyecto base", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("d6b46e"))
	draw_string(fuente, Vector2(24, 60), "Si ves la paleta de Raiz, Godot esta bien instalado.", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("fff8e8"))
	draw_string(fuente, Vector2(24, 72), "Resolucion base 640x360 - pixeles nitidos (sin difuminar).", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("c9b07e"))
	# Muestrario de la paleta: 4 colores por material
	for i in _paleta.size():
		var columna := i % 16
		var fila: int = i / 16
		var r := Rect2(Vector2(24 + columna * 18, 100 + fila * 18), Vector2(16, 16))
		draw_rect(r, _paleta[i])
	draw_string(fuente, Vector2(24, 100 + 4 * 18 + 16), "%d colores cargados desde arte/paletas/raiz.gpl" % _paleta.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("fff8e8"))
	# Un latido, para comprobar que el juego se actualiza
	var pulso: float = 1.0 + 0.15 * sin(_tiempo * 6.0) * max(0.0, sin(_tiempo * 2.0))
	draw_circle(Vector2(560, 180), 18.0 * pulso, Color("e8b860"))
	draw_circle(Vector2(560, 180), 12.0 * pulso, Color("fff3c4"))
