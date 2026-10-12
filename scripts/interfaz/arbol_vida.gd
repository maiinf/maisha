extends CanvasLayer
## EL ÁRBOL DE LA VIDA: se abre al meditar junto al brote de un Claro de Calma.
## Cada rama es un Arte (Runa · Raíz · Aliento · Tierra); cada nudo de la rama, un nivel.
##   ← → eligen el Arte · ↑ ↓ miran sus niveles · mantener Acción despierta el siguiente nivel
##   Tab, Esc o Acción sobre «salir» dejan de meditar.
## Lo que da cada nivel está en datos/artes.json; la lógica, en scripts/globales/artes.gd.

signal cerrado

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PANEL := Color(0.06, 0.07, 0.08, 0.88)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const ORDEN := ["runa", "raiz", "aliento", "tierra"]
## Dónde está la punta de cada rama (y por dónde se curva)
const RAMAS := {
	"runa": [Vector2(320, 214), Vector2(210, 196), Vector2(96, 160)],
	"raiz": [Vector2(320, 196), Vector2(250, 150), Vector2(184, 62)],
	"aliento": [Vector2(320, 196), Vector2(390, 150), Vector2(456, 62)],
	"tierra": [Vector2(320, 214), Vector2(430, 196), Vector2(544, 160)],
}
const TRONCO := [Vector2(320, 300), Vector2(316, 250), Vector2(320, 196)]
## Mantener Acción este tiempo para despertar un nivel (para no gastar Esencia sin querer)
const MANTENER := 0.7

var abierto := false
var _elegida := 1
var _mirando := -1                   # nivel que se mira con ↑ ↓ (-1 = el siguiente)
var _lienzo: Control
var _fuente: FontFile
var _tiempo := 0.0
var _alfa := 0.0
var _carga := 0.0                    # cuánto se ha mantenido Acción
var _destellos: Array[Dictionary] = []
var _motas: Array[Dictionary] = []
var _abierto_en := -1
var _aviso := ""
var _aviso_t := 0.0
var _maisha_tex: Texture2D


func _ready() -> void:
	add_to_group("arbol_vida")
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	visible = false
	var azar := RandomNumberGenerator.new()
	azar.seed = 7
	for i in 46:
		_motas.append({"p": Vector2(azar.randf_range(0, 640), azar.randf_range(0, 360)), "v": azar.randf_range(4, 14),
			"f": azar.randf_range(0, TAU), "r": azar.randf_range(0.6, 1.6)})


func abrir() -> void:
	abierto = true
	visible = true
	_elegida = 1
	_mirando = -1
	_carga = 0.0
	_alfa = 0.0
	_abierto_en = Engine.get_process_frames()
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		var sprite := maisha.get_node_or_null("Sprite") as AnimatedSprite2D
		if sprite and sprite.sprite_frames.has_animation("reposo_abajo"):
			_maisha_tex = sprite.sprite_frames.get_frame_texture("reposo_abajo", 0)
	get_tree().paused = true
	var hud := get_tree().get_first_node_in_group("hud")
	if hud and hud.get("_lienzo"):
		hud.get("_lienzo").queue_redraw()


func cerrar() -> void:
	if not abierto:
		return
	abierto = false
	Sonido.efecto("menu_atras")
	var t := create_tween()
	t.tween_property(self, "_alfa", 0.0, 0.35)
	await t.finished
	visible = false
	get_tree().paused = false
	get_tree().set_meta("menu_cerrado_en", Engine.get_process_frames())
	cerrado.emit()


func _arte() -> Dictionary:
	return Artes.buscar(ORDEN[_elegida])


func _process(delta: float) -> void:
	_tiempo += delta
	if not abierto:
		_lienzo.queue_redraw()
		return
	_alfa = move_toward(_alfa, 1.0, delta * 2.0)
	_aviso_t = maxf(0.0, _aviso_t - delta)
	for d in _destellos:
		d["t"] += delta
		d["p"] += d["v"] * delta
		d["v"] *= 0.96
	_destellos = _destellos.filter(func(d: Dictionary) -> bool: return d["t"] < d["vida"])
	_lienzo.queue_redraw()
	if Engine.get_process_frames() == _abierto_en:
		return
	var arte := _arte()
	# mantener Acción para despertar el siguiente nivel
	if Input.is_action_pressed("accion") and Artes.puede_subir(String(arte.get("id", ""))):
		_carga += delta
		if _carga >= MANTENER:
			_carga = 0.0
			_subir()
	else:
		if Input.is_action_just_pressed("accion") and not Artes.puede_subir(String(arte.get("id", ""))):
			Sonido.efecto("menu_atras")
			_aviso = _por_que_no()
			_aviso_t = 2.0
		_carga = maxf(0.0, _carga - delta * 3.0)


## Las pulsaciones sueltas (salir, cambiar de Arte, mirar niveles) van por eventos
func _input(evento: InputEvent) -> void:
	if not abierto or Engine.get_process_frames() == _abierto_en or evento.is_echo():
		return
	if evento.is_action_pressed("mochila") or evento.is_action_pressed("menu"):
		cerrar()
	elif evento.is_action_pressed("mover_derecha") or evento.is_action_pressed("ui_right"):
		_elegir(mini(_elegida + 1, ORDEN.size() - 1))
	elif evento.is_action_pressed("mover_izquierda") or evento.is_action_pressed("ui_left"):
		_elegir(maxi(_elegida - 1, 0))
	elif evento.is_action_pressed("mover_arriba") or evento.is_action_pressed("ui_up"):
		_mirar(1)
	elif evento.is_action_pressed("mover_abajo") or evento.is_action_pressed("ui_down"):
		_mirar(-1)
	else:
		return
	get_viewport().set_input_as_handled()


func _mirar(paso: int) -> void:
	var maximo: int = _arte().get("niveles", []).size()
	if maximo == 0:
		return
	_mirando = clampi(_nivel_mirado() + paso, 0, maximo - 1)
	Sonido.efecto("menu_mover")


func _elegir(i: int) -> void:
	if i != _elegida:
		Sonido.efecto("menu_mover")
	_elegida = i
	_mirando = -1
	_carga = 0.0


## El nivel que se está mirando (índice desde 0): por defecto, el siguiente por despertar
func _nivel_mirado() -> int:
	var arte := _arte()
	var maximo: int = arte.get("niveles", []).size()
	if _mirando >= 0:
		return _mirando
	return mini(Artes.nivel(String(arte["id"])), maxi(0, maximo - 1))


func _por_que_no() -> String:
	var arte := _arte()
	if arte.has("bloqueada"):
		return String(arte["bloqueada"])
	var id := String(arte["id"])
	if Artes.nivel(id) >= Artes.nivel_maximo(id):
		return "Esta rama ya ha crecido todo lo que puede en Raíz."
	if Artes.esencia() < Artes.coste_siguiente(id):
		return "Hace falta más Esencia (%d de %d)." % [Artes.esencia(), Artes.coste_siguiente(id)]
	return "Este nodo grande pide también Cristales del Nexo (%d de %d)." % [Tienda.cristales(), Artes.cristales_siguiente(id)]


func _subir() -> void:
	var id := String(_arte()["id"])
	if not Artes.subir(id):
		return
	Sonido.efecto("arte_sube")
	_mirando = -1
	var nivel := Artes.nivel(id)
	var p := _nudo(id, nivel - 1)
	var color := Color(String(_arte()["color"]))
	var azar := RandomNumberGenerator.new()
	for i in 26:
		var a := azar.randf() * TAU
		_destellos.append({"p": p, "v": Vector2.from_angle(a) * azar.randf_range(20, 90), "t": 0.0,
			"vida": azar.randf_range(0.5, 1.1), "c": color})
	# la luz baja por la rama hasta Maisha
	for i in 10:
		_destellos.append({"p": _punto_rama(id, 1.0 - i / 10.0), "v": Vector2(0, azar.randf_range(-10, 10)), "t": -i * 0.04,
			"vida": 0.6, "c": color})
	var nivel_datos: Dictionary = _arte()["niveles"][nivel - 1]
	_aviso = "¡%s! %s" % [nivel_datos["nombre"], "Maisha cambia." if nivel_datos.has("rasgo") else ""]
	_aviso_t = 2.5


# --- Geometría de las ramas ------------------------------------------------------------

func _bezier(puntos: Array, t: float) -> Vector2:
	var a: Vector2 = puntos[0].lerp(puntos[1], t)
	var b: Vector2 = puntos[1].lerp(puntos[2], t)
	return a.lerp(b, t)


func _punto_rama(id: String, t: float) -> Vector2:
	var p := _bezier(RAMAS[id], t)
	return p + Vector2(0, sin(_tiempo * 0.8 + t * 3.0) * t * 1.5)


## Dónde está el nudo de un nivel (índice desde 0) en su rama
func _nudo(id: String, i: int) -> Vector2:
	var total := maxi(Artes.nivel_maximo(id), 6)
	return _punto_rama(id, 0.28 + 0.72 * float(i + 1) / total)


# --- Dibujo ---------------------------------------------------------------------------

func _texto(texto: String, pos: Vector2, color: Color, tam := 16) -> void:
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(0, 0, 0, 0.6 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, color)


func _ancho(texto: String) -> float:
	return _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x


func _parrafo(texto: String, pos: Vector2, ancho: float, color: Color) -> float:
	var linea := ""
	var y := pos.y
	for palabra in texto.split(" "):
		var prueba := palabra if linea == "" else linea + " " + palabra
		if _ancho(prueba) > ancho and linea != "":
			_texto(linea, Vector2(pos.x, y), color)
			y += 15
			linea = palabra
		else:
			linea = prueba
	if linea != "":
		_texto(linea, Vector2(pos.x, y), color)
		y += 15
	return y


func _brillo(p: Vector2, radio: float, color: Color, capas := 4) -> void:
	for i in capas:
		_lienzo.draw_circle(p, radio * (1.0 + i * 0.6), Color(color, color.a * 0.18 / (i + 1)))


func _dibujar() -> void:
	var a := _alfa
	if a <= 0.01:
		return
	# fondo: noche verde muy oscura con motas de luz que suben
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.02, 0.04, 0.03, 0.97 * a))
	for i in 6:
		_lienzo.draw_circle(Vector2(320, 240), 260.0 - i * 40.0, Color(0.15, 0.3, 0.12, 0.035 * a))
	for m in _motas:
		var p: Vector2 = m["p"]
		var y := fposmod(p.y - _tiempo * float(m["v"]), 360.0)
		var x := p.x + sin(_tiempo * 0.7 + float(m["f"])) * 6.0
		var parpadeo := 0.5 + 0.5 * sin(_tiempo * 2.0 + float(m["f"]) * 3.0)
		_lienzo.draw_circle(Vector2(x, y), float(m["r"]), Color(0.75, 1.0, 0.6, 0.35 * parpadeo * a))
	_dibujar_arbol(a)
	_dibujar_maisha(a)
	for d in _destellos:
		if d["t"] < 0.0:
			continue
		var vida: float = 1.0 - d["t"] / d["vida"]
		_brillo(d["p"], 1.5 + vida * 2.0, Color(d["c"], vida * a), 2)
		_lienzo.draw_circle(d["p"], 1.0, Color(1, 1, 0.9, vida * a))
	_dibujar_cabecera(a)
	_dibujar_detalle(a)


func _dibujar_arbol(a: float) -> void:
	# el tronco (de luz cálida)
	var tronco := PackedVector2Array()
	for i in 13:
		tronco.append(_bezier(TRONCO, i / 12.0))
	for capa in 3:
		_lienzo.draw_polyline(tronco, Color(0.95, 0.75, 0.4, (0.10 - capa * 0.03) * a), 16.0 - capa * 4.0)
	_lienzo.draw_polyline(tronco, Color(0.55, 0.38, 0.22, a), 7.0)
	_lienzo.draw_polyline(tronco, Color(0.85, 0.62, 0.36, a), 3.0)
	# raíces bajo Maisha
	for lado in [-1.0, 1.0]:
		var raiz := PackedVector2Array()
		for i in 8:
			var t := i / 7.0
			raiz.append(Vector2(320 + lado * t * 70.0, 300 + t * 18.0 + sin(t * 3.0) * 4.0))
		_lienzo.draw_polyline(raiz, Color(0.55, 0.38, 0.22, 0.7 * a), 3.0 - 0.5)
	# las ramas
	for i in ORDEN.size():
		var id: String = ORDEN[i]
		var arte := Artes.buscar(id)
		var bloqueada := arte.has("bloqueada")
		var color := Color(String(arte["color"]))
		var elegida := i == _elegida
		var nivel := Artes.nivel(id)
		var puntos := PackedVector2Array()
		for k in 17:
			puntos.append(_punto_rama(id, k / 16.0))
		var gris := Color(0.32, 0.3, 0.34)
		var grosor := 5.0 if not bloqueada else 3.0
		if elegida:
			_lienzo.draw_polyline(puntos, Color(color, 0.18 * a), grosor + 8.0)
		_lienzo.draw_polyline(puntos, Color(0.45, 0.32, 0.2, a) if not bloqueada else Color(gris, 0.7 * a), grosor)
		# la parte ya despierta de la rama brilla con su color
		if nivel > 0:
			var hasta := 0.28 + 0.72 * float(nivel) / maxi(Artes.nivel_maximo(id), 6)
			var vivo := PackedVector2Array()
			for k in 17:
				var t := hasta * k / 16.0
				vivo.append(_punto_rama(id, t))
			_lienzo.draw_polyline(vivo, Color(color, 0.85 * a), 2.0)
		# hojitas a lo largo de la rama
		for k in range(2, 16, 3):
			var t := k / 16.0
			var p := _punto_rama(id, t)
			var lado := 1.0 if k % 2 == 0 else -1.0
			var hoja_color := color if (not bloqueada and t <= 0.28 + 0.72 * float(nivel) / 6.0) else gris
			var h := p + Vector2(lado * 4.0, -3.0)
			_lienzo.draw_colored_polygon(PackedVector2Array([p, h + Vector2(lado * 2, -2), h + Vector2(lado * 3, 2)]), Color(hoja_color, 0.75 * a))
		# los nudos (niveles)
		var total := maxi(Artes.nivel_maximo(id), 6)
		for n in total:
			var p := _nudo(id, n)
			var despierto := n < nivel
			var siguiente := n == nivel and not bloqueada and n < Artes.nivel_maximo(id)
			var mirado := elegida and n == _nivel_mirado() and not bloqueada
			var datos_nivel: Dictionary = arte["niveles"][n] if n < arte.get("niveles", []).size() else {}
			var es_rasgo := datos_nivel.has("rasgo")
			var r := 6.0 if es_rasgo else 4.5
			if despierto:
				_brillo(p, r, Color(color, a))
				_lienzo.draw_circle(p, r, Color(color, a))
				_lienzo.draw_circle(p + Vector2(-1, -1), r * 0.45, Color(1, 1, 1, 0.55 * a))
			elif siguiente:
				var latido := 0.5 + 0.5 * sin(_tiempo * 4.0)
				var puede := Artes.puede_subir(id)
				_lienzo.draw_circle(p, r, Color(0.08, 0.1, 0.08, a))
				_lienzo.draw_arc(p, r, 0, TAU, 20, Color(color, (0.5 + 0.5 * latido) * a if puede else 0.45 * a), 1.5)
				if elegida and _carga > 0.0:
					_lienzo.draw_arc(p, r + 3.0, -PI / 2, -PI / 2 + TAU * _carga / MANTENER, 24, Color(1, 1, 0.85, a), 2.0)
			else:
				_lienzo.draw_circle(p, r, Color(0.06, 0.06, 0.07, a))
				_lienzo.draw_arc(p, r, 0, TAU, 16, Color(gris, 0.8 * a), 1.0)
			if es_rasgo and not despierto:
				# los niveles que cambian a Maisha llevan una estrellita
				_lienzo.draw_colored_polygon(PackedVector2Array([p + Vector2(0, -2.5), p + Vector2(1, -0.5), p + Vector2(2.5, 0),
					p + Vector2(1, 0.5), p + Vector2(0, 2.5), p + Vector2(-1, 0.5), p + Vector2(-2.5, 0), p + Vector2(-1, -0.5)]), Color(color if not bloqueada else gris, 0.8 * a))
			if mirado:
				_lienzo.draw_arc(p, r + 5.0 + sin(_tiempo * 5.0), 0, TAU, 24, Color(TEXTO, 0.8 * a), 1.0)
		# nombre del Arte en la punta
		var punta := _punto_rama(id, 1.0)
		var nombre := String(arte["nombre"]).replace("Arte de la ", "").replace("Arte del ", "")
		var cn := Color(color, a) if not bloqueada else Color(0.55, 0.53, 0.58, 0.9 * a)
		if elegida:
			cn = Color(TEXTO, a) if not bloqueada else Color(0.8, 0.78, 0.82, a)
		_texto(nombre, Vector2(round(punta.x - _ancho(nombre) / 2.0), punta.y - 12), cn)
		if not bloqueada:
			var cuenta := "%d/%d" % [nivel, Artes.nivel_maximo(id)]
			_texto(cuenta, Vector2(round(punta.x - _ancho(cuenta) / 2.0), punta.y + 22), Color(cn, 0.7 * a))


## Maisha medita al pie del árbol (con sus rasgos)
func _dibujar_maisha(a: float) -> void:
	var base := Vector2(320, 336)
	_brillo(base + Vector2(0, -30), 22.0, Color(0.8, 1.0, 0.7, 0.6 * a), 5)
	if Artes.tiene_rasgo("aura"):
		var pulso := 0.5 + 0.5 * sin(_tiempo * 2.0)
		_brillo(base + Vector2(0, -32), 30.0 + pulso * 4.0, Color(0.75, 0.92, 1.0, 0.8 * a), 5)
	if _maisha_tex:
		var tam := _maisha_tex.get_size() * 2.5
		var flota := sin(_tiempo * 1.6) * 2.0
		var mod := Color(1, 1, 1, a * (0.7 if Artes.tiene_rasgo("brisa") else 1.0))
		_lienzo.draw_texture_rect(_maisha_tex, Rect2(base - Vector2(tam.x / 2.0, tam.y) + Vector2(0, flota), tam), false, mod)


func _dibujar_cabecera(a: float) -> void:
	var titulo := "Árbol de la Vida"
	_texto(titulo, Vector2(round(320 - _ancho(titulo) / 2.0), 22), Color(TEXTO, a))
	# la Esencia que hay
	var esencia := "%d" % Artes.esencia()
	var caja := Rect2(640 - 16 - 72, 8, 72, 22)
	_lienzo.draw_rect(caja, Color(PANEL, a))
	_lienzo.draw_rect(caja, Color(FILO, 0.6 * a), false, 1.0)
	var c := caja.position + Vector2(13, 11)
	_brillo(c, 3.5, Color(0.8, 1.0, 0.6, a), 3)
	_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -6), c + Vector2(4, 0), c + Vector2(0, 6), c + Vector2(-4, 0)]), Color(0.75, 1.0, 0.55, a))
	_lienzo.draw_circle(c + Vector2(-1, -1), 1.2, Color(1, 1, 1, 0.8 * a))
	_texto(esencia, caja.position + Vector2(26, 16), Color(TEXTO, a))
	var etiqueta := "Esencia"
	_texto(etiqueta, Vector2(caja.position.x - 6 - _ancho(etiqueta), caja.position.y + 16), Color(APAGADO, 0.85 * a))


func _dibujar_detalle(a: float) -> void:
	var arte := _arte()
	var id := String(arte["id"])
	var color := Color(String(arte["color"]))
	var caja := Rect2(14, 226, 204, 112)
	_lienzo.draw_rect(caja, Color(PANEL, a))
	_lienzo.draw_rect(caja, Color(color, 0.7 * a), false, 1.0)
	var x := caja.position.x + 8
	_texto(String(arte["nombre"]), Vector2(x, caja.position.y + 16), Color(color, a))
	if arte.has("bloqueada"):
		var y := _parrafo(String(arte["texto"]), Vector2(x, caja.position.y + 34), caja.size.x - 16, Color(APAGADO, a))
		_texto(String(arte["bloqueada"]), Vector2(x, y + 6), Color(0.75, 0.72, 0.8, a))
	else:
		var n := _nivel_mirado()
		var niveles: Array = arte["niveles"]
		var datos: Dictionary = niveles[n]
		var nivel_actual := Artes.nivel(id)
		var estado := "despierto" if n < nivel_actual else ("siguiente" if n == nivel_actual else "dormido")
		_texto("Nivel %d · %s" % [n + 1, datos["nombre"]], Vector2(x, caja.position.y + 34), Color(TEXTO, a))
		var y := _parrafo(String(datos["texto"]), Vector2(x, caja.position.y + 51), caja.size.x - 16, Color(APAGADO, a))
		var pie := ""
		var color_pie := AMBAR
		if estado == "despierto":
			pie = "Ya despierto"
			color_pie = color
		elif estado == "siguiente":
			if Artes.puede_subir(id):
				pie = "Mantén Acción: %d de Esencia" % Artes.coste_siguiente(id)
				if Artes.cristales_siguiente(id) > 0:
					pie += " y %d Cristales" % Artes.cristales_siguiente(id)
			elif Artes.esencia() < Artes.coste_siguiente(id):
				pie = "Cuesta %d de Esencia (tienes %d)" % [Artes.coste_siguiente(id), Artes.esencia()]
				color_pie = Color(APAGADO, 0.8)
			else:
				pie = "Pide %d Cristales (tienes %d)" % [Artes.cristales_siguiente(id), Tienda.cristales()]
				color_pie = Color(APAGADO, 0.8)
		else:
			pie = "Antes, el nivel %d" % (nivel_actual + 1)
			color_pie = Color(APAGADO, 0.6)
		_texto(pie, Vector2(x, caja.end.y - 8), Color(color_pie, a))
	# ayuda abajo
	var ayuda := "← → Arte · ↑ ↓ niveles · Tab: salir"
	_texto(ayuda, Vector2(640 - 14 - _ancho(ayuda), 354), Color(APAGADO, 0.75 * a))
	if _aviso_t > 0.0:
		var b := clampf(_aviso_t / 0.4, 0.0, 1.0) * a
		var w := _ancho(_aviso) + 20
		var r := Rect2(round(320 - w / 2.0), 36, w, 22)
		_lienzo.draw_rect(r, Color(PANEL, 0.9 * b))
		_lienzo.draw_rect(r, Color(FILO, b), false, 1.0)
		_texto(_aviso, r.position + Vector2(10, 16), Color(TEXTO, b))
