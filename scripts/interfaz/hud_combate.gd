extends CanvasLayer
## HUD CONTEXTUAL: al explorar no se ve nada; Vida y Aliento aparecen al acercarse a una zona
## corrupta, al recibir daño o al gastar Aliento, y se ocultan solos cuando ya no hacen falta.
## También muestra los mensajes breves y el fundido a negro al caer.

const R := preload("res://scripts/combate/reglas_combate.gd")
const HOJAS := preload("res://arte/interfaz/hoja_vida.png")
const OBJETOS := preload("res://arte/interfaz/objetos.png")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PIEL := preload("res://scripts/interfaz/piel.gd")
const PANEL := Color(0.08, 0.07, 0.10, 0.72)
const FILO := Color("d6b46e")            # Interfaz 2
const ALIENTO := Color("9aa95f")         # Hierba 4
const ALIENTO_LLENO := Color("fff3c4")
const AGOTADA := Color("de6771")
const TEXTO := Color("fff3c4")

var _maisha: Node
var _visible := 0.0
var _texto := ""
var _texto_tiempo := 0.0
var _lienzo: Control
var _negro: ColorRect
var _ayuda := true
var texto_ayuda := "WASD mover · C correr · J golpe · K semilla · L latido"
var _fuente: FontFile
var _guardando := 0.0


func _ready() -> void:
	add_to_group("hud")
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	# letra nítida, sin suavizado (pixel art)
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	_fuente.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	_negro = ColorRect.new()
	_negro.color = Color(0.03, 0.03, 0.04, 0.0)
	_negro.set_anchors_preset(Control.PRESET_FULL_RECT)
	_negro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_negro)
	_conectar_zonas()
	Estado.guardado.connect(_al_guardar)


func _al_guardar() -> void:
	_guardando = 1.6


## Escucha los mensajes de las zonas corruptas (también las que se crean después, al cargar un mapa)
func _conectar_zonas() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.mensajes and not zona.mensaje.is_connected(mostrar_mensaje):
			zona.mensaje.connect(mostrar_mensaje)


func mostrar_mensaje(texto: String) -> void:
	_texto = texto
	_texto_tiempo = 3.0


## Al empezar una región: aparece desde negro y muestra su nombre
func despertar(titulo: String) -> void:
	_negro.color.a = 1.0
	var t := create_tween()
	t.tween_interval(0.3)
	t.tween_property(_negro, "color:a", 0.0, 1.4)
	t.tween_callback(mostrar_mensaje.bind(titulo))


## Funde a negro, ejecuta «en_medio» (p. ej. devolver a Maisha al borde) y vuelve a la imagen
func fundido(en_medio: Callable) -> void:
	var t := create_tween()
	t.tween_interval(0.5)
	t.tween_property(_negro, "color:a", 1.0, 0.45)
	t.tween_callback(en_medio)
	t.tween_interval(0.25)
	t.tween_property(_negro, "color:a", 0.0, 0.45)


func _process(delta: float) -> void:
	if _maisha == null:
		_maisha = get_tree().get_first_node_in_group("maisha")
		return
	_conectar_zonas()
	_texto_tiempo = maxf(0.0, _texto_tiempo - delta)
	_guardando = maxf(0.0, _guardando - delta)
	if Input.is_action_just_pressed("golpe") or Input.is_action_just_pressed("explosivo") \
			or Input.is_action_just_pressed("accion"):
		if _ayuda:
			Estado.marcar("ayuda/" + texto_ayuda)
		_ayuda = false
	if Estado.tiene("ayuda/" + texto_ayuda):
		_ayuda = false
	var hace_falta: bool = _hay_peligro() or _maisha.segundos_desde_danio() < 3.0 \
		or _maisha.aliento < _maisha.aliento_maximo() - 0.5 or _maisha.vida < _maisha.vida_maxima()
	_visible = move_toward(_visible, 1.0 if hace_falta else 0.0, delta * 3.0)
	_lienzo.queue_redraw()


func dialogo_narrando() -> bool:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	return dialogo != null and dialogo.hablando and dialogo.get("_estilo") == "narrador"


func _hay_peligro() -> bool:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado in [1, 2, 3]:   # AVISO, CERRADA, PURGANDO
			return true
	return false


func _hay_modal() -> bool:
	if get_tree().paused:
		return true
	var d := get_tree().get_first_node_in_group("dialogo")
	if d and d.hablando:
		return true
	for n: Node in get_tree().get_nodes_in_group("modales"):
		if n.has_method("esta_abierta") and bool(n.call("esta_abierta")):
			return true
	return false


func _dibujar() -> void:
	if _maisha == null:
		return
	var alfa := _visible
	var modal := _hay_modal()
	if alfa > 0.01 and not modal:
		var mod := Color(1, 1, 1, alfa)
		# panel de vida y aliento
		var hojas: int = _maisha.vida_maxima()
		var panel := Rect2(6, 6, maxi(10, hojas) * 10 + 10, 29)
		PIEL.caja(_lienzo, panel.grow(2), "cuero", 0.96 * alfa)
		PIEL.esquinas_oro(_lienzo, panel.grow(2), PIEL.ORO, 0.55 * alfa, 4.0)
		# vida: una hoja por bloque
		for i in hojas:
			var llena: bool = i < _maisha.vida
			_lienzo.draw_texture_rect_region(HOJAS, Rect2(10 + i * 10, 9, 9, 8),
				Rect2(0 if llena else 9, 0, 9, 8), mod)
		# aliento con medidor biselado y muesca de semilla
		var barra := Rect2(10, 22, panel.size.x - 10, 6)
		var parte: float = _maisha.aliento / _maisha.aliento_maximo()
		var color := ALIENTO_LLENO if parte >= 0.999 else ALIENTO
		if _maisha.agotada:
			color = AGOTADA if int(Time.get_ticks_msec() / 150) % 2 == 0 else ALIENTO
		var umbral := Artes.semilla_coste() / maxf(_maisha.aliento_maximo(), 0.01)
		PIEL.medidor(_lienzo, barra, parte, color, -1.0, Color.WHITE, alfa, 4, umbral)
		# sopas que lleva (se toman con F)
		var sopas := Estado.cuantos("sopa")
		if sopas > 0:
			var sx := panel.end.x + 6
			var scaja := Rect2(sx, 5, 52, 29)
			PIEL.caja(_lienzo, scaja, "cuero", 0.96 * alfa)
			_lienzo.draw_texture_rect_region(OBJETOS, Rect2(sx + 4, 11, 16, 16), Rect2(160, 0, 16, 16), mod)
			_lienzo.draw_string(_fuente, Vector2(sx + 21, 20), str(sopas), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(TEXTO, alfa))
			PIEL.tecla(_lienzo, Vector2(sx + 33, 12), "F", _fuente, 16, 0.92 * alfa)
		# el sigilo elegido (con más de uno aprendido)
		if (Estado.tiene("sigilo_hielo") or Estado.tiene("sigilo_rayo")) and _maisha.has_method("sigilo_elegido"):
			var caja := Rect2(6, panel.end.y + 6, 42, 22)
			PIEL.caja(_lienzo, caja, "cuero", 0.96 * alfa)
			var hielo: bool = _maisha.sigilo_elegido() == "hielo"
			var rayo: bool = _maisha.sigilo_elegido() == "rayo"
			var col := Color(0.75, 0.92, 1.0, alfa) if hielo else (Color(1.0, 0.92, 0.45, alfa) if rayo else Color(1.0, 0.62, 0.2, alfa))
			var c := caja.position + Vector2(11, 11)
			if rayo:
				_lienzo.draw_polyline(PackedVector2Array([c + Vector2(3, -6), c + Vector2(-3, -1), c + Vector2(3, 0), c + Vector2(-3, 6)]), col, 1.0)
				_lienzo.draw_line(c + Vector2(-5, -6), c + Vector2(5, -6), col, 1.0)
				_lienzo.draw_line(c + Vector2(-5, 6), c + Vector2(5, 6), col, 1.0)
			elif hielo:
				_lienzo.draw_polyline(PackedVector2Array([c + Vector2(0, -6), c + Vector2(4, 0), c + Vector2(0, 6), c + Vector2(-4, 0), c + Vector2(0, -6)]), col, 1.0)
				_lienzo.draw_line(c + Vector2(-6, -3), c + Vector2(6, 3), col, 1.0)
				_lienzo.draw_line(c + Vector2(-6, 3), c + Vector2(6, -3), col, 1.0)
			else:
				_lienzo.draw_line(c + Vector2(0, 6), c + Vector2(0, -5), col, 1.0)
				_lienzo.draw_polyline(PackedVector2Array([c + Vector2(-5, -1), c + Vector2(0, 2), c + Vector2(5, -1)]), col, 1.0)
				_lienzo.draw_line(c + Vector2(-3, 5), c + Vector2(3, 5), col, 1.0)
			PIEL.tecla(_lienzo, caja.position + Vector2(21, 4), "R", _fuente, 16, 0.92 * alfa)
	# mensaje centrado arriba (salvo si está hablando el narrador o hay modal abierto)
	var narrando: bool = dialogo_narrando()
	if _texto_tiempo > 0.0 and not narrando and not modal:
		var a := clampf(_texto_tiempo / 0.4, 0.0, 1.0)
		var tam := _fuente.get_string_size(_texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16)
		var pos := Vector2(round((640 - tam.x) / 2.0), 52 if get_tree().get_first_node_in_group("barra_jefe") == null else 86)
		var caja_msg := Rect2(pos - Vector2(18, 19), Vector2(tam.x + 36, 28))
		PIEL.caja(_lienzo, caja_msg, "noche", 0.96 * a)
		PIEL.esquinas_oro(_lienzo, caja_msg, PIEL.ORO, 0.85 * a, 5.0)
		_lienzo.draw_string(_fuente, pos + Vector2(1, 1), _texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.75 * a))
		_lienzo.draw_string(_fuente, pos, _texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(TEXTO, a))
	# aviso de que se ha guardado la partida (abajo a la derecha, encima de la barra de teclas si está visible)
	if _guardando > 0.0 and not modal:
		var a := clampf(_guardando / 0.5, 0.0, 1.0)
		var texto := "Guardado"
		var ancho := _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var base_y := 320.0 if (_ayuda and texto_ayuda != "") else 348.0
		var pos := Vector2(640 - 12 - ancho, base_y)
		var parpadeo := 1.0 if int(_guardando * 4.0) % 2 == 0 or _guardando < 1.0 else 0.4
		var gcaja := Rect2(pos + Vector2(-22, -16), Vector2(ancho + 32, 22))
		PIEL.caja(_lienzo, gcaja, "cuero", 0.96 * a, false)
		_lienzo.draw_texture_rect_region(HOJAS, Rect2(pos + Vector2(-14, -9), Vector2(9, 8)), Rect2(0, 0, 9, 8), Color(1, 1, 1, a * parpadeo))
		_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.6 * a))
		_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(TEXTO, a))
	# ayuda de controles hasta que se usan (en barra con pastillas tactiles)
	if _ayuda and texto_ayuda != "" and not modal:
		var pares := []
		for trozo: String in texto_ayuda.split(" · "):
			var limpio := trozo.strip_edges()
			var sp := limpio.find(" ")
			if sp > 0:
				pares.append([limpio.substr(0, sp), limpio.substr(sp + 1).capitalize()])
			elif not limpio.is_empty():
				pares.append([limpio, ""])
		PIEL.barra_teclas(_lienzo, 320.0, 344.0, pares, _fuente, 16, 0.96, true)
