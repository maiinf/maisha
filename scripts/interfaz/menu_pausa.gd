extends CanvasLayer
## MENÚ DE PAUSA (Esc o Start): el juego se para y se puede
##   seguir, cambiar a pantalla completa, volver a la pantalla de inicio o salir.
## La partida se guarda sola al volver al inicio o al salir.
## También muestra dónde está Maisha, el tiempo jugado, lo que lleva y sus mejoras.

const LISTA := preload("res://scripts/interfaz/menu_lista.gd")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const OBJETOS_TEX := preload("res://arte/interfaz/objetos.png")
## Mejoras que se muestran si se tiene su marca: marca -> texto
const MEJORAS := {
	"cetro_templado": "Cetro templado: el golpe llega más lejos",
	"vigia": "Torre del vigía: los secretos brillan",
}
const PANEL := Color(0.08, 0.07, 0.10, 0.92)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const CAJA_MENU := Rect2(24, 34, 278, 252)
const CAJA_INFO := Rect2(312, 34, 304, 252)
const PIEL := preload("res://scripts/interfaz/piel.gd")

var abierto := false
var _lista: Control
var _lienzo: Control
var _fuente: FontFile
var _acciones: Array[String] = []


func _ready() -> void:
	add_to_group("pausa")
	add_to_group("modales")
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	_fuente.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	_lista = LISTA.new()
	_lista.position = CAJA_MENU.position + Vector2(12, 42)
	_lista.size = Vector2(CAJA_MENU.size.x - 20, 200)
	_lista.en_papel = true
	_lista.elegida.connect(_al_elegir)
	_lista.ajustada.connect(_al_ajustar)
	add_child(_lista)
	visible = false


func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("menu"):
		if abierto:
			cerrar()
		elif _se_puede_abrir():
			abrir()
	if abierto:
		_lienzo.queue_redraw()


func _se_puede_abrir() -> bool:
	if Estado.cambiando or get_tree().paused:
		return false
	if get_tree().get_meta("menu_cerrado_en", -1) == Engine.get_process_frames():
		return false             # esa misma pulsación acaba de cerrar la mochila
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	return not (dialogo and dialogo.hablando)


func abrir() -> void:
	Sonido.efecto("pausa")
	abierto = true
	visible = true
	get_tree().paused = true
	_montar()
	_lista.seleccion = 0
	_lista.reiniciar()


func cerrar() -> void:
	abierto = false
	visible = false
	get_tree().paused = false


func esta_abierta() -> bool:
	return abierto


func _montar() -> void:
	var completa := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
	_lista.opciones = [
		{"texto": "Seguir"},
		{"texto": "Pantalla completa", "interruptor": completa},
		{"texto": "Música", "valor": float(Sonido.niveles["Musica"]) / 10.0},
		{"texto": "Sonidos", "valor": float(Sonido.niveles["Efectos"]) / 10.0},
		{"texto": "Temblores de pantalla", "interruptor": Impacto.temblores},
		{"texto": "Objetivo en pantalla", "interruptor": Misiones.ver_objetivo},
		{"texto": "Volver al inicio"},
		{"texto": "Salir del juego"},
	]
	_acciones = ["seguir", "pantalla", "musica", "efectos", "temblores", "objetivo", "inicio", "salir"]


## Izquierda y derecha cambian el volumen; Acción lo sube (y del máximo vuelve a cero)
func _al_ajustar(i: int, direccion: int) -> void:
	if _acciones[i] in ["musica", "efectos"]:
		_cambiar_nivel(_acciones[i], direccion)


func _cambiar_nivel(cual: String, direccion: int) -> void:
	var buses: Array = ["Musica"] if cual == "musica" else ["Efectos", "Ambiente"]
	var nivel: int = Sonido.niveles[buses[0]] + direccion
	if direccion > 0 and nivel > 10:
		nivel = 0
	for bus in buses:
		Sonido.poner_nivel(bus, clampi(nivel, 0, 10))
	Sonido.efecto("menu_mover")
	_montar()


func _al_elegir(i: int) -> void:
	match _acciones[i]:
		"seguir":
			cerrar()
		"musica", "efectos":
			_cambiar_nivel(_acciones[i], 1)
		"temblores":
			Impacto.poner_temblores(not Impacto.temblores)
			Sonido.efecto("menu_mover")
			_montar()
		"objetivo":
			Misiones.poner_ver_objetivo(not Misiones.ver_objetivo)
			Sonido.efecto("menu_mover")
			_montar()
		"pantalla":
			var completa := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if completa else DisplayServer.WINDOW_MODE_FULLSCREEN)
			_montar()
		"inicio":
			Estado.guardar()
			cerrar()
			Estado.jugando = false
			Estado.ir_a("inicio", "")
		"salir":
			Estado.guardar()
			await Sonido.callar()
			get_tree().quit()


## En el pergamino se escribe con tinta (los colores de siempre se cambian por su tinta)
func _texto(texto: String, pos: Vector2, color: Color) -> void:
	var tinta: Color = {TEXTO: PIEL.TINTA, APAGADO: PIEL.TINTA_SUAVE, AMBAR: PIEL.ROJO}.get(Color(color, 1.0), PIEL.TINTA)
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(tinta, color.a))


func _caja(r: Rect2) -> void:
	PIEL.caja(_lienzo, r, "pergamino")
	PIEL.esquinas_oro(_lienzo, r, PIEL.TINTA_SUAVE, 0.55, 5.0)


func _dibujar() -> void:
	# oscurece el juego detrás
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, 0.62))
	_caja(CAJA_MENU)
	_texto("Pausa", CAJA_MENU.position + Vector2(16, 23), AMBAR)
	PIEL.divisor(_lienzo, CAJA_MENU.position.x + 12, CAJA_MENU.end.x - 12, CAJA_MENU.position.y + 32, PIEL.TINTA_SUAVE, 0.55)
	_caja(CAJA_INFO)
	var p := CAJA_INFO.position + Vector2(16, 23)
	_texto(Estado.lugar if Estado.lugar != "" else "Raíz", p, AMBAR)
	var t_txt := Estado.texto_tiempo(Estado.tiempo_jugado)
	var w_t := _fuente.get_string_size(t_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 12.0
	PIEL.insignia(_lienzo, Vector2(CAJA_INFO.end.x - 14.0 - w_t, CAJA_INFO.position.y + 10), t_txt, _fuente, PIEL.CUERO_OSCURO, PIEL.ORO, PIEL.CREMA, 0.92)
	PIEL.divisor(_lienzo, CAJA_INFO.position.x + 12, CAJA_INFO.end.x - 12, CAJA_INFO.position.y + 32, PIEL.TINTA_SUAVE, 0.55)
	# lo que lleva Maisha (en dos columnas para que no se salga de la caja aunque lleve muchos objetos)
	p.y += 28
	_texto("Lleva", p, TEXTO)
	p.y += 6
	var llevados: Array[String] = []
	for o in Estado.OBJETOS:
		if Estado.cuantos(o) > 0:
			llevados.append(o)
	if llevados.is_empty():
		_texto("Nada, por ahora", p + Vector2(0, 16), Color(APAGADO, 0.65))
		p.y += 22
	else:
		var dos_col := llevados.size() > 3
		for idx in llevados.size():
			var o := llevados[idx]
			var n := Estado.cuantos(o)
			var col := (idx % 2) if dos_col else 0
			var fila := (idx / 2) if dos_col else idx
			var pos_o := p + Vector2(col * 138, fila * 20)
			var idx_icono: int = int(Estado.OBJETOS[o].get("icono", -1))
			if idx_icono >= 0:
				_lienzo.draw_texture_rect_region(OBJETOS_TEX, Rect2(pos_o + Vector2(0, 2), Vector2(16, 16)),
					Rect2(idx_icono * 16, 0, 16, 16))
			_texto("%s x%d" % [Estado.OBJETOS[o]["uno"], n], pos_o + Vector2(19, 15), APAGADO)
		var filas_usadas := ((llevados.size() + 1) / 2) if dos_col else llevados.size()
		p.y += filas_usadas * 20
	# mejoras
	p.y = minf(p.y + 16, CAJA_INFO.end.y - 68)
	PIEL.divisor(_lienzo, CAJA_INFO.position.x + 12, CAJA_INFO.end.x - 12, p.y - 12, PIEL.TINTA_SUAVE, 0.45)
	_texto("Mejoras", p, TEXTO)
	var hay_mejoras := false
	for m in MEJORAS:
		if Estado.tiene(m):
			hay_mejoras = true
			p.y += 18
			var dc := p + Vector2(4, -4)
			_lienzo.draw_colored_polygon(PackedVector2Array([dc + Vector2(0, -3), dc + Vector2(3, 0), dc + Vector2(0, 3), dc + Vector2(-3, 0)]), PIEL.VERDE)
			_texto(String(MEJORAS[m]), p + Vector2(10, 0), APAGADO)
	if not hay_mejoras:
		_texto("Ninguna, por ahora", p + Vector2(0, 18), Color(APAGADO, 0.65))
	PIEL.barra_teclas(_lienzo, 320.0, 314.0, [["↑↓", "Elegir"], ["←→", "Ajustar"], ["Espacio", "Aceptar"], ["Esc", "Volver"]], _fuente, 16, 0.96, true)
