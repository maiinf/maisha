extends CanvasLayer
## BARRA DE UN JEFE: su nombre y su vida (un trozo por cada golpe que aguanta), arriba en el centro.
## Entra deslizándose, parpadea al perder un trozo y se va al vencerlo.

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PIEL := preload("res://scripts/interfaz/piel.gd")
const PANEL := Color(0.08, 0.07, 0.10, 0.88)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const GIZA := Color("a855d6")
const GIZA_OSCURO := Color("3a1650")
const ANCHO := 236.0

var nombre := ""
var maximo := 4
## La Ira del jefe (0..100, -1 = no tiene): una barrita debajo con su etapa (Calma, Enfado, Furia, Frenesí)
var ira := -1.0
const ETAPAS := ["Calma", "Enfado", "Furia", "Frenesí"]
const COLOR_IRA := [Color("8fd0c4"), Color("e6a852"), Color("de6771"), Color("ff3b4a")]
## Las partes que se le pueden romper (opcional): [{nombre, maximo, vida, oculta}] — una fila debajo con sus marcas
var partes: Array = []
var _destello_parte := {}
var _vida := 4
var _bajada := 0.0           # 0 = fuera de la pantalla, 1 = en su sitio
var _destello := 0.0
var _perdido := -1           # el trozo que se acaba de perder (parpadea)
var _lienzo: Control


func _ready() -> void:
	layer = 15
	add_to_group("barra_jefe")
	_vida = maximo
	_lienzo = Control.new()
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_lienzo)
	_lienzo.draw.connect(_dibujar)
	create_tween().tween_property(self, "_bajada", 1.0, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func poner(vida: int) -> void:
	_perdido = vida
	_vida = vida
	_destello = 0.6


func poner_parte(i: int, vida: int) -> void:
	if i >= 0 and i < partes.size():
		partes[i]["vida"] = vida
		_destello_parte[i] = 0.6


func mostrar_parte(i: int) -> void:
	if i >= 0 and i < partes.size():
		partes[i]["oculta"] = false
		_destello_parte[i] = 1.2


func cerrar() -> void:
	var t := create_tween()
	t.tween_property(self, "_bajada", 0.0, 0.5).set_delay(0.8)
	t.tween_callback(queue_free)


func _process(delta: float) -> void:
	_destello = maxf(0.0, _destello - delta)
	for i in _destello_parte:
		_destello_parte[i] = maxf(0.0, _destello_parte[i] - delta)
	_lienzo.queue_redraw()


func _dibujar() -> void:
	var y := -40.0 + 48.0 * _bajada
	var caja := Rect2((640.0 - ANCHO) / 2.0, y, ANCHO, 30.0 if ira < 0.0 else 35.0)
	PIEL.caja(_lienzo, caja.grow(2), "cuero")
	var ancho_nombre := FUENTE.get_string_size(nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
	_lienzo.draw_string(FUENTE, Vector2(320.0 - ancho_nombre / 2.0, y + 13).round(), nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, TEXTO)
	# un trozo de raíz por cada punto de vida
	var hueco := 3.0
	var tam := (ANCHO - 24.0 - hueco * (maximo - 1)) / maximo
	for i in maximo:
		var r := Rect2(caja.position.x + 12.0 + i * (tam + hueco), y + 18, tam, 6).abs()
		r.position = r.position.round()
		_lienzo.draw_rect(r, Color("1a0d24"))
		if i < _vida:
			_lienzo.draw_rect(r.grow(-1), GIZA_OSCURO)
			_lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(r.size.x - 2, 2)), GIZA)
		elif i == _perdido and _destello > 0.0 and int(_destello * 12.0) % 2 == 0:
			_lienzo.draw_rect(r.grow(-1), TEXTO)
	if ira >= 0.0:
		var etapa := mini(3, int(ira / 25.0))
		var barra := Rect2(caja.position.x + 12.0, y + 27, ANCHO - 24.0, 3)
		_lienzo.draw_rect(barra, Color("1a0d24"))
		var col: Color = COLOR_IRA[etapa]
		if etapa == 3 and int(Time.get_ticks_msec() / 120) % 2 == 0:
			col = TEXTO
		_lienzo.draw_rect(Rect2(barra.position, Vector2(floorf(barra.size.x * clampf(ira / 100.0, 0.0, 1.0)), 3)), col)
		for k in range(1, 4):
			_lienzo.draw_rect(Rect2(barra.position + Vector2(roundf(barra.size.x * k / 4.0), 0), Vector2(1, 3)), PANEL)
		# la etapa, a la derecha de la caja (con su panel)
		var texto: String = ETAPAS[etapa]
		var ancho_t := FUENTE.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var pt := Vector2(caja.end.x + 10.0, y + 22).round()
		PIEL.caja(_lienzo, Rect2(pt + Vector2(-7, -16), Vector2(ancho_t + 14, 23)), "cuero", 1.0, false)
		_lienzo.draw_rect(Rect2(pt + Vector2(-5, -14), Vector2(ancho_t + 10, 19)).grow(-1), col, false, 1.0)
		_lienzo.draw_string(FUENTE, pt + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.7))
		_lienzo.draw_string(FUENTE, pt, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, COLOR_IRA[etapa])
	if not partes.is_empty():
		_dibujar_partes(caja.end.y + 3.0)


## Una fila con las partes: su nombre y una marca por golpe que aguantan (tachadas si están rotas)
func _dibujar_partes(y: float) -> void:
	var trozos: Array = []
	var total := 0.0
	for i in partes.size():
		var p: Dictionary = partes[i]
		if p["oculta"]:
			continue
		var ancho_n := FUENTE.get_string_size(p["nombre"], HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var ancho: float = ancho_n + 4.0 + p["maximo"] * 5.0
		trozos.append([i, ancho_n, ancho])
		total += ancho + 12.0
	total -= 12.0
	var caja := Rect2(roundf(320.0 - total / 2.0 - 8.0), y, total + 16.0, 19.0)
	PIEL.caja(_lienzo, caja.grow(2), "cuero")
	var x := caja.position.x + 8.0
	for t in trozos:
		var p: Dictionary = partes[t[0]]
		var rota: bool = p["vida"] <= 0
		var brilla: bool = _destello_parte.get(t[0], 0.0) > 0.0 and int(_destello_parte[t[0]] * 12.0) % 2 == 0
		var col := TEXTO if not rota else Color(0.5, 0.45, 0.5)
		if brilla:
			col = Color("fde27e")
		_lienzo.draw_string(FUENTE, Vector2(x, y + 14).round(), p["nombre"], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, col)
		if rota:
			_lienzo.draw_rect(Rect2(Vector2(x - 1, y + 9).round(), Vector2(t[1] + 2, 1)), Color("de6771"))
		for k in p["maximo"]:
			var r := Rect2(Vector2(x + t[1] + 4.0 + k * 5.0, y + 6).round(), Vector2(4, 7))
			_lienzo.draw_rect(r, Color("1a0d24"))
			if k < p["vida"]:
				_lienzo.draw_rect(r.grow(-1), GIZA if p["nombre"] != "Corazón" else Color("ef8a26"))
		x += t[2] + 12.0
