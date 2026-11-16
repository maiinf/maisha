extends StaticBody2D
## UNA GEODA RESONANTE (Asterhaul, la Bóveda de las Geodas): una piedra partida con cristales dentro. Dormida no
## alumbra. Un golpe de cetro (o una Carga) la hace resonar y se queda encendida para siempre (su `marca`): un halo
## cálido que alumbra la oscuridad a su alrededor.
## Dibujo: arte/mundos/asterhaul/galerias/geoda.png, 0 dormida · 1 encendida.

signal encendida_ahora

const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/geoda.png")

@export var marca := ""
var encendida := false
var radio_carga := 6.0
var _sprite: Sprite2D
var _luz: PointLight2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("geodas")
	add_to_group("golpeables")
	add_to_group("sismicos")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(18, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)
	_luz = PointLight2D.new()
	_luz.texture = preload("res://scripts/mundo/relieve.gd").textura_luz(256)
	_luz.texture_scale = 1.5
	_luz.color = Color(1.0, 0.78, 0.42)
	_luz.energy = 0.0
	_luz.position = Vector2(0, -12)
	add_child(_luz)
	if marca != "" and Estado.tiene(marca):
		_encender(false)


func _process(delta: float) -> void:
	if encendida:
		_tiempo += delta
		_luz.energy = 1.25 + sin(_tiempo * 2.2) * 0.12       # respira


func _encender(con_sonido: bool) -> void:
	encendida = true
	_sprite.frame = 1
	_luz.energy = 1.25
	if con_sonido:
		if marca != "":
			Estado.marcar(marca)
		Sonido.efecto("geoda_encender", 0.0, global_position)
		encendida_ahora.emit()


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if encendida:
		return false
	_encender(true)
	return true


func recibir_carga(_direccion: Vector2) -> bool:
	if not encendida:
		_encender(true)
	return true
