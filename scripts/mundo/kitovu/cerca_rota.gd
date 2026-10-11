extends StaticBody2D
## EL HUECO DE LA CERCA del huerto: con unas tablas, se arregla.

const TEXTURA := preload("res://arte/mundos/kitovu/cerca.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")

@export var radio_interaccion := 22.0
@export var altura_bocadillo := 20.0

var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("cercas")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-16, -15)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 4)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	_sprite.frame = 1 if Estado.tiene("cerca_arreglada") else 0


func interactuar() -> void:
	if Estado.tiene("cerca_arreglada"):
		await CHARLA.hablar(self, "kitovu_cerca_bien")
	elif Estado.quitar("tablas"):
		Sonido.efecto("cerca_martillo")
		get_tree().create_timer(1.2).timeout.connect(Sonido.efecto.bind("cerca_arreglada"))
		Estado.marcar("cerca_arreglada")
		var t := create_tween()
		for i in 4:
			t.tween_property(_sprite, "position:y", -1.0 if i % 2 == 0 else 0.0, 0.07)
		t.tween_callback(func() -> void: _sprite.frame = 1)
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("¡Cerca arreglada! Vuelve con Mzee Shamba")
	else:
		await CHARLA.hablar(self, "kitovu_cerca_rota")
