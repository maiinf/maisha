extends Node2D
## PANTALLA DE INICIO: el diario de Maisha, cerrado, sobre una mesa de madera a la luz de una vela.
##   Continuar        (solo si hay una partida guardada: dice dónde y cuánto tiempo)
##   Nueva partida    (si ya hay una guardada, pregunta antes de borrarla)
##   Pantalla completa
##   Salir
## El menú está en una tarjeta de papel junto al diario. Al empezar o continuar, el diario se abre
## (como la mochila); en una partida nueva, la introducción se escribe a pluma en la primera página.
## La mesa: arte/interfaz/inicio_mesa.png (herramientas/pintar_inicio_mesa.py).

const MESA := preload("res://arte/interfaz/inicio_mesa.png")
const LOGO := preload("res://arte/interfaz/logo_maisha.png")
const LIBRO := preload("res://arte/interfaz/diario/libro.png")
const TAPA := preload("res://arte/interfaz/diario/tapa.png")
const LISTA := preload("res://scripts/interfaz/menu_lista.gd")
const PIEL := preload("res://scripts/interfaz/piel.gd")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const VERSION := "v0.6 · prototipo"
const APAGADO := Color("c9b07e")
const LOMO := 320.0
const LLAMA := Vector2(284, 124)          # la punta de la mecha (la misma que en pintar_inicio_mesa.py)
const TARJETA_X := 30.0
const TARJETA_Y := 116.0
const MENU_FUERA := 0.35                  # lo que tarda en irse la tarjeta del menú
const ABRIR_DURA := 1.3                   # lo que tarda el diario en abrirse
const LINEA_DURA := 2.6                   # cada línea de la introducción
const LETRAS_SEG := 26.0                  # letras por segundo de la pluma
const INTRO := ["Silencio.", "Bajo la tierra gris, algo sigue latiendo.", "Despierta."]
## La tinta de la introducción: clara (las páginas son de cielo de noche), como en el diario del juego
const TINTA_CLARA := Color("efe6cf")
const TINTA_SUAVE := Color("e2e2f6")
const TINTA_ROJA := Color("f2a07a")
const PAG_IZQ := Rect2(38, 48, 272, 282)
const PAG_DER := Rect2(332, 48, 270, 282)

var _lista: Control
var _pregunta: Control
var _lienzo: Control
var _brillo: Control
var _fuente: FontFile
var _tiempo := 0.0
var _motas: Array[Dictionary] = []
var _azar := RandomNumberGenerator.new()
var _acciones: Array[String] = []
var _intro := -1            # línea de la introducción que se está escribiendo (-1 = no hay)
var _intro_tiempo := 0.0
var _saliendo := false
var _abriendo := -1.0       # tiempo desde que se eligió empezar o continuar (-1 = el diario sigue cerrado)
var _tras_abrir := ""       # "intro" o "continuar"
var _negro := 0.0           # el fundido final a negro
var _letras_antes := 0


func _ready() -> void:
	Estado.jugando = false
	Sonido.musica("inicio", 1.0)
	Sonido.ambiente({"fuego": 0.25})
	RenderingServer.set_default_clear_color(Color("0e0705"))
	_azar.seed = 8
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	var mesa := Sprite2D.new()
	mesa.texture = MESA
	mesa.centered = false
	add_child(mesa)
	# todo lo demás, en una capa por encima: el diario, la tarjeta, la llama, las motas y los textos
	var capa := CanvasLayer.new()
	capa.layer = 5
	add_child(capa)
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	capa.add_child(_lienzo)
	# la luz de la vela, que se suma a lo que hay debajo (también ilumina el diario)
	_brillo = Control.new()
	_brillo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_brillo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_brillo.material = suma
	_brillo.draw.connect(_dibujar_brillo)
	capa.add_child(_brillo)
	_lista = LISTA.new()
	_lista.en_papel = true
	_lista.position = Vector2(TARJETA_X + 22, TARJETA_Y + 20)
	_lista.size = Vector2(196, 120)
	_lista.elegida.connect(_al_elegir)
	capa.add_child(_lista)
	_pregunta = LISTA.new()
	_pregunta.en_papel = true
	_pregunta.position = Vector2(254, 210)
	_pregunta.size = Vector2(140, 50)
	_pregunta.visible = false
	_pregunta.elegida.connect(_al_responder)
	capa.add_child(_pregunta)
	_montar_menu()
	# aparece desde negro
	var negro := ColorRect.new()
	negro.color = Color("0e0705")
	negro.set_anchors_preset(Control.PRESET_FULL_RECT)
	negro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	capa.add_child(negro)
	create_tween().tween_property(negro, "color:a", 0.0, 1.2)


func _montar_menu() -> void:
	var opciones := []
	_acciones.clear()
	var guardada := Estado.leer_partida()
	if not guardada.is_empty():
		var lugar := String(guardada.get("lugar", ""))
		var nota := "%s · %s" % [lugar, Estado.texto_tiempo(float(guardada.get("tiempo", 0.0)))]
		opciones.append({"texto": "Continuar", "nota": nota})
		_acciones.append("continuar")
	opciones.append({"texto": "Nueva partida"})
	_acciones.append("nueva")
	var completa := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
	opciones.append({"texto": "Pantalla completa: %s" % ("sí" if completa else "no")})
	_acciones.append("pantalla")
	opciones.append({"texto": "Salir"})
	_acciones.append("salir")
	_lista.opciones = opciones
	_lista.size.y = _lista.alto_total()


func _al_elegir(i: int) -> void:
	if _saliendo:
		return
	match _acciones[i]:
		"continuar":
			_saliendo = true
			_lista.activa = false
			_abrir("continuar")
		"nueva":
			if Estado.hay_partida():
				# pregunta antes de borrar la partida guardada
				_lista.activa = false
				_pregunta.opciones = [{"texto": "No"}, {"texto": "Sí, empezar"}]
				_pregunta.seleccion = 0
				_pregunta.size.y = _pregunta.alto_total()
				_pregunta.visible = true
				_pregunta.activa = true
				_pregunta.reiniciar()
			else:
				_empezar()
		"pantalla":
			var completa := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if completa else DisplayServer.WINDOW_MODE_FULLSCREEN)
			_montar_menu()
		"salir":
			await Sonido.callar()
			get_tree().quit()


func _al_responder(i: int) -> void:
	_pregunta.visible = false
	_pregunta.activa = false
	if i == 1:
		_empezar()
	else:
		_lista.activa = true
		_lista.reiniciar()


## Partida nueva: se abre el diario y la introducción se escribe en la primera página; luego, a despertar en el Kitovu
func _empezar() -> void:
	_saliendo = true
	# la música del despertar: de un largo letargo a abrir los ojos (al acabar, la del Kitovu)
	Sonido.musica("despertar", 3.0, "kitovu")
	_lista.activa = false
	Estado.borrar_partida()
	Estado.olvidar_todo()
	_abrir("intro")


func _abrir(despues: String) -> void:
	_tras_abrir = despues
	_abriendo = 0.0
	_lista.activa = false


func _process(delta: float) -> void:
	_tiempo += delta
	_animar_motas(delta)
	if _abriendo >= 0.0:
		_abriendo += delta
		var antes := _abriendo - delta
		if antes < MENU_FUERA and _abriendo >= MENU_FUERA:
			Sonido.efecto("libro_abrir")
		_lista.visible = _abriendo < MENU_FUERA
		_lista.modulate.a = 1.0 - clampf(_abriendo / MENU_FUERA, 0.0, 1.0)
		var abierto := _abriendo >= MENU_FUERA + ABRIR_DURA
		if abierto and _intro == -1:
			if _tras_abrir == "continuar":
				_intro = -2
				Estado.continuar()
			else:
				_intro = 0
				_intro_tiempo = 0.0
				_letras_antes = 0
	if _intro >= 0:
		_intro_tiempo += delta
		var linea: String = INTRO[_intro]
		var letras := mini(linea.length(), int(_intro_tiempo * LETRAS_SEG))
		if letras > _letras_antes and _letras_antes % 6 == 0:
			Sonido.efecto("pluma")
		_letras_antes = letras
		var saltar := Input.is_action_just_pressed("accion") or Input.is_action_just_pressed("ui_accept")
		if _intro_tiempo > LINEA_DURA or (saltar and _intro_tiempo > 0.4):
			if saltar:
				Sonido.efecto("dialogo_pasar")
			_intro += 1
			_intro_tiempo = 0.0
			_letras_antes = 0
			if _intro >= INTRO.size():
				_intro = -2          # se acabó: a despertar
				Estado.ir_a("kitovu", "")
	if _intro == -2:
		_negro = minf(1.0, _negro + delta / 0.6)
	_lienzo.queue_redraw()
	_brillo.queue_redraw()


func _animar_motas(delta: float) -> void:
	# motas de polvo que flotan en la luz de la vela
	if _motas.size() < 22 and _azar.randf() < delta * 6.0:
		var a := _azar.randf() * TAU
		var r := _azar.randf_range(10, 110)
		_motas.append({"pos": LLAMA + Vector2(cos(a) * r * 1.3, sin(a) * r * 0.9 + 30), "fase": _azar.randf() * TAU,
			"vida": 0.0, "dura": _azar.randf_range(4, 9)})
	for m in _motas:
		m["vida"] += delta
		m["pos"] += Vector2(sin(m["vida"] * 0.5 + m["fase"]) * 3.0, -2.0 + cos(m["vida"] * 0.7 + m["fase"]) * 2.0) * delta
	_motas = _motas.filter(func(m: Dictionary) -> bool: return m["vida"] < m["dura"])


## La vela tiembla: un parpadeo lento con algún temblor rápido
func _parpadeo() -> float:
	return 0.82 + 0.1 * sin(_tiempo * 3.1) + 0.06 * sin(_tiempo * 7.7 + 1.0) + 0.04 * sin(_tiempo * 17.0)


func _ease(t: float) -> float:
	return 1.0 - pow(1.0 - clampf(t, 0.0, 1.0), 3.0)


# ---------------------------------------------------------------- dibujo

func _dibujar() -> void:
	var abre := 0.0
	var menu := 1.0
	if _abriendo >= 0.0:
		menu = 1.0 - clampf(_abriendo / MENU_FUERA, 0.0, 1.0)
		abre = clampf((_abriendo - MENU_FUERA) / ABRIR_DURA, 0.0, 1.0)
	_dibujar_llama(1.0 - _ease(abre * 1.6))
	_dibujar_motas(1.0 - abre)
	# la penumbra de la mesa cuando el diario se abre
	if abre > 0.0:
		_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.015, 0.01, 0.6 * _ease(abre)))
	_dibujar_diario(abre)
	if menu > 0.0:
		_dibujar_tarjeta(menu)
	if _intro >= 0 or (_intro == -2 and _tras_abrir == "intro"):
		_dibujar_intro()
	# pie: controles y versión
	if menu > 0.0:
		var ayuda := "↑↓ elegir · Espacio aceptar"
		_texto(ayuda, Vector2(10, 352), Color(APAGADO, 0.75 * menu))
	# la pregunta antes de borrar una partida
	if _pregunta.visible:
		var caja := Rect2(222, 150, 228, 112)
		PIEL.caja(_lienzo, caja, "pergamino")
		_lienzo.draw_string(_fuente, caja.position + Vector2(18, 26), "Se borrará la partida guardada.", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, PIEL.ROJO)
		_lienzo.draw_string(_fuente, caja.position + Vector2(18, 46), "¿Empezar de cero?", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, PIEL.TINTA)
	if _negro > 0.0:
		_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.055, 0.03, 0.02, _negro))


## El diario: cerrado (tapa y lomo) o abriéndose, con la técnica de la mochila: la tapa se estrecha hacia el lomo
## y luego la página de la izquierda se despliega desde él
func _dibujar_diario(abre: float) -> void:
	var giro := _ease(abre) if abre < 1.0 else 1.0
	giro = giro * giro * (3.0 - 2.0 * giro)
	if giro < 0.5:
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO, 0, 320, 360), Rect2(LOMO, 0, 320, 360))
		var w := (1.0 - giro * 2.0) * TAPA.get_width()
		if abre <= 0.0:
			# el lomo redondeado del diario cerrado, a la izquierda de la tapa
			_lienzo.draw_rect(Rect2(LOMO - 6, 33, 9, 316), Color("2a130b"))
			_lienzo.draw_rect(Rect2(LOMO - 5, 34, 3, 314), Color("552a19"))
			_lienzo.draw_rect(Rect2(LOMO - 4, 35, 1, 312), Color("874c2e"))
			for y in [70, 190, 310]:
				_lienzo.draw_rect(Rect2(LOMO - 6, y, 9, 2), Color("170a06"))
				_lienzo.draw_rect(Rect2(LOMO - 6, y + 2, 9, 1), Color("a0613c"))
		if w > 1.0:
			_lienzo.draw_texture_rect(TAPA, Rect2(LOMO + 2, 30, w, TAPA.get_height()), false, Color(1, 1, 1).darkened(giro * 0.8))
	else:
		var w := (giro - 0.5) * 2.0 * LOMO
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO, 0, 320, 360), Rect2(LOMO, 0, 320, 360))
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO - w, 0, w, 360), Rect2(0, 0, LOMO, 360), Color(1, 1, 1).darkened((1.0 - giro) * 0.9))


## El logo sobre la mesa y la tarjeta de papel sujeta con cinta donde va el menú
func _dibujar_tarjeta(alfa: float) -> void:
	var sube := (1.0 - alfa) * -10.0
	var logo_pos := Vector2(34, 26 + round(sin(_tiempo * 1.2) * 1.0) + sube)
	_lienzo.draw_texture_rect(LOGO, Rect2(logo_pos + Vector2(3, 4), LOGO.get_size() * 3), false, Color(0, 0, 0, 0.55 * alfa))
	_lienzo.draw_texture_rect(LOGO, Rect2(logo_pos, LOGO.get_size() * 3), false, Color(1, 1, 1, alfa))
	var alto: float = _lista.alto_total() + 52
	var tarjeta := Rect2(TARJETA_X, TARJETA_Y + sube, 222, alto)
	PIEL.caja(_lienzo, tarjeta, "papel", alfa)
	# dos trozos de cinta que la sujetan a la mesa
	for p: Vector2 in [tarjeta.position + Vector2(-6, -4), tarjeta.position + Vector2(tarjeta.size.x - 26, -6)]:
		var cinta := PackedVector2Array([p, p + Vector2(30, 6), p + Vector2(27, 16), p + Vector2(-3, 10)])
		_lienzo.draw_colored_polygon(cinta, Color(0.93, 0.88, 0.72, 0.55 * alfa))
		_lienzo.draw_polyline(PackedVector2Array([p, p + Vector2(30, 6)]), Color(1, 1, 1, 0.25 * alfa), 1.0)
	# la versión, a lápiz en la esquina
	var ancho := _fuente.get_string_size(VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
	_lienzo.draw_string(_fuente, tarjeta.end - Vector2(16 + ancho, 12), VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(PIEL.TINTA_APAGADA, 0.8 * alfa))


## La llama de la vela: una gota que se mece, con el corazón azulado y la punta blanca
func _dibujar_llama(alfa: float) -> void:
	if alfa <= 0.01:
		return
	var f := _parpadeo()
	var mece := sin(_tiempo * 2.3) * 1.2 + sin(_tiempo * 9.0) * 0.4
	var alto := 11.0 * f
	var base := LLAMA + Vector2(0, 4)
	var capas := [[4.0, 1.0, Color("e8742a")], [3.0, 0.82, Color("ffb347")], [2.0, 0.62, Color("ffe7a0")], [1.0, 0.4, Color("fffbe8")]]
	for c in capas:
		var ancho: float = c[0]
		var h: float = alto * c[1]
		var puntos := PackedVector2Array()
		for i in 12:
			var t := float(i) / 11.0
			var y := -t * h
			var x := sin(t * PI * 0.95 + 0.15) * ancho * (1.0 - t * 0.5) + mece * t * t
			puntos.append(base + Vector2(x, y))
		for i in range(11, -1, -1):
			var t := float(i) / 11.0
			puntos.append(base + Vector2(-sin(t * PI * 0.95 + 0.15) * ancho * (1.0 - t * 0.5) + mece * t * t, -t * h))
		_lienzo.draw_colored_polygon(puntos, Color(c[2], alfa))
	_lienzo.draw_rect(Rect2(base + Vector2(-1, -2), Vector2(2, 2)), Color(0.35, 0.45, 0.9, 0.6 * alfa))


func _dibujar_motas(alfa: float) -> void:
	if alfa <= 0.01:
		return
	for m in _motas:
		var vida: float = m["vida"] / m["dura"]
		var cerca := clampf(1.0 - m["pos"].distance_to(LLAMA) / 140.0, 0.0, 1.0)
		var brillo := sin(vida * PI) * (0.5 + 0.5 * sin(m["vida"] * 3.0 + m["fase"])) * cerca * alfa
		_lienzo.draw_rect(Rect2(m["pos"].round(), Vector2.ONE), Color(1.0, 0.86, 0.6, 0.8 * brillo))


## La luz de la vela, sumada: un halo que tiembla y un baño cálido sobre la mesa y el diario
func _dibujar_brillo() -> void:
	var abre := 0.0
	if _abriendo >= 0.0:
		abre = clampf((_abriendo - MENU_FUERA) / ABRIR_DURA, 0.0, 1.0)
	var f := _parpadeo() * (1.0 - _ease(abre * 1.6))
	if f <= 0.01:
		return
	var centro := LLAMA + Vector2(0, -2)
	for k in 6:
		_brillo.draw_circle(centro, 4.0 + k * k * 3.0, Color(1.0, 0.6, 0.25, 0.06 * f))
	for k in 4:
		_brillo.draw_circle(centro + Vector2(0, 50), 110.0 + k * 50.0, Color(0.5, 0.25, 0.08, 0.025 * f))


## La introducción, escrita a pluma en la primera página del diario, y una semilla que brota en la otra
func _dibujar_intro() -> void:
	var izq := PAG_IZQ
	var titulo := "Lo primero que recuerdo"
	_letra(titulo, izq.position + Vector2(22, 34), TINTA_ROJA)
	var ancho_t := _fuente.get_string_size(titulo, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
	PIEL.raya(_lienzo, izq.position + Vector2(20, 40), izq.position + Vector2(24 + ancho_t, 40), TINTA_ROJA, 0.7)
	var y := izq.position.y + 74
	var hechas := INTRO.size() if _intro == -2 else _intro
	for i in mini(hechas + 1, INTRO.size()):
		var linea: String = INTRO[i]
		if i == hechas:
			linea = linea.substr(0, int(_intro_tiempo * LETRAS_SEG))
		var alto: float = _escribir(linea, Vector2(izq.position.x + 22, y), izq.size.x - 44)
		y += alto + 14
	# el dibujo de la otra página: una semilla, y el brote que sale según avanza la introducción
	var avance := 1.0 if _intro == -2 else (float(_intro) + minf(1.0, _intro_tiempo / 1.6)) / INTRO.size()
	var s := PAG_DER.get_center() + Vector2(0, 62)
	# la tierra: unas rayas cortas a mano
	for k in 7:
		var x := -70.0 + k * 22.0
		PIEL.raya(_lienzo, s + Vector2(x, 16 + (k % 2) * 2), s + Vector2(x + 14, 16 + (k % 2) * 2), TINTA_SUAVE, 0.6)
	# la semilla, con su sombreado de rayitas
	var semilla := PackedVector2Array()
	for i in 21:
		var a := TAU * i / 20.0
		semilla.append(s + Vector2(cos(a) * 22.0, sin(a) * 13.0))
	_lienzo.draw_polyline(semilla, Color(TINTA_CLARA, 0.9), 2.0)
	for k in 5:
		var x := 2.0 + k * 3.5
		_lienzo.draw_line(s + Vector2(x, -10 + k * 1.5), s + Vector2(x - 6, 10 - k * 0.5), Color(TINTA_SUAVE, 0.6), 1.0)
	# las raíces, que bajan primero
	var raiz := clampf(avance / 0.35, 0.0, 1.0)
	for r: Vector2 in [Vector2(-14, 34), Vector2(2, 42), Vector2(16, 30)]:
		_trazo_tinta(s + Vector2(r.x * 0.3, 11), s + Vector2(r.x * 0.3, 11) + (r - Vector2(r.x * 0.3, 11)) * raiz, TINTA_SUAVE, 1.0)
	# el tallo y las dos primeras hojas
	if avance > 0.2:
		var tallo := clampf((avance - 0.2) / 0.45, 0.0, 1.0)
		var base := s + Vector2(0, -12)
		var punta := base + Vector2(sin(tallo * 2.0) * 6.0, -84.0 * tallo)
		var medio := base.lerp(punta, 0.5) + Vector2(-5 * tallo, 0)
		_trazo_tinta(base, medio, PIEL.VERDE, 2.0)
		_trazo_tinta(medio, punta, PIEL.VERDE, 2.0)
		if avance > 0.62:
			var hoja := clampf((avance - 0.62) / 0.3, 0.0, 1.0)
			for lado: float in [-1.0, 1.0]:
				var a := punta + Vector2(0, 4)
				var b := a + Vector2(lado * 32.0, -14.0) * hoja
				var arriba := a.lerp(b, 0.5) + Vector2(0, -9) * hoja
				var abajo := a.lerp(b, 0.5) + Vector2(0, 5) * hoja
				_lienzo.draw_colored_polygon(PackedVector2Array([a, arriba, b, abajo]), Color(PIEL.VERDE, 0.25 * hoja))
				_lienzo.draw_polyline(PackedVector2Array([a, arriba, b, abajo, a]), Color(PIEL.VERDE, 0.9), 1.5)
				_lienzo.draw_line(a, b, Color(PIEL.VERDE, 0.6), 1.0)
	if avance >= 1.0:
		var nota := "lo que encontré al despertar"
		var w := _fuente.get_string_size(nota, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		_letra(nota, Vector2(round(PAG_DER.get_center().x - w / 2.0), s.y + 62), TINTA_SUAVE)
	# la fecha, como en un diario
	_letra("día uno", PAG_DER.position + Vector2(PAG_DER.size.x - 70, 34), TINTA_SUAVE)


## Una raya de tinta gruesa entre dos puntos
func _trazo_tinta(a: Vector2, b: Vector2, color: Color, grosor: float) -> void:
	if a.distance_to(b) < 0.5:
		return
	_lienzo.draw_line(a.round(), b.round(), Color(color, 0.9), grosor)


## Escribe un texto en tinta, partiendo las líneas por palabras; devuelve lo que ocupa de alto
func _escribir(texto: String, pos: Vector2, ancho: float) -> float:
	var renglon := ""
	var y := pos.y
	for palabra in texto.split(" "):
		var prueba := palabra if renglon == "" else renglon + " " + palabra
		if renglon != "" and _fuente.get_string_size(prueba, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x > ancho:
			_letra(renglon, Vector2(pos.x, y), TINTA_CLARA)
			y += 20
			renglon = palabra
		else:
			renglon = prueba
	_letra(renglon, Vector2(pos.x, y), TINTA_CLARA)
	return y - pos.y + 20


## Letra clara con contorno oscuro (las páginas del diario son de cielo de noche: la tinta oscura no se vería)
func _letra(texto: String, pos: Vector2, color: Color) -> void:
	_lienzo.draw_string_outline(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, 4, Color(0.04, 0.02, 0.07, 0.95 * color.a))
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.7 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, color)


func _texto(texto: String, pos: Vector2, color: Color) -> void:
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.6 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, color)
