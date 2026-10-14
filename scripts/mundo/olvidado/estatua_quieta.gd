extends StaticBody2D
## ESTATUA del Sendero Olvidado: alguien de Raíz que se quedó quieto para no perder algo, y Giza lo volvió piedra.
## 0 la liebre abrazada a su gavilla · 1 el tejón con el farol apagado · 2 la garza con las alas abiertas.
## Al mirarla (Acción) Maisha entiende qué quería guardar (conversación «estatua_olvidado_<n>»).

const DIBUJO := preload("res://arte/mundos/raiz/olvidado/estatua.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")

@export var cual := 0
@export var radio_interaccion := 26.0
@export var altura_bocadillo := 44.0

var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("estatuas_olvidado")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 12.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.frame = cual
	_sprite.centered = false
	_sprite.offset = Vector2(-15, -39)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(20, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func interactuar() -> void:
	await CHARLA.hablar(self, "estatua_olvidado_%d" % cual)
