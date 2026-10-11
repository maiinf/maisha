extends StaticBody2D
## ROCA QUE SE APARTA: cierra un escondite hasta que se encienden todas las piedras-eco.

const TEXTURA := preload("res://arte/mundos/raiz/objetos/roca_grande.png")

var abierta := false
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("rocas_moviles")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.offset = Vector2(0, -7)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 8)
	_forma.shape = caja
	_forma.position = Vector2(0, -3)
	add_child(_forma)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)


func apartarse(al_instante := false) -> void:
	if abierta:
		return
	abierta = true
	_forma.set_deferred("disabled", true)
	if al_instante:
		_sprite.visible = false
		return
	# tiembla y se hunde en la tierra
	var t := create_tween()
	for i in 4:
		t.tween_property(_sprite, "position:x", 1.0 if i % 2 == 0 else -1.0, 0.05)
	t.tween_property(_sprite, "position", Vector2(0, 10), 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	t.parallel().tween_property(_sprite, "modulate:a", 0.0, 0.6)
