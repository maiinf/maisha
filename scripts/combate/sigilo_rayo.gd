extends Node2D
## EL SIGILO DE RAYO (arte Runa, Sigilia; lo enseña Nyota en el Observatorio de la Aurora): una runa en zigzag delante.
##   - 0 → 0,25 s: la runa se dibuja trazo a trazo (líneas amarillo claro).
##   - a los 0,25 s DESCARGA: un círculo de RADIO px que carga lo que se deja cargar («cargables» → cargar: las
##     bobinas y diapasones astrales, Saa el autómata) y da un calambre a los enemigos («daniables», 1, tipo «rayo»).
##   - después saltan chispas.

const RADIO := 22.0
const TRAZA := 0.25
const DURA := 0.95
const RAYO := [Color("ffffff"), Color("fff6b0"), Color("ffd84a"), Color("7fd6ff")]
## la runa: un rayo en zigzag con una raya arriba y otra abajo
const TRAZOS := [[Vector2(0.45, -1), Vector2(-0.45, -0.1), Vector2(0.4, 0.05), Vector2(-0.4, 1)],
	[Vector2(-0.7, -1), Vector2(0.7, -1)], [Vector2(-0.7, 1), Vector2(0.7, 1)]]

var _t := 0.0
var _descargo := false
var _chispas: Array[Dictionary] = []
var _arcos: Array[PackedVector2Array] = []


func _ready() -> void:
	z_index = 2
	Sonido.efecto("pluma", -4.0, global_position, 0.1)


func _process(delta: float) -> void:
	_t += delta
	if _t >= TRAZA and not _descargo:
		_descargo = true
		_descargar()
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
	if _t >= DURA:
		queue_free()
	queue_redraw()


func _descargar() -> void:
	Sonido.efecto("chispa", 2.0, global_position, 0.15)
	var centro := global_position + Vector2(0, 6)
	for nodo in get_tree().get_nodes_in_group("cargables"):
		if (nodo as Node2D).global_position.distance_to(centro) <= RADIO + 12.0:
			nodo.call("cargar")
			_arcos.append(_arco(Vector2(0, 6), (nodo as Node2D).global_position + Vector2(0, -14) - global_position))
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var o := nodo as Node2D
		if o and not o.is_in_group("cargables") and not o.is_in_group("maisha") and o.global_position.distance_to(centro) <= RADIO + 4.0:
			o.call("recibir_danio", 1, centro, "rayo")
	for i in 5:
		var a := randf() * TAU
		_arcos.append(_arco(Vector2(0, 6), Vector2(cos(a), sin(a) * 0.6) * RADIO + Vector2(0, 6)))
	for i in 14:
		var a := randf() * TAU
		_chispas.append({"p": Vector2(cos(a), sin(a) * 0.6) * randf_range(4, RADIO), "v": Vector2(randf_range(-40, 40), randf_range(-50, 10)), "t": 0.0})
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position, Color("fff0a0"), 0.9, 0.9, 0.3)


## Un rayo quebrado de `a` a `b`
func _arco(a: Vector2, b: Vector2) -> PackedVector2Array:
	var puntos := PackedVector2Array([a])
	var lado := (b - a).orthogonal().normalized()
	for k in range(1, 5):
		puntos.append((a.lerp(b, k / 5.0) + lado * randf_range(-5.0, 5.0)).round())
	puntos.append(b)
	return puntos


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
		# (cada trazo se dibuja entero hasta donde llega el avance, tramo a tramo)
		var hecho := cuanto * (tramo.size() - 1)
		for i in tramo.size() - 1:
			var parte := clampf(hecho - i, 0.0, 1.0)
			if parte <= 0.0:
				break
			var a: Vector2 = tramo[i] * escala
			var hasta := a.lerp(tramo[i + 1] * escala, parte)
			draw_line(a, hasta, Color(0.3, 0.2, 0.05, 0.85 * vida), 4.0)
			draw_line(a, hasta, Color(1.0, 0.85, 0.3, vida), 2.0)
			draw_line(a, hasta, Color(1.0, 1.0, 0.85, vida), 1.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(0.3, 0.2, 0.05, 0.7 * vida), 3.0)
	draw_arc(Vector2.ZERO, escala + 3.0, -PI / 2, -PI / 2 + TAU * avance, 24, Color(1.0, 0.92, 0.5, vida), 1.0)
	# al descargar: rayos quebrados que saltan (parpadean) y chispas
	if _descargo:
		var f := 1.0 - clampf((_t - TRAZA) / 0.35, 0.0, 1.0)
		if f > 0.0 and int(_t * 40.0) % 2 == 0:
			for arco in _arcos:
				draw_polyline(arco, Color(0.5, 0.84, 1.0, f * 0.8), 3.0)
				draw_polyline(arco, Color(1.0, 1.0, 0.9, f), 1.0)
	for c in _chispas:
		var v: float = 1.0 - c["t"] / 0.6
		if v > 0.0:
			draw_rect(Rect2((c["p"] as Vector2).floor(), Vector2.ONE), Color(RAYO[int(c["t"] * 20.0) % 4], v))
