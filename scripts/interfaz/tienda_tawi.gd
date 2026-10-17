extends CanvasLayer
## LA TIENDA (de Tawi, en Cuna de Musgo; de Wino, en Maandiko): se abre al hablar con el tendero.
## A la izquierda, el puesto por dentro con Tawi detrás del mostrador (parpadea, habla, se alegra al vender);
## a la derecha, lo que vende, con su precio en Cristales del Nexo.
##   ↑ ↓ elegir · Acción comprar · Tab o Esc salir
## Lo que vende y cuánto cuesta: datos/tienda.json. La lógica (cristales, compras, ropa): scripts/globales/tienda.gd.

signal cerrado

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
## Cada tendero: su puesto por dentro, su dibujo grande (4 gestos), su nombre, el rótulo y lo que dice.
## (Los artículos llevan «tienda»: el id del tendero; sin ella, son de Tawi.)
const TENDEROS := {
	"tawi": {"fondo": preload("res://arte/interfaz/tienda_fondo.png"), "dibujo": preload("res://arte/interfaz/tienda_tawi.png"),
		"nombre": "Tawi", "rotulo": "Puesto de Tawi", "saludos": [
		"¡Pasa, pasa! Mira qué género. Todo de primera.",
		"¡Mira quién viene! Hoy tengo cosas que no verás en ningún otro puesto. Bueno, no hay otro puesto.",
		"¿Cristales del Nexo? ¡Aquí valen su peso en semillas!"]},
	"wino": {"fondo": preload("res://arte/interfaz/tienda_wino_fondo.png"), "dibujo": preload("res://arte/interfaz/tienda_wino.png"),
		"nombre": "Wino", "rotulo": "Tintas de Wino", "saludos": [
		"¡Bienvenida la luz! Mira, mira: la tinta ya se mueve en los botes.",
		"Plumas, tinta y papel. Y un par de cosas que no salen en ningún libro... todavía.",
		"¿Cristales del Nexo? Aquí se cambian por algo que escriba solo. Bueno, casi solo."]},
}
const ICONOS := preload("res://arte/interfaz/objetos.png")
const CRISTAL := preload("res://arte/interfaz/cristal.png")
const PANEL := Color(0.08, 0.07, 0.10, 0.94)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const VERDE := Color("8fd06a")
const ROJO := Color("de6771")
const AZUL := Color("97c1bf")
const POS_FONDO := Vector2(24, 34)
const PIEL := preload("res://scripts/interfaz/piel.gd")
const LISTA := Rect2(262, 34, 354, 292)
const VENDIDO := ["¡Trato hecho!", "¡Vendido! Un placer hacer negocios.", "¡Gran elección! Tienes buen ojo."]
const RESPUESTAS := {
	"caro": "Te faltan cristales. Cumple encargos y vuelve: ¡aquí te espero!",
	"agotado": "Eso ya es tuyo. ¡No vendo dos veces lo mismo!",
	"nada_que_olvidar": "Tu Árbol de la Vida aún no ha crecido. No hay nada que olvidar.",
}

@export var tendero := "tawi"
var abierto := false
var seleccion := 0
var _lienzo: Control
var _fuente: FontFile
var _alfa := 0.0
var _tiempo := 0.0
var _abierto_en := -1
var _frase := ""
var _letras := 0.0                 # cuántas letras de la frase se ven ya (Tawi habla mientras salen)
var _contento := 0.0
var _parpadeo := 2.5
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	add_to_group("tienda")
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	visible = false


func abrir() -> void:
	abierto = true
	visible = true
	seleccion = 0
	_alfa = 0.0
	_abierto_en = Engine.get_process_frames()
	var saludos: Array = TENDEROS[tendero]["saludos"]
	_decir(String(saludos[randi() % saludos.size()]))
	get_tree().paused = true
	Sonido.efecto("mochila_abrir")
	Sonido.musica("tienda", 0.8)
	create_tween().tween_property(self, "_alfa", 1.0, 0.3)


func cerrar() -> void:
	if not abierto:
		return
	abierto = false
	Sonido.efecto("mochila_cerrar")
	var escena := get_tree().current_scene
	if escena and escena.has_method("volver_a_su_musica"):
		escena.call("volver_a_su_musica")
	var t := create_tween()
	t.tween_property(self, "_alfa", 0.0, 0.25)
	await t.finished
	visible = false
	get_tree().paused = false
	get_tree().set_meta("menu_cerrado_en", Engine.get_process_frames())
	cerrado.emit()
	queue_free()


func _decir(frase: String) -> void:
	_frase = frase
	_letras = 0.0


func _lista() -> Array:
	return Tienda.disponibles().filter(func(a: Dictionary) -> bool: return String(a.get("tienda", "tawi")) == tendero)


func _process(delta: float) -> void:
	_tiempo += delta
	_letras += delta * 38.0
	_contento = maxf(0.0, _contento - delta)
	_parpadeo -= delta
	if _parpadeo < -0.15:
		_parpadeo = randf_range(2.0, 4.0)
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
		c["v"].y += 60.0 * delta
	_chispas = _chispas.filter(func(c: Dictionary) -> bool: return c["t"] < 0.9)
	_lienzo.queue_redraw()


func _input(evento: InputEvent) -> void:
	if not abierto or Engine.get_process_frames() == _abierto_en or evento.is_echo():
		return
	var n := _lista().size()
	if evento.is_action_pressed("mochila") or evento.is_action_pressed("menu"):
		cerrar()
	elif n > 0 and (evento.is_action_pressed("mover_abajo") or evento.is_action_pressed("ui_down")):
		seleccion = (seleccion + 1) % n
		Sonido.efecto("menu_mover")
	elif n > 0 and (evento.is_action_pressed("mover_arriba") or evento.is_action_pressed("ui_up")):
		seleccion = (seleccion - 1 + n) % n
		Sonido.efecto("menu_mover")
	elif evento.is_action_pressed("accion"):
		comprar_elegido()
	else:
		return
	get_viewport().set_input_as_handled()


func comprar_elegido() -> String:
	var lista := _lista()
	if seleccion >= lista.size():
		return "no_hay"
	var a: Dictionary = lista[seleccion]
	var r := Tienda.comprar(String(a["id"]))
	if r == "ok":
		Sonido.efecto("comprar")
		_contento = 1.4
		_decir(VENDIDO[int(_tiempo * 7.0) % VENDIDO.size()] + (" Póntelo en la mochila (Objetos)." if a.get("tipo", "") == "prenda" else ""))
		var centro := Vector2(LISTA.position.x + 22, _y_fila(seleccion) + 8)
		for k in 14:
			var ang := randf() * TAU
			_chispas.append({"p": centro, "v": Vector2(cos(ang), sin(ang) - 0.6) * randf_range(30, 90), "t": 0.0})
	else:
		Sonido.efecto("menu_atras")
		_decir(String(RESPUESTAS.get(r, "Hmm... eso no lo tengo.")))
	return r


# --- Dibujo ------------------------------------------------------------------------------

## Sobre el pergamino se escribe con tinta: cada color de siempre tiene su tinta
func _texto(texto: String, pos: Vector2, color: Color, tam := 16, en_papel := true) -> void:
	if en_papel:
		var tinta: Color = {TEXTO: PIEL.TINTA, APAGADO: PIEL.TINTA_SUAVE, AMBAR: PIEL.ROJO, AZUL: PIEL.AZUL, VERDE: PIEL.VERDE,
			ROJO: PIEL.ROJO}.get(Color(color, 1.0), PIEL.TINTA)
		_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(tinta, color.a))
		return
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(0, 0, 0, 0.6 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, color)


func _ancho(texto: String) -> float:
	return _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x


func _lineas(texto: String, ancho: float) -> Array[String]:
	var salida: Array[String] = []
	var linea := ""
	for palabra in texto.split(" "):
		var prueba := palabra if linea == "" else linea + " " + palabra
		if _ancho(prueba) > ancho and linea != "":
			salida.append(linea)
			linea = palabra
		else:
			linea = prueba
	if linea != "":
		salida.append(linea)
	return salida


func _caja(r: Rect2, a: float, tipo := "pergamino") -> void:
	PIEL.caja(_lienzo, r, tipo, a)


func _y_fila(i: int) -> float:
	return LISTA.position.y + 46 + i * 26


func _dibujar() -> void:
	var a := _alfa
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.02, 0.02, 0.03, 0.6 * a))
	var sube := (1.0 - a) * 16.0
	# ---- el puesto con su tendero
	var fondo: Texture2D = TENDEROS[tendero]["fondo"]
	var dibujo: Texture2D = TENDEROS[tendero]["dibujo"]
	var nombre: String = TENDEROS[tendero]["nombre"]
	var pf := POS_FONDO + Vector2(0, sube)
	_caja(Rect2(pf - Vector2(6, 6), Vector2(fondo.get_width() + 12, fondo.get_height() + 12)), a, "cuero")
	_lienzo.draw_texture(fondo, pf, Color(1, 1, 1, a))
	var f := 0
	if _contento > 0.0:
		f = 3
	elif _letras < _frase.length() and int(_tiempo * 9.0) % 2 == 0:
		f = 2
	elif _parpadeo < 0.0:
		f = 1
	var respira := roundf(sin(_tiempo * 2.4) * 0.8)
	var pt := pf + Vector2(62, 54 + respira)
	_lienzo.draw_texture_rect_region(dibujo, Rect2(pt, Vector2(96, 84)), Rect2(f * 96, 0, 96, 84), Color(1, 1, 1, a))
	# el mostrador por delante de Tawi
	_lienzo.draw_texture_rect_region(fondo, Rect2(pf + Vector2(0, 124), Vector2(fondo.get_width(), 44)),
		Rect2(0, 124, fondo.get_width(), 44), Color(1, 1, 1, a))
	# ---- lo que dice Tawi (letra a letra)
	var bocadillo := Rect2(pf.x - 4, pf.y + fondo.get_height() + 14, fondo.get_width() + 8, 100)
	_caja(bocadillo, a)
	var etiqueta := Rect2(bocadillo.position + Vector2(10, -10), Vector2(_ancho(nombre) + 16, 18))
	_caja(etiqueta, a, "cuero")
	_texto(nombre, etiqueta.position + Vector2(8, 14), Color(PIEL.CREMA, a), 16, false)
	var visible_txt := _frase.substr(0, int(_letras))
	var y := bocadillo.position.y + 38
	for linea in _lineas(visible_txt, bocadillo.size.x - 20):
		_texto(linea, Vector2(bocadillo.position.x + 10, y), Color(TEXTO, a))
		y += 17
	# ---- la lista de lo que vende
	var lista_r := Rect2(LISTA.position + Vector2(0, sube), LISTA.size)
	_caja(lista_r, a)
	_texto(String(TENDEROS[tendero]["rotulo"]), lista_r.position + Vector2(12, 22), Color(AMBAR, a))
	var cr := "%d" % Tienda.cristales()
	var xc := lista_r.end.x - 16 - _ancho(cr)
	_lienzo.draw_texture(CRISTAL, Vector2(xc - 14, lista_r.position.y + 10), Color(1, 1, 1, a))
	_texto(cr, Vector2(xc, lista_r.position.y + 22), Color(AZUL, a))
	PIEL.raya(_lienzo, Vector2(lista_r.position.x + 12, lista_r.position.y + 32), Vector2(lista_r.end.x - 12, lista_r.position.y + 32), PIEL.TINTA_SUAVE, 0.6 * a)
	var lista := _lista()
	for i in lista.size():
		var art: Dictionary = lista[i]
		var fy := _y_fila(i) + sube
		var fila := Rect2(lista_r.position.x + 8, fy - 4, lista_r.size.x - 16, 24)
		var elegida := i == seleccion
		if elegida:
			PIEL.subrayar(_lienzo, Rect2(fila.position + Vector2(10, 1), fila.size - Vector2(10, 2)), _tiempo, a)
			PIEL.marcapaginas(_lienzo, fila.position + Vector2(6, 12), a)
		var icono := int(art.get("icono", 0))
		_lienzo.draw_texture_rect_region(ICONOS, Rect2(fila.position + Vector2(12, 4), Vector2(16, 16)), Rect2(icono * 16, 0, 16, 16), Color(1, 1, 1, a))
		var agotado: bool = Tienda.agotado(art)
		var color_n := APAGADO if agotado else TEXTO
		_texto(String(art["nombre"]), fila.position + Vector2(34, 17), Color(color_n, a))
		var derecha := ""
		var color_d := AZUL
		if agotado:
			derecha = "Puesta" if Tienda.lleva(String(art["id"])) else "Comprado"
			color_d = VERDE
		else:
			var p := Tienda.precio(art)
			derecha = str(p)
			color_d = AZUL if Tienda.cristales() >= p else ROJO
			_lienzo.draw_texture(CRISTAL, Vector2(fila.end.x - 18, fila.position.y + 7), Color(1, 1, 1, a))
		var xd := fila.end.x - (22 if not agotado else 8) - _ancho(derecha)
		_texto(derecha, Vector2(xd, fila.position.y + 17), Color(color_d, a))
	if lista.is_empty():
		_texto("Hoy no queda nada. ¡Vuelve otro día!", lista_r.position + Vector2(12, 60), Color(APAGADO, a))
	# descripción de lo elegido
	if seleccion < lista.size():
		var art: Dictionary = lista[seleccion]
		var dy := lista_r.end.y - 92
		PIEL.raya(_lienzo, Vector2(lista_r.position.x + 12, dy - 8), Vector2(lista_r.end.x - 12, dy - 8), PIEL.TINTA_SUAVE, 0.6 * a)
		for linea in _lineas(String(art.get("texto", "")), lista_r.size.x - 24):
			_texto(linea, Vector2(lista_r.position.x + 12, dy + 8), Color(APAGADO, a))
			dy += 17
	var pie := Rect2(lista_r.position.x + 10, lista_r.end.y + 6, _ancho("↑ ↓ elegir · Acción comprar · Tab salir") + 20, 22)
	_caja(pie, a, "cuero")
	_texto("↑ ↓ elegir · Acción comprar · Tab salir", pie.position + Vector2(10, 16), Color(PIEL.CREMA, 0.9 * a), 16, false)
	# chispas al comprar
	for c in _chispas:
		var v: float = 1.0 - c["t"] / 0.9
		_lienzo.draw_rect(Rect2(c["p"].round(), Vector2(2, 2)), Color(0.75, 0.92, 1.0, v * a))
