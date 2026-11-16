extends StaticBody2D
## UNA REJA de mina (Asterhaul): cierra un paso por el que cruza la vía. Se abre (y se queda abierta) con su
## `marca`. Cerrada, corta la vía (está en «topes_via»).
## Dibujo: arte/mundos/asterhaul/galerias/reja.png, 0 cerrada · 1 abierta.

const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/reja.png")

@export var marca := ""
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("topes_via")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -16)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 20)
	_forma.shape = caja
	_forma.position = Vector2(0, -6)
	add_child(_forma)
	Estado.marca_puesta.connect(func(m: String) -> void:
		if m == marca:
			_abrir(true))
	if Estado.tiene(marca):
		_abrir(false)


func es_tope() -> bool:
	return _sprite.frame == 0


func _abrir(con_sonido: bool) -> void:
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	if con_sonido:
		Sonido.efecto("rueda_abrir", 0.0, global_position)
