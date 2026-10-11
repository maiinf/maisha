extends Sprite2D
## Destello de una casilla de la explosión (5 fotogramas). Se borra solo al terminar.

const TEXTURA := preload("res://arte/efectos/explosion.png")
const SEGUNDOS_POR_FOTOGRAMA := 0.06

var _tiempo := 0.0


func _ready() -> void:
	texture = TEXTURA
	hframes = 5
	offset = Vector2(0, -8)   # el nodo está en la base de la casilla, para ordenarse bien en profundidad


func _process(delta: float) -> void:
	_tiempo += delta
	var f := int(_tiempo / SEGUNDOS_POR_FOTOGRAMA)
	if f >= hframes:
		queue_free()
	else:
		frame = f
