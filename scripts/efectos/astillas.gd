extends Node2D
## ASTILLAS: trocitos de piedra (y alguna chispa violeta de Giza) que saltan al romperse algo.
## Uso: var a := ASTILLAS.new(); a.cantidad = 8; a.position = ...; padre.add_child(a)

const COLORES := [Color("525649"), Color("7a806d"), Color("a0a596"), Color("292c25")]
const CHISPA := Color("a855d6")

@export var cantidad := 8
@export var fuerza := 70.0
@export var chispas := 3
@export var dura := 0.7
@export var colores: Array = COLORES

var _trozos: Array[Dictionary] = []
var _vida := 0.0


func _ready() -> void:
	z_index = 2
	for i in cantidad + chispas:
		var a := randf_range(-PI * 0.95, -PI * 0.05)        # hacia arriba, abriéndose a los lados
		var v := Vector2(cos(a), sin(a)) * randf_range(0.4, 1.0) * fuerza
		var es_chispa := i >= cantidad
		_trozos.append({
			"p": Vector2(randf_range(-4, 4), randf_range(-8, 0)),
			"v": v * (1.3 if es_chispa else 1.0),
			"suelo": randf_range(2.0, 7.0),
			"tam": 1.0 if es_chispa else float(randi_range(1, 2)),
			"color": CHISPA if es_chispa else colores[randi() % colores.size()],
			"chispa": es_chispa,
		})


func _process(delta: float) -> void:
	_vida += delta
	if _vida >= dura:
		queue_free()
		return
	for t in _trozos:
		if t["chispa"]:
			t["v"] *= 0.92
			t["p"] += t["v"] * delta
		elif t["p"].y < t["suelo"]:
			t["v"].y += 300.0 * delta
			t["p"] += t["v"] * delta
		else:
			t["p"].y = t["suelo"]                                  # se queda en el suelo un momento
	queue_redraw()


func _draw() -> void:
	var alfa := clampf((dura - _vida) / 0.25, 0.0, 1.0)
	for t in _trozos:
		var c: Color = t["color"]
		draw_rect(Rect2(Vector2(t["p"]).round(), Vector2.ONE * t["tam"]), Color(c, alfa))
