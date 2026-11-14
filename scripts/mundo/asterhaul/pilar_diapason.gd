extends StaticBody2D
## UN PILAR-DIAPASÓN (Asterhaul, la Puerta del Cráter): una columna de basalto con una horquilla de hierro
## meteórico. Dormido, no suena. Un golpe de CARGA SÍSMICA lo hace vibrar para siempre (su `marca`).
## Dibujo: arte/mundos/asterhaul/desfiladero/pilar.png, 0 dormido · 1 sonando.

signal sonando

const DIBUJO := preload("res://arte/mundos/asterhaul/desfiladero/pilar.png")

@export var marca := ""
var radio_carga := 6.0
var encendido := false
var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("sismicos")
	add_to_group("pilares_diapason")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -22)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 8)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	if marca != "" and Estado.tiene(marca):
		encendido = true
		_sprite.frame = 1


func _process(delta: float) -> void:
	if encendido:
		_tiempo += delta
		_sprite.position.x = roundf(sin(_tiempo * 50.0) * 0.6)      # vibra


func recibir_carga(_direccion: Vector2) -> bool:
	if encendido:
		return true
	encendido = true
	_sprite.frame = 1
	if marca != "":
		Estado.marcar(marca)
	Sonido.efecto("diapason_ambar", 2.0, global_position)
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position + Vector2(0, -30), Color("ffb040"), 0.9, 0.9, 0.5)
	sonando.emit()
	return true
