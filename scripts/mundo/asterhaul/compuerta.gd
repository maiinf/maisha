extends StaticBody2D
## UNA COMPUERTA DE CRISOL (Asterhaul, la Fundición): una hoja de hierro que cierra un paso de tres casillas de
## alto. Se abre (y se queda abierta) con su `marca`.
## Dibujo: arte/mundos/asterhaul/fundicion/compuerta.png, 0 cerrada · 1 abierta.

const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/compuerta.png")

@export var marca := ""
var abierta := false
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("compuertas")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -26)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 50)
	_forma.shape = caja
	_forma.position = Vector2(0, -22)
	add_child(_forma)
	Estado.marca_puesta.connect(func(m: String) -> void:
		if m == marca:
			_abrir(true))
	if Estado.tiene(marca):
		_abrir(false)


func _abrir(con_sonido: bool) -> void:
	abierta = true
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	if con_sonido:
		Sonido.efecto("rueda_abrir", 2.0, global_position)
		Impacto.temblar(2.0, 0.3)
