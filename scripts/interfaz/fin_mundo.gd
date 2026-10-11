extends CanvasLayer
## FIN DE UN MUNDO: la pantalla que sale al liberar Raíz (tras el narrador de la Cosechadora).
## La ilustración del final, Maisha celebrándolo, hojas doradas que caen y lo conseguido en el mundo,
## que va apareciendo línea a línea (con su cuenta). Suena «Raíz respira». Acción para seguir jugando.

signal cerrado

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const ILUSTRACION := preload("res://arte/historia/11_cosecha_libre.png")
const ANIMACIONES := preload("res://arte/personajes/maisha/maisha_animaciones.tres")
const PANEL := Color(0.08, 0.07, 0.10, 0.9)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const VERDE := Color("8fd06a")
const MAPAS := ["kitovu", "prados_del_eco", "bosque_cobrizo", "cienaga_quieta", "campo_segado"]
const ALDEANOS := ["pino", "corteza", "tawi", "juncia"]
const COLORES_HOJA := [Color("e6a852"), Color("f1c27a"), Color("c68756"), Color("8fd06a"), Color("fff3c4")]

var abierto := false
var _lienzo: Control
var _fuente: FontFile
var _t := 0.0
var _alfa := 0.0
var _lineas: Array = []           # [texto, valor, total o -1]
var _hojas: Array[Dictionary] = []
var _maisha: AnimatedSprite2D
var _ultima_vista := -1


func _ready() -> void:
	add_to_group("fin_mundo")
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	# Maisha celebrando, al doble de tamaño, delante de todo
	_maisha = AnimatedSprite2D.new()
	_maisha.sprite_frames = ANIMACIONES
	_maisha.scale = Vector2(3, 3)
	_maisha.position = Vector2(320, 262)
	_maisha.modulate.a = 0.0
	add_child(_maisha)
	visible = false


func abrir() -> void:
	abierto = true
	visible = true
	_t = 0.0
	_alfa = 0.0
	_lineas = _calcular()
	get_tree().paused = true
	Sonido.musica("raiz_libre", 1.5)
	if _maisha.sprite_frames.has_animation("celebrar_abajo"):
		_maisha.play("celebrar_abajo")


func _calcular() -> Array:
	var zonas := 0
	var zonas_total := 0
	var secretos := 0
	var secretos_total := 0
	for mapa in MAPAS:
		var datos: Dictionary = (load("res://datos/mapas/%s.json" % mapa) as JSON).data
		zonas_total += datos.get("zonas", {}).size()
		for fila in datos.get("filas", []):
			secretos_total += String(fila).count("X")
	for m in Estado.marcas:
		var marca := String(m)
		for mapa in MAPAS:
			if marca.begins_with("zona/%s/" % mapa):
				zonas += 1
			if marca.begins_with("secreto/%s/" % mapa):
				secretos += 1
	var aldeanos := ALDEANOS.filter(func(a: String) -> bool: return Estado.tiene("rescatado_" + a)).size()
	var misiones := Misiones.hechas().size()
	var misiones_total := Misiones.hechas().size() + Misiones.activas().size()
	return [
		["Tiempo de juego", -1, -1, Estado.texto_tiempo(Estado.tiempo_jugado)],
		["Zonas purgadas", zonas, zonas_total, ""],
		["Aldeanos de vuelta", aldeanos, ALDEANOS.size(), ""],
		["Secretos", secretos, secretos_total, ""],
		["Misiones cumplidas", misiones, misiones_total, ""],
		["Esencia", Artes.esencia_ganada_total(), -1, ""],
		["Cristales del Nexo", Tienda.cristales_ganados_total(), -1, ""],
	]


func cerrar() -> void:
	if not abierto:
		return
	abierto = false
	Sonido.efecto("menu_aceptar")
	var t := create_tween()
	t.tween_property(self, "_alfa", 0.0, 0.8)
	t.parallel().tween_property(_maisha, "modulate:a", 0.0, 0.5)
	await t.finished
	visible = false
	get_tree().paused = false
	get_tree().set_meta("menu_cerrado_en", Engine.get_process_frames())
	var escena := get_tree().current_scene
	if escena and escena.has_method("volver_a_su_musica"):
		escena.call("volver_a_su_musica")
	cerrado.emit()
	queue_free()


## Cuántas líneas se ven ya (salen una a una)
func lineas_vistas() -> int:
	return clampi(int((_t - 2.2) / 0.55), 0, _lineas.size())


func _process(delta: float) -> void:
	if not abierto:
		return
	_t += delta
	_alfa = minf(1.0, _alfa + delta * 0.8)
	_maisha.modulate.a = clampf((_t - 1.2) / 0.6, 0.0, 1.0)
	var vistas := lineas_vistas()
	if vistas != _ultima_vista:
		if vistas > 0:
			Sonido.efecto("mision_paso")
		_ultima_vista = vistas
	# hojas y pétalos dorados que caen
	if _hojas.size() < 60 and randf() < delta * 30.0:
		_hojas.append({"p": Vector2(randf() * 680 - 20, -8), "v": randf_range(18, 40), "f": randf() * TAU,
			"c": COLORES_HOJA[randi() % COLORES_HOJA.size()], "g": randf_range(2.0, 5.0)})
	for h in _hojas:
		h["p"] += Vector2(sin(_t * 1.3 + h["f"]) * 18.0 + 6.0, h["v"]) * delta
	_hojas = _hojas.filter(func(h: Dictionary) -> bool: return h["p"].y < 370)
	_lienzo.queue_redraw()


func _input(evento: InputEvent) -> void:
	if not abierto or evento.is_echo():
		return
	if evento.is_action_pressed("accion") or evento.is_action_pressed("menu"):
		get_viewport().set_input_as_handled()
		if _t > 3.0:
			cerrar()


func _texto(texto: String, pos: Vector2, color: Color, tam := 16) -> void:
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(0, 0, 0, 0.7 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, color)


func _ancho(texto: String, tam := 16) -> float:
	return _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x


func _dibujar() -> void:
	var a := _alfa
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.06, 0.04, 0.03, a))
	# la ilustración, arriba, que se acerca muy despacio
	var zoom := 1.0 + minf(_t, 30.0) * 0.002
	var tam := Vector2(600, 256) * zoom
	_lienzo.draw_texture_rect(ILUSTRACION, Rect2(Vector2(320, 128) - tam / 2.0, tam), false, Color(1, 1, 1, a * 0.9))
	_lienzo.draw_rect(Rect2(0, 200, 640, 160), Color(0.06, 0.04, 0.03, a * 0.55))
	# el título
	var ta := clampf((_t - 0.6) / 0.8, 0.0, 1.0) * a
	var titulo := "Raíz es libre"
	var tam_t := 32
	_texto(titulo, Vector2(320 - _ancho(titulo, tam_t) / 2.0, 44).round(), Color(TEXTO, ta), tam_t)
	var sub := "Fin del primer mundo"
	_texto(sub, Vector2(320 - _ancho(sub) / 2.0, 66).round(), Color(AMBAR, ta))
	# lo conseguido, en dos columnas a los lados de Maisha
	var vistas := lineas_vistas()
	for i in vistas:
		var l: Array = _lineas[i]
		var col := 0 if i < 4 else 1
		var fila := i if i < 4 else i - 4
		var x := 32.0 if col == 0 else 374.0
		var y := 236.0 + fila * 26.0
		var caja := Rect2(x - 8, y - 16, 242, 22)
		var aparece := clampf((_t - 2.2 - i * 0.55) / 0.3, 0.0, 1.0)
		_lienzo.draw_rect(caja, Color(PANEL, PANEL.a * a * aparece))
		_lienzo.draw_rect(caja.grow(-1), Color(FILO, 0.6 * a * aparece), false, 1.0)
		_texto(String(l[0]), Vector2(x, y), Color(APAGADO, a * aparece))
		var valor := String(l[3])
		if valor == "":
			var cuenta := int(round(float(l[1]) * aparece))
			valor = str(cuenta) if int(l[2]) < 0 else "%d/%d" % [cuenta, int(l[2])]
		var completo := int(l[2]) >= 0 and int(l[1]) >= int(l[2])
		_texto(valor, Vector2(caja.end.x - 8 - _ancho(valor), y), Color(VERDE if completo else TEXTO, a * aparece))
	if _t > 3.0 and vistas >= _lineas.size():
		var pie := "Continuará en Sigilia...   ·   Acción para seguir"
		var pa := (0.6 + 0.4 * sin(_t * 3.0)) * a
		_texto(pie, Vector2(320 - _ancho(pie) / 2.0, 350).round(), Color(APAGADO, pa))
	# hojas que caen por delante
	for h in _hojas:
		var p: Vector2 = h["p"].round()
		var giro := int(_t * h["g"] + h["f"] * 3.0) % 3
		var forma: Vector2 = [Vector2(3, 2), Vector2(2, 2), Vector2(2, 3)][giro]
		_lienzo.draw_rect(Rect2(p, forma), Color(h["c"], 0.85 * a))
