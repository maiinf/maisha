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
## Metadatos tácticos por script de enemigo: telegrafía de ataque e icono de debilidad
const INFO_ENEMIGO := {
	"kaa_jiwe.gd": {"prop": "fase", "aviso": [1], "debil": "sismica"},
	"saa.gd": {"prop": "fase", "aviso": [2], "debil": "rayo"},
	"jabali.gd": {"prop": "fase", "aviso": [1], "debil": "escudo"},
	"tintero.gd": {"prop": "fase", "aviso": [1], "debil": "fuego"},
	"cangrejo.gd": {"prop": "fase", "aviso": [2], "debil": "atras"},
	"ruba.gd": {"prop": "fase", "aviso": [1], "debil": "hielo"},
	"sombra_renglon.gd": {"prop": "fase", "aviso": [1], "debil": "fuego"},
	"murcielago.gd": {"prop": "fase", "aviso": [2], "debil": "latido"},
	"cuervo.gd": {"prop": "fase", "aviso": [1], "debil": ""},
	"rana.gd": {"prop": "fase", "aviso": [1], "debil": ""},
	"topo.gd": {"prop": "fase", "aviso": [1], "debil": ""},
	"anguila.gd": {"prop": "fase", "aviso": [0], "debil": ""},
	"bundi.gd": {"prop": "estado", "aviso": [1], "debil": "escudo"},
	"buibui.gd": {"prop": "fase", "aviso": [], "debil": "semilla"},
	"espino.gd": {"prop": "fase", "aviso": [], "debil": "semilla"},
	"pagina_suelta.gd": {"prop": "fase", "aviso": [], "debil": "fuego"},
}

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
var _enemigos_estado := {}   # id -> {max: int, ant: int, cola: float, destello: float}


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
	_actualizar_enemigos(delta)
	_lienzo.queue_redraw()


func _actualizar_enemigos(delta: float) -> void:
	var vivos := {}
	for en in get_tree().get_nodes_in_group("enemigos"):
		if not is_instance_valid(en):
			continue
		var v_val: Variant = en.get("vida")
		if v_val == null:
			continue
		var vida := int(v_val)
		var id := en.get_instance_id()
		vivos[id] = true
		var st: Dictionary = _enemigos_estado.get(id, {"max": maxi(1, vida), "ant": vida, "cola": float(vida), "destello": 0.0})
		st["max"] = maxi(int(st["max"]), vida)
		if vida < int(st["ant"]):
			st["destello"] = 0.28
		st["ant"] = vida
		st["cola"] = move_toward(float(st["cola"]), float(vida), delta * 2.2)
		st["destello"] = maxf(0.0, float(st["destello"]) - delta)
		_enemigos_estado[id] = st
	for id in _enemigos_estado.keys():
		if not vivos.has(id):
			_enemigos_estado.erase(id)


func _proyectar_sobre_cabeza(en: Node2D, altura_m := 1.25, offset_2d := Vector2(0, -18)) -> Variant:
	var esp := get_tree().root.get_node_or_null("EspejoHD2D")
	if esp != null:
		var cam_v: Variant = esp.get("camara")
		if cam_v is Camera3D and is_instance_valid(cam_v):
			var cam3 := cam_v as Camera3D
			var wpos := Vector3(en.global_position.x * 0.0625, altura_m, en.global_position.y * 0.0625)
			if cam3.is_position_behind(wpos):
				return null
			var pos_vp := cam3.unproject_position(wpos)
			var vr := get_viewport().get_visible_rect().size
			if vr.x > 1.0 and vr.y > 1.0:
				pos_vp *= Vector2(640.0 / vr.x, 360.0 / vr.y)
			return pos_vp
	return get_viewport().get_canvas_transform() * (en.global_position + offset_2d)


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
	if not modal:
		_dibujar_barras_enemigos()
	if alfa > 0.01 and not modal:
		var mod := Color(1, 1, 1, alfa)
		# panel de vida y aliento
		var hojas: int = _maisha.vida_maxima()
		var panel := Rect2(6, 6, maxi(10, hojas) * 10 + 10, 29)
		var pulso_p := 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.008)
		PIEL.caja(_lienzo, panel.grow(2), "cuero", 0.96 * alfa)
		if _maisha.vida == 1:
			_lienzo.draw_rect(panel.grow(3), Color("de6771", (0.28 + 0.35 * pulso_p) * alfa), false, 1.0)
		PIEL.esquinas_oro(_lienzo, panel.grow(2), Color("de6771") if _maisha.vida == 1 else PIEL.ORO, 0.65 * alfa, 4.0)
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


## Mini barras biseladas, telegrafía e indicadores tácticos sobre enemigos
func _dibujar_barras_enemigos() -> void:
	for en in get_tree().get_nodes_in_group("enemigos"):
		if not is_instance_valid(en) or not (en is Node2D):
			continue
		var n2d := en as Node2D
		if not n2d.visible or en.get("_barra") != null:
			continue
		var st: Dictionary = _enemigos_estado.get(en.get_instance_id(), {})
		if st.is_empty():
			continue
		var vmax := int(st["max"])
		var vida := int(st["ant"])
		if vmax <= 0 or vmax > 8 or vida <= 0:
			continue
		var helado := float(en.get("_congelado")) > 0.0 if en.get("_congelado") != null else false
		var electro := float(en.get("_electrificado")) > 0.0 if en.get("_electrificado") != null else false
		var volcado := float(en.get("_volcado")) > 0.0 if en.get("_volcado") != null else false
		var info := _info_enemigo(n2d)
		var avisando := _esta_telegrafiando(n2d, info)
		var herido_o_alterado := vida < vmax or helado or electro or volcado
		if not herido_o_alterado and not avisando:
			continue
		var p_v: Variant = _proyectar_sobre_cabeza(n2d)
		if p_v == null:
			continue
		var p: Vector2 = (p_v as Vector2).round()
		if p.x < -20.0 or p.x > 660.0 or p.y < 14.0 or p.y > 350.0:
			continue
		var top_y := p.y - 2.0
		if herido_o_alterado:
			var w := clampf(float(vmax) * 7.0 + 2.0, 18.0, 44.0)
			var caja := Rect2(roundf(p.x - w * 0.5), roundf(p.y - 6.0), w, 6.0)
			top_y = caja.position.y
			var destello := float(st["destello"]) > 0.0
			_lienzo.draw_rect(Rect2(caja.position + Vector2(1, 1), caja.size), Color(0, 0, 0, 0.55))
			_lienzo.draw_rect(caja, Color(0.08, 0.05, 0.11, 0.94))
			_lienzo.draw_rect(caja, Color("fff3c4") if destello else Color(PIEL.ORO, 0.7), false, 1.0)
			var inner := caja.grow(-1)
			var cola := clampf(float(st["cola"]) / float(vmax), 0.0, 1.0)
			var frac := clampf(float(vida) / float(vmax), 0.0, 1.0)
			if cola > frac:
				var cw := maxf(1.0, roundf(inner.size.x * cola))
				_lienzo.draw_rect(Rect2(inner.position, Vector2(cw, inner.size.y)), Color("f4df9a", 0.9))
			var rw := maxf(1.0, roundf(inner.size.x * frac))
			var col_fill := Color("d64f5e")
			if helado:
				col_fill = Color("7ad7f0")
			elif electro:
				col_fill = Color("f6e05e")
			elif volcado:
				col_fill = Color("ef8a26")
			_lienzo.draw_rect(Rect2(inner.position, Vector2(rw, inner.size.y)), col_fill)
			_lienzo.draw_rect(Rect2(inner.position, Vector2(rw, 1.0)), col_fill.lightened(0.35))
			if vmax > 1 and vmax <= 6:
				for k in range(1, vmax):
					var tx := roundf(inner.position.x + inner.size.x * float(k) / float(vmax))
					_lienzo.draw_line(Vector2(tx, inner.position.y), Vector2(tx, inner.end.y), Color(0.08, 0.05, 0.11, 0.72), 1.0)
			var debil := String(info.get("debil", ""))
			if debil != "":
				PIEL.icono_tactico(_lienzo, Vector2(caja.position.x - 8.0, caja.get_center().y), debil, 0.85, 0.96)
			if helado or electro or volcado:
				var tag := "ATURDIDO" if volcado else ("RAYO" if electro else "HIELO")
				var col_tag := Color("ef8a26") if volcado else (Color("f6e05e") if electro else Color("7ad7f0"))
				var cx := roundf(p.x - _fuente.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x * 0.5)
				_lienzo.draw_string(_fuente, Vector2(cx + 1, caja.position.y - 2).round(), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.8))
				_lienzo.draw_string(_fuente, Vector2(cx, caja.position.y - 3).round(), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, col_tag)
				top_y -= 13.0
		if avisando:
			_dibujar_aviso_ataque(Vector2(p.x, top_y - 8.0))


func _info_enemigo(n2d: Node2D) -> Dictionary:
	var scr: Script = n2d.get_script() as Script
	if scr == null:
		return {}
	return INFO_ENEMIGO.get(scr.resource_path.get_file(), {})


func _esta_telegrafiando(n2d: Node2D, info: Dictionary) -> bool:
	if info.is_empty():
		return false
	var avisos: Array = info.get("aviso", [])
	if avisos.is_empty():
		return false
	var val: Variant = n2d.get(String(info.get("prop", "fase")))
	return val != null and int(val) in avisos


func _dibujar_aviso_ataque(centro: Vector2) -> void:
	var c := centro.round()
	var pulso := 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.025)
	var col_fondo := Color("de6771").lerp(Color("ff3b4a"), pulso)
	var r := 6.0 + pulso
	_lienzo.draw_colored_polygon(PackedVector2Array([
		c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0)
	]), Color(0.08, 0.04, 0.08, 0.94))
	_lienzo.draw_polyline(PackedVector2Array([
		c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0), c + Vector2(0, -r)
	]), col_fondo, 1.2)
	_lienzo.draw_rect(Rect2(c + Vector2(-1, -3), Vector2(2, 4)), Color("fff3c4"))
	_lienzo.draw_rect(Rect2(c + Vector2(-1, 2), Vector2(2, 2)), Color("fff3c4"))
