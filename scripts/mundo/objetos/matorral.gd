extends StaticBody2D
## MATORRAL: estorba el paso hasta que una semilla lo hace estallar.
## A veces esconde un secreto detrás.

const TEXTURA := preload("res://arte/mundos/raiz/objetos/matorral.png")

var roto := false
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("daniables")
	add_to_group("matorrales")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -6)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 8)
	_forma.shape = caja
	_forma.position = Vector2(0, -3)
	add_child(_forma)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if roto or tipo != "explosion":
		return
	roto = true
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	remove_from_group("daniables")
	# sacudida al romperse
	var t := create_tween()
	t.tween_property(_sprite, "position:x", 2.0, 0.04)
	t.tween_property(_sprite, "position:x", -2.0, 0.06)
	t.tween_property(_sprite, "position:x", 0.0, 0.04)
