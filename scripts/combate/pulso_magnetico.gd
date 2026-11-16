extends Node2D
## EL PULSO MAGNÉTICO (arte Tierra, Asterhaul): los anillos azules que salen de Maisha al pulsar (personajes/maisha.gd
## → pulso()). Solo se ve: lo que hace cada cosa lo decide su `recibir_pulso()`.

const DURA := 0.55
const RADIO := 120.0
const AZUL := [Color("c0f4ff"), Color("6ad0f0"), Color("2e9ac0")]

var _t := 0.0


func _ready() -> void:
	z_index = 2
	Sonido.efecto("pulso_magnetico", 0.0, global_position, 0.08)
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position + Vector2(0, -8), Color("6ad0f0"), 0.8, 0.9, 0.3)


func _process(delta: float) -> void:
	_t += delta
	if _t >= DURA:
		queue_free()
	queue_redraw()


func _draw() -> void:
	var f := _t / DURA
	# tres anillos que se abren (aplastados: están en el suelo) y unas rayitas que vuelven hacia Maisha
	for k in 3:
		var r := RADIO * clampf(f * 1.2 - k * 0.16, 0.0, 1.0)
		if r > 2.0:
			draw_set_transform(Vector2(0, -4), 0.0, Vector2(1.0, 0.62))
			draw_arc(Vector2.ZERO, r, 0, TAU, 40, Color(AZUL[k], (1.0 - f) * (0.9 - k * 0.2)), 2.0 - k * 0.5)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	for k in 10:
		var a := k * TAU / 10.0 + 0.3
		var dentro := RADIO * (1.0 - f) * 0.9
		var d := Vector2(cos(a), sin(a) * 0.62)
		draw_line(d * dentro + Vector2(0, -4), d * (dentro + 7.0) + Vector2(0, -4), Color(AZUL[0], 0.7 * (1.0 - f)), 1.0)
