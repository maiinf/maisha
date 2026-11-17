extends Node2D
## LA RESONANCIA DE ÁMBAR (arte Tierra, Asterhaul): la nota que suelta Maisha (personajes/maisha.gd → resonancia()).
## Un anillo de ámbar que se abre hasta ALCANCE px: los MONOLITOS-DIAPASÓN («monolitos») que alcanza empiezan a
## cantar con toda su fuerza (asterhaul/monolito.gd → resonar(3)). No hace nada más: el resto lo hacen ellos.

const DURA := 0.5
const ALCANCE := 104.0
const AMBAR := [Color("fff4c8"), Color("ffd878"), Color("f8b040")]

var _t := 0.0


func _ready() -> void:
	z_index = 2
	Sonido.efecto("resonancia_ambar", 0.0, global_position, 0.05)
	for nodo in get_tree().get_nodes_in_group("monolitos"):
		if (nodo as Node2D).global_position.distance_to(global_position) <= ALCANCE * (1.0 + Artes.valor("tierra_alcance")):
			nodo.call("resonar", 3)


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
	queue_redraw()


func _draw() -> void:
	var f := _t / DURA
	draw_set_transform(Vector2(0, -4), 0.0, Vector2(1.0, 0.62))      # (aplastado: va por el suelo)
	for k in 3:
		var r := ALCANCE * clampf(f * 1.15 - k * 0.14, 0.0, 1.0)
		if r > 2.0:
			draw_arc(Vector2.ZERO, r, 0, TAU, 40, Color(AMBAR[k], (1.0 - f) * (0.9 - k * 0.2)), 2.0 - k * 0.5)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# la nota: tres rayitas que suben del cetro
	for k in 3:
		var x := (k - 1) * 5.0
		draw_line(Vector2(x, -22.0 - f * 10.0), Vector2(x, -27.0 - f * 14.0 - k * 2.0), Color(AMBAR[0], 1.0 - f), 1.0)
