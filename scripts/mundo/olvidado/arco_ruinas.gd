extends Node2D
## EL ARCO DE LAS RUINAS, al final del Sendero Olvidado: dos pilares rotos de piedra clara, abrazados por raíces del
## Primer Árbol, con las nueve espirales de los ecos talladas. Entre los pilares, una NIEBLA que se mueve sola
## (dibujada aquí: un dibujo no puede tener bordes de humo). La puerta de verdad es la «^» de debajo.

const DIBUJO := preload("res://arte/mundos/raiz/olvidado/arco_ruinas.png")

var _tiempo := 0.0
var _niebla: Node2D


func _ready() -> void:
	var s := Sprite2D.new()
	s.texture = DIBUJO
	s.centered = false
	s.offset = Vector2(-56, -86)
	add_child(s)
	# los pilares chocan (el paso, entre ellos, queda libre)
	for x in [-34.0, 34.0]:
		var cuerpo := StaticBody2D.new()
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(18, 8)
		forma.shape = caja
		cuerpo.position = Vector2(x, -4)
		cuerpo.add_child(forma)
		add_child(cuerpo)
	_niebla = Node2D.new()
	_niebla.z_index = 1
	_niebla.draw.connect(_dibujar_niebla)
	add_child(_niebla)


func _process(delta: float) -> void:
	_tiempo += delta
	_niebla.queue_redraw()


## Bancos de niebla que suben y se deshilachan entre los pilares
func _dibujar_niebla() -> void:
	for i in 18:
		var fase := _tiempo * (0.25 + (i % 5) * 0.04) + i * 1.7
		var x := -22.0 + fmod(i * 13.0 + sin(fase) * 6.0, 44.0)
		var y := -6.0 - fmod(_tiempo * 4.0 + i * 9.0, 60.0)
		var alto_t: float = -y / 60.0
		var r := 7.0 + (i % 3) * 3.0
		_niebla.draw_circle(Vector2(x, y), r, Color(0.86, 0.9, 0.96, 0.16 * (1.0 - alto_t)))
	_niebla.draw_rect(Rect2(-24, -14, 48, 14), Color(0.88, 0.92, 0.97, 0.22))
