extends Node2D
## LA CARGA SÍSMICA (arte Tierra, Asterhaul): la onda de ámbar que va por delante de Maisha mientras embiste
## (personajes/maisha.gd → carga()). Dura DURA s y va pegada a ella.
##   - Lo que es «sismicos» y queda delante (a ALCANCE px + su `radio_carga`) recibe `recibir_carga(direccion)`, una
##     sola vez: muros agrietados, vagonetas, pilares-diapasón, los Kaa-Jiwe... Si devuelve true, Maisha se para en seco.
##   - A los demás enemigos («daniables») que pille delante les quita 1 (tipo «carga»).

const DURA := 0.4
const ALCANCE := 14.0
const AMBAR := [Color("fff4c8"), Color("ffd878"), Color("f8b040"), Color("d8841c")]

var maisha: Node2D
var direccion := Vector2.RIGHT
var _t := 0.0
var _tocados := {}
var _polvo: Array[Dictionary] = []


func _ready() -> void:
	z_index = 2
	Sonido.efecto("carga_sismica", 0.0, maisha.global_position if maisha else global_position, 0.08)
	if maisha:
		global_position = maisha.global_position


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA or not is_instance_valid(maisha):
		queue_free()
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
		var radio: float = ALCANCE + float(o.get("radio_carga") if o.get("radio_carga") != null else 0.0)
		if (o.global_position + Vector2(0, -6)).distance_to(frente) > radio:
			continue
		_tocados[o.get_instance_id()] = true
		if o.call("recibir_carga", direccion):
			maisha.call("frenar_carga")
			Impacto.temblar(2.5, 0.18)
			Impacto.chispa(frente + direccion * 6.0, direccion, AMBAR[1])
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var o := nodo as Node2D
		if o == null or o.is_in_group("maisha") or o.is_in_group("sismicos") or _tocados.has(o.get_instance_id()):
			continue
		if (o.global_position + Vector2(0, -6)).distance_to(frente) <= ALCANCE + 4.0:
			_tocados[o.get_instance_id()] = true
			o.call("recibir_danio", 1, maisha.global_position, "carga")
			Impacto.chispa(o.global_position + Vector2(0, -8), direccion, AMBAR[1])


func _draw() -> void:
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
