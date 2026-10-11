extends Sprite2D
## PLANTA QUE SE MECE: un adorno de 2 fotogramas (trigo...) que cambia con el viento.
## Cada mata lleva su propio desfase para que el campo se mueva como una ola.

@export var velocidad := 1.6
var desfase := 0.0
var _tiempo := 0.0


func _ready() -> void:
	hframes = 2
	centered = false
	offset = Vector2(-texture.get_width() / 4, -texture.get_height() + 1)


func _process(delta: float) -> void:
	_tiempo += delta
	frame = 1 if sin(_tiempo * velocidad + desfase) > 0.0 else 0
