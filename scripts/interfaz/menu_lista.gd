extends Control
## LISTA DE OPCIONES para los menús (pantalla de inicio, pausa, preguntas de sí o no).
## Se maneja con arriba/abajo y Acción (o Intro), con el mando, o con el ratón.
## La opción elegida lleva la hojita delante y brilla.
##   lista.opciones = [{"texto": "Continuar", "nota": "Prados del Eco · 12 min"}, {"texto": "Salir"}]
##   lista.elegida.connect(func(i): ...)

signal elegida(indice: int)
signal ajustada(indice: int, direccion: int)      # izquierda/derecha sobre una opción (p. ej. el volumen)

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const CURSOR := preload("res://arte/interfaz/cursor_hoja.png")
const TEXTO := Color("fff3c4")          # Maisha 4
const APAGADO := Color("c9b07e")        # Pergamino 2
const NOTA := Color("e6a852")           # Flor ámbar 3
const SOMBRA := Color(0.08, 0.05, 0.1, 0.8)
const ALTO_LINEA := 22
const ALTO_NOTA := 13

var opciones: Array = []:
	set(valor):
		opciones = valor
		seleccion = clampi(seleccion, 0, maxi(0, opciones.size() - 1))
		queue_redraw()
var seleccion := 0
## Sobre el pergamino del diario: tinta en vez de letras claras, y lo elegido subrayado
var en_papel := false
const PIEL := preload("res://scripts/interfaz/piel.gd")
var activa := true
var _fuente: FontFile
var _tiempo := 0.0
var _abierta_en := -1


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	mouse_filter = Control.MOUSE_FILTER_STOP
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	_fuente.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	_abierta_en = Engine.get_process_frames()


## Para que la misma pulsación que abre un menú no elija ya una opción
func reiniciar() -> void:
	_abierta_en = Engine.get_process_frames()


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()
	if not activa or not is_visible_in_tree() or opciones.is_empty() or Engine.get_process_frames() == _abierta_en:
		return
	if Input.is_action_just_pressed("mover_abajo") or Input.is_action_just_pressed("ui_down"):
		seleccion = (seleccion + 1) % opciones.size()
		Sonido.efecto("menu_mover")
	elif Input.is_action_just_pressed("mover_arriba") or Input.is_action_just_pressed("ui_up"):
		seleccion = (seleccion - 1 + opciones.size()) % opciones.size()
		Sonido.efecto("menu_mover")
	elif Input.is_action_just_pressed("mover_izquierda") or Input.is_action_just_pressed("ui_left"):
		ajustada.emit(seleccion, -1)
	elif Input.is_action_just_pressed("mover_derecha") or Input.is_action_just_pressed("ui_right"):
		ajustada.emit(seleccion, 1)
	elif Input.is_action_just_pressed("accion") or Input.is_action_just_pressed("ui_accept"):
		Sonido.efecto("menu_aceptar")
		elegida.emit(seleccion)


func _y_de(i: int) -> float:
	var y := 0.0
	for k in i:
		y += ALTO_LINEA + (ALTO_NOTA if String(opciones[k].get("nota", "")) != "" else 0)
	return y


func alto_total() -> float:
	return _y_de(opciones.size())


func _gui_input(evento: InputEvent) -> void:
	if not activa:
		return
	if evento is InputEventMouseMotion or evento is InputEventMouseButton:
		var y: float = evento.position.y
		for i in opciones.size():
			if y >= _y_de(i) and y < _y_de(i + 1):
				if seleccion != i:
					Sonido.efecto("menu_mover")
				seleccion = i
				if evento is InputEventMouseButton and evento.pressed and evento.button_index == MOUSE_BUTTON_LEFT:
					elegida.emit(i)
				break


func _draw() -> void:
	for i in opciones.size():
		var y := _y_de(i)
		var texto := String(opciones[i]["texto"])
		var elegida_ahora := i == seleccion and activa
		var x := 14.0 if elegida_ahora else 10.0
		var color := TEXTO if elegida_ahora else APAGADO
		if opciones[i].get("apagada", false):
			color = Color(APAGADO, 0.45)
		if en_papel:
			color = PIEL.TINTA if elegida_ahora else PIEL.TINTA_SUAVE
			if opciones[i].get("apagada", false):
				color = PIEL.TINTA_APAGADA
			if elegida_ahora:
				PIEL.subrayar(self, Rect2(x - 4, y + 1, _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 10, 19), _tiempo)
		else:
			draw_string(_fuente, Vector2(x + 1, y + 16), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, SOMBRA)
		draw_string(_fuente, Vector2(x, y + 15), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, color)
		if elegida_ahora:
			var vaiven := roundf(sin(_tiempo * 5.0))
			draw_texture(CURSOR, Vector2(vaiven, y + 6))
		var nota := String(opciones[i].get("nota", ""))
		if nota != "":
			if not en_papel:
				draw_string(_fuente, Vector2(x + 1, y + 29), nota, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, SOMBRA)
			draw_string(_fuente, Vector2(x, y + 28), nota, HORIZONTAL_ALIGNMENT_LEFT, -1, 16,
				Color(PIEL.ROJO if en_papel else NOTA, 0.9 if elegida_ahora else 0.6))
