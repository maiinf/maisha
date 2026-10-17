extends Node2D
## EL SIGILO DE FUEGO (arte Runa, Sigilia): Maisha traza en el aire, delante de ella, una runa de fuego.
##   - 0 → 0,25 s: la runa se dibuja trazo a trazo (líneas doradas).
##   - a los 0,25 s ARDE: un círculo de llamas de RADIO px que enciende los faroles rúnicos («faroles_runicos» →
##     encender_runa), lo que se puede encender («encendibles» → encender, p. ej. los braseros), derrite lo que es de
##     Tinta Quieta o de hielo («derretibles» → derretir) y quema a los enemigos («daniables», 1 de daño, tipo «fuego»).
##   - después las llamas se apagan y suben chispas.

const RADIO := 20.0
const RADIO_TINTA_VIVA := 30.0     # con la tinta viva de Wino, arde más lejos
const TRAZA := 0.25
const DURA := 0.95
const LLAMA := [Color("fff4c0"), Color("ffc860"), Color("ff8a2a"), Color("c84a14")]
## la runa (trazos en coordenadas de -1 a 1): un tronco, dos brazos que suben y un punto arriba
const TRAZOS := [[Vector2(0, 1), Vector2(0, -0.8)], [Vector2(-0.7, -0.1), Vector2(0, 0.35), Vector2(0.7, -0.1)],
	[Vector2(-0.45, 0.75), Vector2(0.45, 0.75)]]

var radio := RADIO
var _t := 0.0
var _ardio := false
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	z_index = 2
	radio = RADIO_TINTA_VIVA if Estado.tiene("tinta_viva") else RADIO
	Sonido.efecto("pluma", -4.0, global_position, 0.1)


func _process(delta: float) -> void:
	_t += delta
	if _t >= TRAZA and not _ardio:
		_ardio = true
		_arder()
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
		c["v"].y -= 20.0 * delta
	if _t >= DURA:
		queue_free()
	queue_redraw()


func _arder() -> void:
	Sonido.efecto("fuego_quema", 0.0, global_position)
	var centro := global_position
	for nodo in get_tree().get_nodes_in_group("faroles_runicos"):
		if (nodo as Node2D).global_position.distance_to(centro) <= radio + 10.0:
			nodo.call("encender_runa")
	for nodo in get_tree().get_nodes_in_group("encendibles"):
		if (nodo as Node2D).global_position.distance_to(centro) <= radio + 8.0:
			nodo.call("encender")
	for nodo in get_tree().get_nodes_in_group("derretibles"):
		if (nodo as Node2D).global_position.distance_to(centro) <= radio + 10.0:
			nodo.call("derretir")
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var o := nodo as Node2D
		if o and o.global_position.distance_to(centro) <= radio + 4.0:
			o.call("recibir_danio", 1, centro, "fuego")
	for i in 18:
		var a := randf() * TAU
		_chispas.append({"p": Vector2(cos(a), sin(a)) * randf_range(4, radio), "v": Vector2(randf_range(-14, 14), randf_range(-50, -20)), "t": 0.0})
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position, Color("ff9a40"), 0.7, 0.8, 0.35)


func _draw() -> void:
	var escala := 7.0
	# la runa: se dibuja trazo a trazo y luego brilla hasta apagarse
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
			# (con su borde oscuro, para que se vea también sobre la nieve)
			draw_line(a, hasta, Color(0.45, 0.12, 0.05, 0.85 * vida), 4.0)
			draw_line(a, hasta, Color(1.0, 0.55, 0.15, vida), 2.0)
			draw_line(a, hasta, Color(1.0, 0.95, 0.6, vida), 1.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(0.45, 0.12, 0.05, 0.7 * vida), 3.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(1.0, 0.7, 0.25, vida), 1.0)
	# el círculo de llamas al arder: lenguas de píxeles alrededor que suben y se apagan
	if _ardio:
		var f := 1.0 - clampf((_t - TRAZA) / 0.5, 0.0, 1.0)
		for k in 14:
			var ang := k * TAU / 14.0
			var base := Vector2(cos(ang), sin(ang) * 0.6) * radio * (0.6 + 0.4 * (1.0 - f))
			var alto := (5.0 + 3.0 * sin(_t * 30.0 + k)) * f
			for i in int(alto):
				var t := float(i) / maxf(alto, 1.0)
				var col: Color = LLAMA[clampi(int(t * 3.2), 0, 3)]
				var p := (base + Vector2(sin(_t * 20.0 + i + k) * t, -i)).floor()
				if i == 0:
					draw_rect(Rect2(p + Vector2(-1, 1), Vector2(4, 1)), Color(0.45, 0.12, 0.05, f))      # la brasa, oscura
				draw_rect(Rect2(p, Vector2(2, 1)), Color(col, f * (1.0 - t * 0.4)))
	for c in _chispas:
		var v: float = 1.0 - c["t"] / 0.7
		if v > 0.0:
			draw_rect(Rect2((c["p"] as Vector2).floor(), Vector2.ONE), Color(1.0, 0.55, 0.15, v))
