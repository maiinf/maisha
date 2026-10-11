extends CanvasLayer
## MENÚ DE PAUSA (Esc o Start): el juego se para y se puede
##   seguir, cambiar a pantalla completa, volver a la pantalla de inicio o salir.
## La partida se guarda sola al volver al inicio o al salir.
## También muestra dónde está Maisha, el tiempo jugado, lo que lleva y sus mejoras.

const LISTA := preload("res://scripts/interfaz/menu_lista.gd")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const ICONOS := {
	"seta_luminosa": preload("res://arte/mundos/raiz/objetos/seta_luminosa.png"),
	"mineral": preload("res://arte/mundos/raiz/objetos/mineral.png"),
}
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
const CAJA_MENU := Rect2(28, 40, 262, 232)
const CAJA_INFO := Rect2(300, 40, 312, 232)
const PIEL := preload("res://scripts/interfaz/piel.gd")

var abierto := false
var _lista: Control
var _lienzo: Control
var _fuente: FontFile
var _acciones: Array[String] = []


func _ready() -> void:
	add_to_group("pausa")
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	_lista = LISTA.new()
	_lista.position = CAJA_MENU.position + Vector2(14, 40)
	_lista.size = Vector2(CAJA_MENU.size.x - 20, 184)
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


func _montar() -> void:
	var completa := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
	_lista.opciones = [
		{"texto": "Seguir"},
		{"texto": "Pantalla completa: %s" % ("sí" if completa else "no")},
		{"texto": "Música  " + _barra(Sonido.niveles["Musica"])},
		{"texto": "Sonidos  " + _barra(Sonido.niveles["Efectos"])},
		{"texto": "Temblores de pantalla: %s" % ("sí" if Impacto.temblores else "no")},
		{"texto": "Objetivo en pantalla: %s" % ("sí" if Misiones.ver_objetivo else "no")},
		{"texto": "Volver al inicio"},
		{"texto": "Salir del juego"},
	]
	_acciones = ["seguir", "pantalla", "musica", "efectos", "temblores", "objetivo", "inicio", "salir"]


## Nivel de volumen con puntitos: ‹•••••••···› (de 0 a 10; con izquierda y derecha se cambia)
func _barra(nivel: int) -> String:
	return "‹" + "•".repeat(nivel) + "·".repeat(10 - nivel) + "›"


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


func _dibujar() -> void:
	# oscurece el juego detrás
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, 0.55))
	_caja(CAJA_MENU)
	_texto("Pausa", CAJA_MENU.position + Vector2(16, 24), AMBAR)
	_caja(CAJA_INFO)
	var p := CAJA_INFO.position + Vector2(16, 24)
	_texto(Estado.lugar if Estado.lugar != "" else "Raíz", p, AMBAR)
	_texto("Tiempo de juego: %s" % Estado.texto_tiempo(Estado.tiempo_jugado), p + Vector2(0, 20), APAGADO)
	# lo que lleva Maisha
	p.y += 50
	_texto("Lleva", p, TEXTO)
	p.y += 8
	var algo := false
	for o in Estado.OBJETOS:
		var n := Estado.cuantos(o)
		if n <= 0:
			continue
		algo = true
		var icono: Texture2D = ICONOS.get(o)
		if icono:
			_lienzo.draw_texture_rect_region(icono, Rect2(p + Vector2(0, 4), Vector2(icono.get_width() / 2, icono.get_height())),
				Rect2(0, 0, icono.get_width() / 2, icono.get_height()))
		_texto("%s  x%d" % [Estado.OBJETOS[o]["uno"], n], p + Vector2(18, 16), APAGADO)
		p.y += 20
	if not algo:
		_texto("Nada, por ahora", p + Vector2(0, 16), Color(APAGADO, 0.6))
		p.y += 20
	# mejoras
	p.y += 18
	_texto("Mejoras", p, TEXTO)
	var hay_mejoras := false
	for m in MEJORAS:
		if Estado.tiene(m):
			hay_mejoras = true
			p.y += 20
			_texto("· " + String(MEJORAS[m]), p, APAGADO)
	if not hay_mejoras:
		_texto("Ninguna, por ahora", p + Vector2(0, 20), Color(APAGADO, 0.6))
