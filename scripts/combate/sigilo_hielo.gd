extends Node2D
## EL SIGILO DE HIELO (arte Runa, Sigilia; lo enseña Mfereji en el Canal de Tinta): una runa de escarcha delante.
##   - 0 → 0,25 s: la runa se dibuja trazo a trazo (líneas azul claro).
##   - a los 0,25 s HIELA: un círculo de RADIO px que congela lo que se deja («congelables» → congelar, p. ej. Ruba)
##     (congelar devuelve true si lo atrapa) y, si no, sobre tinta líquida («~») la endurece en una PLACA DE TINTA
##     HELADA (sigilia/placa_hielo.gd) que flota.
##   - después suben copos.

const PLACA := preload("res://scripts/mundo/sigilia/placa_hielo.gd")
const RADIO := 20.0
const TRAZA := 0.25
const DURA := 0.95
const HIELO := [Color("f4fbff"), Color("bfe6f5"), Color("7fc2e6"), Color("3c78a8")]
## la runa: un rombo partido y tres puntas que salen, como un copo
const TRAZOS := [[Vector2(0, -1), Vector2(0.65, 0), Vector2(0, 1), Vector2(-0.65, 0), Vector2(0, -1)],
	[Vector2(0, -1), Vector2(0, 1)], [Vector2(-0.95, -0.55), Vector2(0.95, 0.55)], [Vector2(-0.95, 0.55), Vector2(0.95, -0.55)]]

var _t := 0.0
var _helo := false
var _copos: Array[Dictionary] = []


func _ready() -> void:
	z_index = 2
	Sonido.efecto("pluma", -4.0, global_position, 0.1)


func _process(delta: float) -> void:
	_t += delta
	if _t >= TRAZA and not _helo:
		_helo = true
		_helar()
	for c in _copos:
		c["t"] += delta
		c["p"] += c["v"] * delta
	if _t >= DURA:
		queue_free()
	queue_redraw()


func _helar() -> void:
	Sonido.efecto("hielo_runa", 0.0, global_position)
	var centro := global_position + Vector2(0, 6)      # (la runa va a la altura del pecho; el hielo, en el suelo)
	var atrapo := false
	for nodo in get_tree().get_nodes_in_group("congelables"):
		if (nodo as Node2D).global_position.distance_to(centro) <= RADIO + 10.0:
			atrapo = bool(nodo.call("congelar")) or atrapo
	# (si ha atrapado algo en el hielo, ese témpano ya es el suyo: no hace además una placa)
	if not atrapo:
		PLACA.helar_en(get_parent(), centro)
	for i in 16:
		var a := randf() * TAU
		_copos.append({"p": Vector2(cos(a), sin(a) * 0.6) * randf_range(4, RADIO), "v": Vector2(randf_range(-8, 8), randf_range(-26, -10)), "t": 0.0})
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position, Color("9fd8f0"), 0.7, 0.8, 0.35)


func _draw() -> void:
	var escala := 7.0
	var avance := clampf(_t / TRAZA, 0.0, 1.0)
	var vida := 1.0 - clampf((_t - TRAZA) / (DURA - TRAZA), 0.0, 1.0)
	var total := TRAZOS.size()
	for k in total:
		var tramo: Array = TRAZOS[k]
		var cuanto := clampf(avance * total - k, 0.0, 1.0)
		if cuanto <= 0.0:
			continue
		for i in tramo.size() - 1:
			var a: Vector2 = tramo[i] * escala
			var b: Vector2 = tramo[i + 1] * escala
			var hasta := a.lerp(b, cuanto)
			draw_line(a, hasta, Color(0.1, 0.2, 0.35, 0.85 * vida), 4.0)
			draw_line(a, hasta, Color(0.5, 0.8, 0.95, vida), 2.0)
			draw_line(a, hasta, Color(0.95, 1.0, 1.0, vida), 1.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(0.1, 0.2, 0.35, 0.7 * vida), 3.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(0.7, 0.9, 1.0, vida), 1.0)
	# al helar: un anillo de escarcha que se abre en el suelo, con cristales de píxeles
	if _helo:
		var f := 1.0 - clampf((_t - TRAZA) / 0.5, 0.0, 1.0)
		for k in 16:
			var ang := k * TAU / 16.0
			var base := Vector2(cos(ang), sin(ang) * 0.6) * RADIO * (0.5 + 0.5 * (1.0 - f)) + Vector2(0, 6)
			var col: Color = HIELO[k % 4]
			draw_rect(Rect2(base.floor() + Vector2(-1, 0), Vector2(3, 1)), Color(col, f))
			draw_rect(Rect2(base.floor() + Vector2(0, -1), Vector2(1, 3)), Color(col, f))
	for c in _copos:
		var v: float = 1.0 - c["t"] / 0.8
		if v > 0.0:
			draw_rect(Rect2((c["p"] as Vector2).floor(), Vector2.ONE), Color(0.9, 0.97, 1.0, v))
