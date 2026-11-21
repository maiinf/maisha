extends StaticBody2D
## UN PILAR DORADO DE LA PASARELA DE LOS TRES PESOS (El Horizonte Inmóvil): se enciende (`marca`) cuando se cumple su
## prueba (`prueba`: una función que devuelve true; la pone la escena) y ya no se apaga.
## Dibujo: arte/mundos/ocaso/horizonte/pilar.png (0 apagado · 1 encendido).

signal encendido

const DIBUJO := preload("res://arte/mundos/ocaso/horizonte/pilar.png")

var marca := ""
var prueba: Callable
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("pilares_dorados")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -20)
	_sprite.frame = 1 if lleno() else 0
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func lleno() -> bool:
	return Estado.tiene(marca)


func _process(_delta: float) -> void:
	if lleno() or not prueba.is_valid() or not prueba.call():
		return
	Estado.marcar(marca)
	_sprite.frame = 1
	Sonido.efecto("pilar_enciende", 0.0, global_position)
	Impacto.chispa(global_position + Vector2(0, -40), Vector2.UP, Color(1.0, 0.85, 0.5))
	encendido.emit()
