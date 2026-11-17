extends Node2D
## LA CARGA SÍSMICA (arte Tierra, Asterhaul): la onda de ámbar que va por delante de Maisha mientras embiste
## (personajes/maisha.gd → carga()). Dura DURA s y va pegada a ella.
##   - Lo que es «sismicos» y queda delante (a ALCANCE px + su `radio_carga`) recibe `recibir_carga(direccion)`, una
##     sola vez: muros agrietados, vagonetas, pilares-diapasón, los Kaa-Jiwe... Si devuelve true, Maisha se para en seco.
##   - A los demás enemigos («daniables») que pille delante les quita 1 (tipo «carga»).

const DURA := 0.4
const ALCANCE := 14.0
const ONDA_R := 40.0
const AMBAR := [Color("fff4c8"), Color("ffd878"), Color("f8b040"), Color("d8841c")]

var maisha: Node2D
var direccion := Vector2.RIGHT
var _t := 0.0
var _tocados := {}
var _polvo: Array[Dictionary] = []
var _devolvio := false
var _onda := -1.0                       # (Tierra 6: la onda de ámbar del final; −1: aún no)


func _ready() -> void:
	z_index = 2
	Sonido.efecto("carga_sismica", 0.0, maisha.global_position if maisha else global_position, 0.08)
	if maisha:
		global_position = maisha.global_position


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA and _onda < 0.0 and Artes.valor("carga_onda") > 0.0 and is_instance_valid(maisha):
		_soltar_onda()
	if (_t >= DURA and (_onda < 0.0 or _onda >= ONDA_R)) or not is_instance_valid(maisha):
		queue_free()
		return
	if _onda >= 0.0:
		_onda += 200.0 * delta
		queue_redraw()
		return
	global_position = maisha.global_position
	if _t < 0.3:
		_polvo.append({"p": Vector2(randf_range(-5, 5), randf_range(-2, 2)) - direccion * 6.0, "t": 0.0})
		_embestir()
	for g in _polvo:
		g["t"] += delta
		g["p"] -= direccion * 20.0 * delta
	queue_redraw()


func _embestir() -> void:
	var frente := maisha.global_position + direccion * 10.0 + Vector2(0, -6)
	for nodo in get_tree().get_nodes_in_group("sismicos"):
		var o := nodo as Node2D
		if o == null or _tocados.has(o.get_instance_id()):
			continue
		var radio: float = ALCANCE * (1.0 + Artes.valor("tierra_alcance")) + float(o.get("radio_carga") if o.get("radio_carga") != null else 0.0)
		if (o.global_position + Vector2(0, -6)).distance_to(frente) > radio:
			continue
		_tocados[o.get_instance_id()] = true
		if o.call("recibir_carga", direccion):
			maisha.call("frenar_carga")
			if not _devolvio and Artes.valor("carga_devuelve") > 0.0:          # (Tierra 4: los guantes de imán)
				_devolvio = true
				maisha.set("aliento", minf(maisha.call("aliento_maximo"), float(maisha.get("aliento")) + Artes.valor("carga_devuelve")))
			Impacto.temblar(2.5, 0.18)
			Impacto.chispa(frente + direccion * 6.0, direccion, AMBAR[1], 1.15, "carga")
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var o := nodo as Node2D
		if o == null or o.is_in_group("maisha") or o.is_in_group("sismicos") or _tocados.has(o.get_instance_id()):
			continue
		if (o.global_position + Vector2(0, -6)).distance_to(frente) <= ALCANCE + 4.0:
			_tocados[o.get_instance_id()] = true
			o.call("recibir_danio", 1 + int(Artes.valor("carga_danio")), maisha.global_position, "carga")
			Impacto.chispa(o.global_position + Vector2(0, -8), direccion, AMBAR[1], 1.1, "carga")


## Tierra 6: una onda de ámbar alrededor de Maisha (1 a los enemigos que no ha tocado ya la Carga)
func _soltar_onda() -> void:
	_onda = 4.0
	Sonido.efecto("diapason_ambar", -4.0, global_position, 0.1)
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var o := nodo as Node2D
		if o and not o.is_in_group("maisha") and not _tocados.has(o.get_instance_id()) and o.global_position.distance_to(global_position) <= ONDA_R + 6.0:
			o.call("recibir_danio", 1, global_position, "carga")
			Impacto.chispa(o.global_position + Vector2(0, -8), Vector2.UP, AMBAR[1])


func _draw() -> void:
	if _onda >= 0.0:
		var f := _onda / ONDA_R
		draw_set_transform(Vector2(0, -2), 0.0, Vector2(1.0, 0.6))
		draw_arc(Vector2.ZERO, _onda, 0, TAU, 32, Color(AMBAR[1], 1.0 - f), 2.5)
		draw_arc(Vector2.ZERO, _onda * 0.8, 0, TAU, 32, Color(AMBAR[0], 0.6 * (1.0 - f)), 1.0)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		return
	var vida := 1.0 - _t / DURA
	var centro := direccion * 6.0 + Vector2(0, -8)
	var a := direccion.angle()
	# tres arcos de ámbar que se abren por delante
	for k in 3:
		var r := 10.0 + k * 6.0 + _t * 40.0
		draw_arc(centro, r, a - 0.9 + k * 0.12, a + 0.9 - k * 0.12, 12, Color(AMBAR[k], vida * (0.9 - k * 0.2)), 2.0 - k * 0.5)
	# el polvo que deja atrás
	for g in _polvo:
		var v: float = 1.0 - float(g["t"]) / 0.4
		if v > 0.0:
			draw_circle((g["p"] as Vector2) + Vector2(0, -float(g["t"]) * 10.0), 1.0 + (1.0 - v) * 2.5, Color(0.83, 0.66, 0.45, 0.45 * v))
