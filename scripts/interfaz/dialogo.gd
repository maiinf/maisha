extends CanvasLayer
## DIÁLOGOS Y COSAS CON LAS QUE HABLAR.
##
## Caja de texto abajo, con el nombre de quien habla. El texto se escribe letra a letra;
## con Acción (Espacio / E / botón A) se completa la línea o se pasa a la siguiente.
##   await dialogo.decir("Bibi Musgo", ["Hola.", "¿Qué tal?"])
##
## Estilos:
##   "normal"       caja abajo con el nombre de quien habla
##   "pensamiento"  lo que piensa Maisha: caja más suave, borde de puntos y una nubecita
##   "narrador"     el narrador: banda arriba, sin nombre, y el juego se para mientras habla
##   await dialogo.decir("", ["Esos seres son..."], "narrador")
## Y susurros: un comentario flotando sobre un personaje que no para el juego
##   dialogo.susurrar(nodo, "(...No puede ser.)")
##
## También se encarga de hablar con lo que hay alrededor: todo lo que esté en el grupo
## «interactuables» y tenga interactuar() se puede usar al acercarse y pulsar Acción.
## Encima de lo que se puede usar aparece un bocadillo pequeño.

signal terminado

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PANEL := Color(0.08, 0.07, 0.10, 0.88)
const FILO := Color("d6b46e")            # Interfaz 2
const TEXTO := Color("fff3c4")           # Maisha 4
const NOMBRE := Color("e6a852")          # Flor ámbar 3
const LETRAS_POR_SEGUNDO := 45.0
const CAJA := Rect2(20, 272, 600, 76)
const CAJA_NARRADOR := Rect2(118, 8, 404, 72)
const PENSAMIENTO := Color("e2cea0")     # Pergamino 3
const VERDE := Color("6fcf4f")           # Brote 2
const NARRADOR := Color("ffe08a")        # Maisha 3
const DISTANCIA := 26.0
const PIEL := preload("res://scripts/interfaz/piel.gd")

var hablando := false
var _lineas: Array = []
var _nombre := ""
var _indice := 0
var _letras := 0.0
var _abierto_en := -1
var _lienzo: Control
var _texto: Label
var _cerca: Node2D = null
var _fuente: FontFile
var _tiempo := 0.0
var _estilo := "normal"
var _pause_mio := false
var _susurros: Array[Dictionary] = []
var _retrato: Texture2D = null
var _ilustracion: Texture2D = null
var _ilustracion_alfa := 0.0
var _ilustracion_objetivo := 0.0
var _retrato_base: Texture2D        # el retrato normal de quien habla (las caras salen de él)
var _ilustracion_pedida := false     # hay (o va a haber enseguida) una ilustración en pantalla
var _caja_n := CAJA_NARRADOR         # dónde habla el narrador en esta conversación


func _ready() -> void:
	add_to_group("dialogo")
	layer = 20
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
	_texto = Label.new()
	_texto.position = CAJA.position + Vector2(12, 9)
	_texto.size = Vector2(CAJA.size.x - 24, CAJA.size.y - 14)
	_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_texto.add_theme_font_override("font", _fuente)
	_texto.add_theme_font_size_override("font_size", 16)
	_texto.add_theme_color_override("font_color", TEXTO)
	_texto.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	_texto.add_theme_constant_override("shadow_offset_x", 1)
	_texto.add_theme_constant_override("shadow_offset_y", 1)
	_texto.add_theme_constant_override("line_spacing", -1)
	_texto.visible = false
	add_child(_texto)


## Muestra varias líneas seguidas. Mientras tanto Maisha no se mueve.
func decir(nombre: String, lineas: Array, estilo := "normal", retrato: Texture2D = null) -> void:
	if lineas.is_empty():
		return
	if hablando:
		await terminado
	hablando = true
	_estilo = estilo
	_retrato = retrato
	_retrato_base = retrato
	_caja_n = _caja_narrador()
	var caja := _caja_n if estilo == "narrador" else CAJA
	_texto.position = caja.position + Vector2(12, 9)
	_texto.size = Vector2(caja.size.x - 24, caja.size.y - 14)
	# en el pergamino se escribe con tinta; el narrador, en dorado sobre la noche
	_texto.add_theme_color_override("font_color", NARRADOR if estilo == "narrador" else (PIEL.TINTA_SUAVE if estilo == "pensamiento" else PIEL.TINTA))
	_texto.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6) if estilo == "narrador" else Color(0, 0, 0, 0))
	_texto.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER if estilo == "narrador" else HORIZONTAL_ALIGNMENT_LEFT
	if estilo == "narrador" and not get_tree().paused:
		get_tree().paused = true      # el mundo se para mientras habla el narrador
		_pause_mio = true
	_nombre = nombre
	_lineas = lineas
	_indice = 0
	_letras = 0.0
	_abierto_en = Engine.get_process_frames()
	_texto.visible = true
	_poner_linea()
	_bloquear_maisha(true)
	await terminado


## El narrador habla en una banda arriba; si hay una ilustración, en la caja de abajo (para no taparla)
func _caja_narrador() -> Rect2:
	return CAJA if _ilustracion_pedida else CAJA_NARRADOR


## Una línea puede empezar con la cara de quien habla: «[sonrisa] ¡Gracias!».
## Con retrato, se usa arte/retratos/<id>_<cara>.png; si habla o piensa Maisha, pone esa expresión.
func _poner_linea() -> void:
	var linea := String(_lineas[_indice])
	_retrato = _retrato_base
	if linea.begins_with("[") and linea.find("]") > 0:
		var cara := linea.substr(1, linea.find("]") - 1)
		linea = linea.substr(linea.find("]") + 1).strip_edges()
		if _retrato_base:
			var ruta := _retrato_base.resource_path.get_basename() + "_" + cara + ".png"
			if ResourceLoader.exists(ruta):
				_retrato = load(ruta)
		elif _nombre == "Maisha":
			var maisha := get_tree().get_first_node_in_group("maisha")
			if maisha and maisha.has_method("expresar"):
				maisha.expresar(cara)
	_texto.text = linea
	_texto.visible_characters = 0
	_letras = 0.0


func _linea_completa() -> bool:
	return _texto.visible_characters < 0 or _texto.visible_characters >= _texto.text.length()


## Ilustración de la historia (como las de los legendarios en Pokémon Platino): una imagen quieta
## pintada con mucho detalle (600×256, herramientas/cinematicas.py), con marco, encima de la caja de texto.
## Aparece y desaparece con un fundido.
func mostrar_ilustracion(textura: Texture2D) -> void:
	_ilustracion_pedida = true
	if _ilustracion and _ilustracion_alfa > 0.5 and textura != _ilustracion:
		# cambia de imagen: se apaga un momento y entra la siguiente
		_ilustracion_objetivo = 0.0
		await get_tree().create_timer(0.25, true).timeout
		if not _ilustracion_pedida:
			return                    # la han quitado mientras tanto
	_ilustracion = textura
	_ilustracion_objetivo = 1.0


func ocultar_ilustracion() -> void:
	_ilustracion_pedida = false
	_ilustracion_objetivo = 0.0


## Un comentario que flota sobre un personaje unos segundos, sin parar el juego
func susurrar(nodo: Node2D, texto: String, segundos := 3.5) -> void:
	_susurros.append({"nodo": nodo, "texto": texto, "vida": 0.0, "dura": segundos})


func _process(delta: float) -> void:
	_tiempo += delta
	_ilustracion_alfa = move_toward(_ilustracion_alfa, _ilustracion_objetivo, delta * 4.0)
	for su in _susurros:
		su["vida"] += delta
	_susurros = _susurros.filter(func(su: Dictionary) -> bool: return su["vida"] < su["dura"] and is_instance_valid(su["nodo"]))
	if get_tree().paused and not hablando:
		_cerca = null
		_lienzo.queue_redraw()
		return
	if hablando:
		if not _linea_completa():
			_letras += delta * LETRAS_POR_SEGUNDO
			_texto.visible_characters = int(_letras)
		if Input.is_action_just_pressed("accion") and Engine.get_process_frames() != _abierto_en:
			pasar()
		_cerca = null
	else:
		_cerca = _buscar_cerca()
		if _cerca and Input.is_action_just_pressed("accion") and not Estado.cambiando:
			_cerca.call("interactuar")
	_lienzo.queue_redraw()


## Acción: completa la línea que se está escribiendo o pasa a la siguiente
func pasar() -> void:
	if not hablando:
		return
	if not _linea_completa():
		_texto.visible_characters = -1
		return
	_indice += 1
	if _indice < _lineas.size():
		Sonido.efecto("dialogo_pasar")          # el «bip» al seguir leyendo
		_poner_linea()
		return
	Sonido.efecto("dialogo_cerrar")
	hablando = false
	_texto.visible = false
	if _pause_mio:
		_pause_mio = false
		get_tree().paused = false
	# un instante sin poder moverse, para que la misma pulsación no vuelva a hablar
	await get_tree().create_timer(0.12, true).timeout
	_bloquear_maisha(false)
	terminado.emit()


## Fuerza el cierre inmediato de cualquier diálogo abierto (seguridad al cambiar de escena o en cancelaciones)
func cerrar() -> void:
	if not hablando:
		return
	Sonido.efecto("dialogo_cerrar")
	hablando = false
	_texto.visible = false
	if _pause_mio:
		_pause_mio = false
		get_tree().paused = false
	_bloquear_maisha(false)
	terminado.emit()


func _bloquear_maisha(si: bool) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		maisha.set("puede_actuar", not si)


func _buscar_cerca() -> Node2D:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or not maisha.get("puede_actuar"):
		return null
	var mejor: Node2D = null
	var mejor_d := INF
	for n in get_tree().get_nodes_in_group("interactuables"):
		var nodo := n as Node2D
		if nodo == null or not nodo.is_visible_in_tree():
			continue
		var punto: Vector2 = nodo.call("punto_interaccion") if nodo.has_method("punto_interaccion") else nodo.global_position
		var radio: float = nodo.get("radio_interaccion") if nodo.get("radio_interaccion") != null else DISTANCIA
		var d := maisha.global_position.distance_to(punto)
		if d < radio and d < mejor_d:
			mejor = nodo
			mejor_d = d
	return mejor


func _dibujar() -> void:
	# ilustración de la historia, con el fondo oscurecido y un marco
	if _ilustracion and _ilustracion_alfa > 0.0:
		var a := _ilustracion_alfa
		_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, 0.8 * a))
		# las cinemáticas (600×256) se ven a su tamaño; las pequeñas de antes, al doble
		var escala := 1.0 if _ilustracion.get_width() >= 400 else 2.0
		var tam := _ilustracion.get_size() * escala
		var pos := Vector2(round((640 - tam.x) / 2.0), 7 if escala == 1.0 else 14)
		var marco := Rect2(pos, tam).grow(6)
		PIEL.caja(_lienzo, marco, "cuero", a)
		_lienzo.draw_texture_rect(_ilustracion, Rect2(pos, tam), false, Color(1, 1, 1, a))
	# susurros flotando sobre los personajes
	for su in _susurros:
		var nodo: Node2D = su["nodo"]
		var a := clampf(minf(su["vida"] / 0.4, (su["dura"] - su["vida"]) / 0.6), 0.0, 1.0)
		var texto: String = su["texto"]
		var ancho := _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var p: Vector2 = get_viewport().get_canvas_transform() * (nodo.global_position + Vector2(0, -44))
		p = (p - Vector2(ancho / 2.0, su["vida"] * 3.0)).round()
		_lienzo.draw_string(_fuente, p + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.7 * a))
		_lienzo.draw_string(_fuente, p, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(PENSAMIENTO, a))
	# bocadillo sobre lo que se puede usar: un papelito con tres puntos de tinta
	if _cerca and not hablando:
		var arriba: float = _cerca.get("altura_bocadillo") if _cerca.get("altura_bocadillo") != null else 36.0
		var p: Vector2 = get_viewport().get_canvas_transform() * (_cerca.global_position + Vector2(0, -arriba))
		p = p.round() + Vector2(0, round(sin(_tiempo * 4.0)))
		var caja := Rect2(p - Vector2(9, 7), Vector2(18, 12))
		_lienzo.draw_rect(Rect2(caja.position + Vector2(1, 2), caja.size), Color(0, 0, 0, 0.35))
		_lienzo.draw_rect(caja, Color("efe0bc"))
		_lienzo.draw_rect(caja, Color("6b4a2e"), false, 1.0)
		_lienzo.draw_colored_polygon(PackedVector2Array([p + Vector2(-2, 5), p + Vector2(2, 5), p + Vector2(0, 8)]), Color("6b4a2e"))
		for i in 3:
			_lienzo.draw_rect(Rect2(p + Vector2(-5 + i * 4, -1), Vector2(2, 2)), PIEL.TINTA)
	if not hablando:
		return
	if _estilo == "narrador":
		# la voz del narrador: un panel de noche con filigrana dorada (abajo si hay una ilustración en pantalla)
		var cn := _caja_n
		PIEL.caja(_lienzo, cn, "noche")
		if _linea_completa():
			var qn := cn.end - Vector2(16, 10 - round(sin(_tiempo * 6.0)))
			_lienzo.draw_colored_polygon(PackedVector2Array([qn + Vector2(-4, -3), qn + Vector2(4, -3), qn + Vector2(0, 2)]), NARRADOR)
		return
	# caja de texto: pergamino con borde de cuero (los pensamientos, en un papel suelto)
	if _estilo == "pensamiento":
		PIEL.caja(_lienzo, CAJA, "papel", 0.97)
	else:
		PIEL.caja(_lienzo, CAJA, "pergamino")
	# retrato de quien habla, encima de la caja a la derecha, en un marco de cuero
	if _retrato and _estilo == "normal" and _ilustracion_alfa < 0.05:
		var marco := Rect2(CAJA.end.x - 80, CAJA.position.y - 80, 76, 76)
		PIEL.caja(_lienzo, marco, "cuero")
		_lienzo.draw_rect(Rect2(marco.position + Vector2(5, 5), Vector2(66, 66)), Color("e6d3a8"))
		_lienzo.draw_texture(_retrato, marco.position + Vector2(6, 6))
	# pestaña con el nombre (los pensamientos llevan una nubecita)
	if _estilo == "pensamiento":
		var base := CAJA.position + Vector2(14, -6)
		for c: Vector3 in [Vector3(0, 2, 2.0), Vector3(7, -2, 3.0), Vector3(16, -6, 4.0)]:
			_lienzo.draw_circle(base + Vector2(c.x, c.y), c.z + 1.0, Color("6b4a2e"))
			_lienzo.draw_circle(base + Vector2(c.x, c.y), c.z, Color("efe0bc"))
		var ancho_n := _fuente.get_string_size(_nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		PIEL.caja(_lienzo, Rect2(base + Vector2(22, -14), Vector2(ancho_n + 12, 18)), "cuero", 1.0, false)
		_lienzo.draw_string(_fuente, base + Vector2(28, 0), _nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("b8ef8e"))
	elif _nombre != "":
		var ancho := _fuente.get_string_size(_nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var pestana := Rect2(CAJA.position + Vector2(12, -18), Vector2(ancho + 18, 20))
		PIEL.caja(_lienzo, pestana, "cuero")
		_lienzo.draw_string(_fuente, pestana.position + Vector2(10, 15), _nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, PIEL.CREMA)
	# flechita que indica que se puede seguir
	if _linea_completa():
		var q := CAJA.end - Vector2(18, 12 - round(sin(_tiempo * 6.0)))
		_lienzo.draw_colored_polygon(PackedVector2Array([q + Vector2(-4, -3), q + Vector2(4, -3), q + Vector2(0, 2)]), PIEL.ROJO)
