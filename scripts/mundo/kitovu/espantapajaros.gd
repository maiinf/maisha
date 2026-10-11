extends StaticBody2D
## ESPANTAPÁJAROS: para probar el golpe del cetro. Se balancea al recibirlo.

signal golpeado(veces: int)

const TEXTURA := preload("res://arte/mundos/kitovu/espantapajaros.png")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")

var veces := 0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("espantapajaros")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 6.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.centered = false
	_sprite.offset = Vector2(-9, -31)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(6, 4)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)


func recibir_golpe(_danio: int, direccion: Vector2) -> bool:
	veces += 1
	Sonido.efecto("espantapajaros_golpe")
	golpeado.emit(veces)
	var lado := 1.0 if direccion.x >= 0.0 else -1.0
	var t := create_tween()
	t.tween_property(_sprite, "rotation", 0.25 * lado, 0.06)
	t.tween_property(_sprite, "rotation", -0.15 * lado, 0.12)
	t.tween_property(_sprite, "rotation", 0.0, 0.15)
	return false
