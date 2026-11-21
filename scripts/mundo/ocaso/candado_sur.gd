extends StaticBody2D
## EL CANDADO DEL SUR (El Horizonte Inmóvil): cierra la Cadena del Sur de Jua-Giza. Solo se le puede dar cuando
## brilla (`brilla`, lo pone Jua-Giza entre ola y ola): cada golpe de cetro lo afloja (`golpeado`).
## Dibujo: arte/mundos/ocaso/horizonte/candado.png (0 cerrado · 1 brilla).

signal golpeado

const DIBUJO := preload("res://arte/mundos/ocaso/horizonte/candado.png")

var brilla := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("golpeables")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -16)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(22, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func _process(_delta: float) -> void:
	_sprite.frame = 1 if brilla else 0


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if not brilla:
		Sonido.efecto("clinc", -2.0, global_position, 0.2)
		return false
	Sonido.efecto("candado_golpe", 0.0, global_position)
	Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color("ffd878"))
	golpeado.emit()
	return true
