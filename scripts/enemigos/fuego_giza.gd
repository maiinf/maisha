extends Node2D
## FUEGO DE GIZA: el rastro que deja la Cosechadora al acelerar. Llamas violetas por abajo y naranjas por arriba,
## casilla a casilla, que se apagan solas al cabo de unos segundos. Quema a Maisha si las pisa.
## En Frenesí, el fuego se extiende: algunas llamas prenden la casilla de al lado.
##   encender(casilla, segundos, extender)   prende una casilla
##   apagar_todo()                           (al vencer a la Cosechadora o al reiniciar la pelea)

const R := preload("res://scripts/combate/reglas_combate.gd")
const BASE := [Color("2a0d3a"), Color("6b2a8f"), Color("a855d6")]
const LLAMA := [Color("b8420f"), Color("ef8a26"), Color("f9b947"), Color("fde27e"), Color("fff8d2")]

var _llamas: Dictionary = {}        # casilla (Vector2i) -> {t, dura, fase, extender}
var _brasas: Array[Dictionary] = []
var _tiempo := 0.0
var _desde_quemadura := 0.0
var _azar := RandomNumberGenerator.new()


func _ready() -> void:
	add_to_group("fuego_giza")
	top_level = true
	z_index = 1
	_azar.seed = 77


func encender(casilla: Vector2i, segundos: float, extender := false) -> void:
	if _llamas.has(casilla):
		_llamas[casilla]["dura"] = maxf(_llamas[casilla]["dura"], _llamas[casilla]["t"] + segundos)
		return
	_llamas[casilla] = {"t": 0.0, "dura": segundos, "fase": _azar.randf() * TAU, "extender": extender}


func hay_fuego(casilla: Vector2i) -> bool:
	return _llamas.has(casilla) and _llamas[casilla]["t"] > 0.12 and _llamas[casilla]["t"] < _llamas[casilla]["dura"] - 0.3


func cuantas() -> int:
	return _llamas.size()


func apagar_todo() -> void:
	for c in _llamas:
		_llamas[c]["dura"] = minf(_llamas[c]["dura"], _llamas[c]["t"] + 0.6)


func _process(delta: float) -> void:
	_tiempo += delta
	_desde_quemadura += delta
	var nuevas: Array[Vector2i] = []
	for c in _llamas.keys():
		var l: Dictionary = _llamas[c]
		l["t"] += delta
		# Frenesí: el fuego se extiende a la casilla de arriba o de abajo (una sola vez)
		if l["extender"] and l["t"] > 0.6:
			l["extender"] = false
			if _azar.randf() < 0.35:
				nuevas.append(c + (Vector2i.UP if _azar.randf() < 0.5 else Vector2i.DOWN))
		if l["t"] >= l["dura"]:
			_llamas.erase(c)
		elif _azar.randf() < delta * 6.0:
			_brasas.append({"p": R.centro_de(c) + Vector2(_azar.randf_range(-6, 6), _azar.randf_range(-4, 4)),
				"v": Vector2(_azar.randf_range(-6, 6), _azar.randf_range(-30, -14)), "t": 0.0, "dura": _azar.randf_range(0.6, 1.2)})
	for c in nuevas:
		var zona := get_tree().get_first_node_in_group("arena_jefe")
		if zona == null or zona.distancia_normal(R.centro_de(c)) < 0.85:
			encender(c, 3.5)
	for b in _brasas:
		b["t"] += delta
		b["p"] += b["v"] * delta
	_brasas = _brasas.filter(func(b: Dictionary) -> bool: return b["t"] < b["dura"])
	# quema a Maisha si pisa una llama
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and _desde_quemadura > 0.5:
		var c := R.casilla_de(maisha.global_position)
		if hay_fuego(c):
			_desde_quemadura = 0.0
			if maisha.call("recibir_danio", 1, R.centro_de(c) + Vector2(0, -2), "fuego"):
				Sonido.efecto("fuego_quema", 0.0, maisha.global_position)
	queue_redraw()


func _draw() -> void:
	for c in _llamas:
		var l: Dictionary = _llamas[c]
		var nace: float = clampf(l["t"] / 0.15, 0.0, 1.0)
		var muere: float = clampf((l["dura"] - l["t"]) / 0.8, 0.0, 1.0)
		var vida := nace * muere
		var centro: Vector2 = R.centro_de(c) + Vector2(0, 4)
		var fase: float = l["fase"]
		# suelo chamuscado, resplandor y la base violeta (el fuego de Giza)
		draw_circle(centro + Vector2(0, 1), 9.0, Color(0.06, 0.02, 0.04, 0.45 * nace))
		draw_circle(centro + Vector2(0, -4), 16.0 * vida, Color(1.0, 0.42, 0.12, 0.10 * vida))
		draw_circle(centro + Vector2(0, -4), 10.0 * vida, Color(1.0, 0.55, 0.2, 0.14 * vida))
		draw_rect(Rect2(centro + Vector2(-8, -1), Vector2(16, 3)), Color(BASE[0], 0.8 * vida))
		draw_rect(Rect2(centro + Vector2(-7, -2), Vector2(14, 2)), Color(BASE[1], 0.9 * vida))
		# cuatro lenguas de fuego que bailan (naranja por fuera, amarilla por dentro, violeta en la raíz)
		for k in 4:
			var x := -6.0 + k * 4.0
			var alto := (12.0 + 7.0 * sin(_tiempo * (8.0 + k * 2.3) + fase + k * 1.7)) * vida * (0.8 if k % 3 == 0 else 1.0)
			var ancho := 3.0 if k % 3 else 2.2
			var vaiven := sin(_tiempo * 6.5 + fase + k) * 2.0
			var punta := centro + Vector2(x + vaiven, -alto - 2.0)
			var pie_i := centro + Vector2(x - ancho, -1)
			var pie_d := centro + Vector2(x + ancho, -1)
			var cintura := centro + Vector2(x + vaiven * 0.4, -alto * 0.45 - 1.0)
			draw_colored_polygon(PackedVector2Array([pie_i.round(), (cintura + Vector2(-ancho * 0.8, 0)).round(), punta.round(),
				(cintura + Vector2(ancho * 0.8, 0)).round(), pie_d.round()]), Color(LLAMA[0], 0.95 * vida))
			var medio := centro + Vector2(x + vaiven * 0.7, -alto * 0.75 - 1.0)
			draw_colored_polygon(PackedVector2Array([(pie_i + Vector2(0.8, 0)).round(), medio.round(), (pie_d - Vector2(0.8, 0)).round()]),
				Color(LLAMA[1], 0.95 * vida))
			var nucleo := centro + Vector2(x + vaiven * 0.4, -alto * 0.45 - 1.0)
			draw_colored_polygon(PackedVector2Array([(pie_i + Vector2(1.6, 0)).round(), nucleo.round(), (pie_d - Vector2(1.6, 0)).round()]),
				Color(LLAMA[3], 0.95 * vida))
			draw_rect(Rect2((centro + Vector2(x - 0.5, -2)).round(), Vector2(1, 1)), Color(BASE[2], vida))
			# una chispa violeta en la punta, de vez en cuando
			if sin(_tiempo * 11.0 + fase * 3.0 + k) > 0.7:
				draw_rect(Rect2((punta + Vector2(0, -2)).round(), Vector2(1, 1)), Color(BASE[2], vida))
	for b in _brasas:
		var f: float = b["t"] / b["dura"]
		var col: Color = LLAMA[4] if f < 0.3 else (LLAMA[2] if f < 0.7 else BASE[2])
		draw_rect(Rect2(b["p"].round(), Vector2.ONE), Color(col, 1.0 - f))
