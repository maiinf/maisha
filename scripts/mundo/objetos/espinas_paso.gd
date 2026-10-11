extends Node2D
## ESPINAS DE GIZA QUE TAPAN UN PASO (letra «!» del mapa): ramas de piedra con pinchos y luz violeta.
## No tienen colisión propia: lo que no deja pasar es la puerta cerrada que guardan.
## Cuando se pone su marca, se marchitan y se hunden en la tierra.

@export var marca := ""

var _sprite: Sprite2D
var _tiempo := 0.0
var _secas := false


func _ready() -> void:
	if marca != "" and Estado.tiene(marca):
		queue_free()
		return
	_tiempo = position.x * 0.13
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/raiz/espinas.png")
	_sprite.hframes = 4
	_sprite.frame = 3
	_sprite.offset = Vector2(0, -9)
	_sprite.scale = Vector2(1.6, 1.6)
	_sprite.flip_h = int(position.x / 16.0) % 2 == 0
	add_child(_sprite)
	Estado.marca_puesta.connect(_al_poner_marca)


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()


func _draw() -> void:
	if _secas:
		return
	var pulso := 0.5 + 0.5 * sin(_tiempo * 2.0)
	draw_circle(Vector2(0, -8), 10.0, Color(0.6, 0.3, 0.8, 0.06 + 0.05 * pulso))


func _al_poner_marca(m: String) -> void:
	if m != marca or _secas:
		return
	_secas = true
	Sonido.efecto("piedra_rompe", 0.0, global_position)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "modulate", Color(0.5, 0.45, 0.4, 0.0), 1.4).set_delay(randf() * 0.4)
	t.tween_property(_sprite, "scale:y", 0.2, 1.4)
	t.chain().tween_callback(queue_free)
