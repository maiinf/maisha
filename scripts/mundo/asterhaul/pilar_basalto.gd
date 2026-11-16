extends StaticBody2D
## UN PILAR DE BASALTO de la Cámara del Ancla Oeste (las Galerías de Ámbar): macizo, no se atraviesa. Si el Kifaru
## se estampa contra él embistiendo, se parte (queda un muñón que ya no para a nadie) y al Kifaru se le abre la coraza.
## Dibujo: arte/mundos/asterhaul/galerias/pilar.png, 0 entero · 1 roto.

const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/pilar.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

var roto := false
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("pilares_basalto")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -26)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(20, 10)
	_forma.shape = caja
	_forma.position = Vector2(0, -4)
	add_child(_forma)


func romper() -> void:
	if roto:
		return
	roto = true
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	Sonido.efecto("roca_romper", 0.0, global_position)
	for k in 2:
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 10
		astillas.position = global_position + Vector2((k * 2 - 1) * 8, -20)
		get_parent().add_child(astillas)
