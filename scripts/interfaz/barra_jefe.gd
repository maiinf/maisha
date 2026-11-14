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
var _cola_vida := 4.0        # rastro animado del daño reciente en la barra de cristales
var _pausa_cola := 0.0
var _bajada := 0.0           # 0 = fuera de la pantalla, 1 = en su sitio
var _destello := 0.0
var _sacudida := 0.0         # vibración horizontal al encajar golpe o perder una parte
var _perdido := -1           # el trozo que se acaba de perder (parpadea)
var _lienzo: Control


func _ready() -> void:
	layer = 15
	add_to_group("barra_jefe")
	_vida = maximo
	_cola_vida = float(maximo)
	_lienzo = Control.new()
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_lienzo)
	_lienzo.draw.connect(_dibujar)
	create_tween().tween_property(self, "_bajada", 1.0, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func poner(vida: int) -> void:
	if vida < _vida:
		_cola_vida = maxf(_cola_vida, float(_vida))
		_pausa_cola = 0.16
		_sacudida = 1.0
	else:
		_cola_vida = float(vida)
	_perdido = vida
	_vida = vida
	_destello = 0.6


func poner_parte(i: int, vida: int) -> void:
	if i >= 0 and i < partes.size():
		if vida < int(partes[i].get("vida", 0)):
			_sacudida = maxf(_sacudida, 0.75)
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
	_sacudida = maxf(0.0, _sacudida - delta * 4.5)
	if _pausa_cola > 0.0:
		_pausa_cola = maxf(0.0, _pausa_cola - delta)
	else:
		_cola_vida = move_toward(_cola_vida, float(_vida), delta * 1.9)
	for i in _destello_parte:
		_destello_parte[i] = maxf(0.0, _destello_parte[i] - delta)
	_lienzo.queue_redraw()


func _dibujar() -> void:
	var sx := roundf(sin(Time.get_ticks_msec() * 0.08) * 2.5 * _sacudida) if _sacudida > 0.01 else 0.0
	var y := -44.0 + 52.0 * _bajada
	var caja := Rect2((640.0 - ANCHO) / 2.0 + sx, y, ANCHO, 32.0 if ira < 0.0 else 40.0)
	var etapa := mini(3, int(ira / 25.0)) if ira >= 0.0 else -1
	var col_borde: Color = GIZA if etapa < 2 else (COLOR_IRA[etapa] as Color)
	var pulso := 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.008)
	PIEL.caja(_lienzo, caja.grow(2), "noche")
	if etapa >= 2:
		_lienzo.draw_rect(caja.grow(3), Color(col_borde, 0.16 + 0.18 * pulso), false, 2.0)
	PIEL.esquinas_oro(_lienzo, caja.grow(2), col_borde, 0.92, 7.0)
	var ancho_nombre := FUENTE.get_string_size(nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
	if ira >= 0.0:
		var t_etapa: String = ETAPAS[etapa]
		var w_etapa := FUENTE.get_string_size(t_etapa, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 10.0
		var nx := roundf(caja.position.x + 12.0)
		_lienzo.draw_string(FUENTE, Vector2(nx + 1, y + 15).round(), nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.75))
		_lienzo.draw_string(FUENTE, Vector2(nx, y + 14).round(), nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, TEXTO)
		PIEL.insignia(_lienzo, Vector2(caja.end.x - 10.0 - w_etapa, y + 2.0), t_etapa, FUENTE, Color(0.14, 0.08, 0.16), COLOR_IRA[etapa], COLOR_IRA[etapa], 0.96, 16, 5.0)
	else:
		var cx := roundf(caja.position.x + caja.size.x * 0.5)
		var tx := roundf(cx - ancho_nombre * 0.5)
		_dibujar_rombo(Vector2(tx - 8.0, y + 9.0), Color(GIZA, 0.9))
		_dibujar_rombo(Vector2(tx + ancho_nombre + 8.0, y + 9.0), Color(GIZA, 0.9))
		_lienzo.draw_string(FUENTE, Vector2(tx + 1, y + 15).round(), nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.75))
		_lienzo.draw_string(FUENTE, Vector2(tx, y + 14).round(), nombre, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, TEXTO)
	# Cristales biselados de Giza por cada golpe que aguanta, con estela dorada de daño
	var hueco := 3.0
	var tam := (ANCHO - 26.0 - hueco * (maximo - 1)) / maximo
	for i in maximo:
		var r := Rect2(caja.position.x + 13.0 + i * (tam + hueco), y + 19, tam, 7).abs()
		r.position = r.position.round()
		_lienzo.draw_rect(r, Color(0.06, 0.04, 0.10, 0.96))
		_lienzo.draw_rect(r, Color(PIEL.ORO, 0.42 if i < _vida else 0.22), false, 1.0)
		var inner := r.grow(-1)
		if i < _vida:
			var critico := _vida == 1
			var col_gem := GIZA.lerp(Color("f3b8ff"), 0.25 * pulso) if critico else GIZA
			_lienzo.draw_rect(inner, col_gem)
			_lienzo.draw_rect(Rect2(inner.position, Vector2(inner.size.x, 1.0)), col_gem.lightened(0.42))
			_lienzo.draw_rect(Rect2(inner.position, Vector2(2.0, inner.size.y - 1.0)), col_gem.lightened(0.25))
			_lienzo.draw_rect(Rect2(inner.position.x, inner.end.y - 1.0, inner.size.x, 1.0), GIZA_OSCURO)
			if inner.size.x >= 8.0:
				_lienzo.draw_rect(Rect2(inner.position + Vector2(3, 1), Vector2(4, 1)), Color(1.0, 0.95, 1.0, 0.55))
		else:
			var frac_cola := clampf(_cola_vida - float(i), 0.0, 1.0)
			if frac_cola > 0.02:
				var rw := maxf(1.0, roundf(inner.size.x * frac_cola))
				_lienzo.draw_rect(Rect2(inner.position, Vector2(rw, inner.size.y)), Color("f4df9a", 0.9))
			if i == _perdido and _destello > 0.0 and int(_destello * 14.0) % 2 == 0:
				_lienzo.draw_rect(inner, Color(1.0, 0.97, 0.85, 0.95))
	if ira >= 0.0:
		var barra := Rect2(caja.position.x + 13.0, y + 30, ANCHO - 26.0, 5)
		var col: Color = COLOR_IRA[etapa]
		if etapa == 3 and int(Time.get_ticks_msec() / 120) % 2 == 0:
			col = TEXTO
		PIEL.medidor(_lienzo, barra, clampf(ira / 100.0, 0.0, 1.0), col, -1.0, Color.WHITE, 1.0, 4)
	if not partes.is_empty():
		_dibujar_partes(caja.end.y + 4.0, sx)


## Pequeño cristal ornamental flanqueando el nombre del jefe
func _dibujar_rombo(c: Vector2, col: Color) -> void:
	var p := c.round()
	_lienzo.draw_colored_polygon(PackedVector2Array([
		p + Vector2(0, -3), p + Vector2(3, 0), p + Vector2(0, 3), p + Vector2(-3, 0)
	]), col)
	_lienzo.draw_rect(Rect2(p - Vector2(1, 1), Vector2(1, 1)), TEXTO)


## Una fila con las partes: su nombre y una marca por golpe que aguantan (tachadas si están rotas)
func _dibujar_partes(y: float, sx := 0.0) -> void:
	var trozos: Array = []
	var total := 0.0
	for i in partes.size():
		var p: Dictionary = partes[i]
		if p["oculta"]:
			continue
		var ancho_n := FUENTE.get_string_size(p["nombre"], HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var ancho: float = ancho_n + 4.0 + p["maximo"] * 6.0
		trozos.append([i, ancho_n, ancho])
		total += ancho + 12.0
	if trozos.is_empty():
		return
	total -= 12.0
	var caja := Rect2(roundf(320.0 - total / 2.0 - 8.0 + sx), y, total + 16.0, 19.0)
	PIEL.caja(_lienzo, caja.grow(2), "cuero")
	PIEL.esquinas_oro(_lienzo, caja.grow(2), PIEL.ORO, 0.55, 4.0)
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
			var r := Rect2(Vector2(x + t[1] + 4.0 + k * 6.0, y + 6).round(), Vector2(5, 7))
			_lienzo.draw_rect(r, Color("140a1e"))
			_lienzo.draw_rect(r, Color(PIEL.ORO, 0.35), false, 1.0)
			if k < p["vida"]:
				var col_p := GIZA if p["nombre"] != "Corazón" else Color("ef8a26")
				_lienzo.draw_rect(r.grow(-1), col_p)
				_lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(3, 1)), col_p.lightened(0.35))
		x += t[2] + 12.0
