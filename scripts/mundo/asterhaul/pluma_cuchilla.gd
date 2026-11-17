extends Node2D
## UNA PLUMA-CUCHILLA de Kipanga, clavada en el suelo (Asterhaul, la Aguja Caída): zumba. Mientras está, ENMUDECE a
## los monolitos que tenga cerca (asterhaul/monolito.gd la busca en «plumas_cuchilla»). Un golpe de cetro la parte.
## Si nadie la rompe, se deshace sola a los DURA s.
## Dibujo: arte/mundos/asterhaul/aguja/pluma.png.

const DIBUJO := preload("res://arte/mundos/asterhaul/aguja/pluma.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DURA := 14.0

var _t := 0.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("plumas_cuchilla")
	add_to_group("golpeables")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	Sonido.efecto("kipanga_pluma", -4.0, global_position, 0.2)


func _process(delta: float) -> void:
	_t += delta
	_sprite.position.x = roundf(sin(_t * 46.0) * 0.6)                 # zumba
	_sprite.modulate.a = 1.0 if _t < DURA - 2.0 or int(_t * 8.0) % 2 == 0 else 0.4
	queue_redraw()
	if _t >= DURA:
		queue_free()


func _draw() -> void:
	# el zumbido: dos anillitos que suben
	for k in 2:
		var f := fmod(_t * 1.4 + k * 0.5, 1.0)
		draw_arc(Vector2(0, -14.0 - f * 8.0), 4.0 + f * 5.0, PI * 1.1, PI * 1.9, 8, Color(0.42, 0.82, 0.94, 0.7 * (1.0 - f)), 1.0)


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	romper()
	return true


func romper() -> void:
	remove_from_group("plumas_cuchilla")
	remove_from_group("golpeables")
	Sonido.efecto("clinc", 0.0, global_position, 0.3)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 6
	astillas.position = global_position + Vector2(0, -10)
	get_parent().add_child(astillas)
	queue_free()
