extends StaticBody2D
## LA CORTINA DE MICELIO (cueva de las setas, «ǫ»): hilos blancos y violetas que tapan el paso a la sala de Kuvu. Late
## despacio. Se mira con Acción («cueva_cortina») y se CORTA con el cetro: tres golpes y se rompe (marca
## «cortina_abierta»). Dibujo: arte/mundos/raiz/paso/cortina.png (0 quieta, 1 latiendo).

const DIBUJO := preload("res://arte/mundos/raiz/paso/cortina.png")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const GOLPES := 3

var ancho := 48.0
var radio_interaccion := 36.0
var altura_bocadillo := 40.0
var _golpes := 0
var _tiempo := 0.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("cortina")
	add_to_group("golpeables")
	add_to_group("interactuables")
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(ancho, 14)
	forma.shape = caja
	forma.position = Vector2(0, -6)
	add_child(forma)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -20)
	_sprite.modulate = Color(0.75, 0.7, 0.8)
	add_child(_sprite)
	var luz := PointLight2D.new()
	luz.texture = OSCURIDAD.textura_luz()
	luz.texture_scale = 0.6
	luz.color = Color(0.7, 0.4, 0.95)
	luz.energy = 0.35
	luz.position = Vector2(0, -20)
	add_child(luz)


func _process(delta: float) -> void:
	_tiempo += delta
	_sprite.frame = 1 if fmod(_tiempo, 2.4) < 0.6 else 0


func interactuar() -> void:
	await CHARLA.hablar(self, "cueva_cortina")


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	_golpes += 1
	Sonido.efecto("mende_muere", 0.0, global_position)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 6
	astillas.position = global_position + Vector2(randf_range(-16, 16), -18)
	get_parent().add_child(astillas)
	_sprite.scale = Vector2(1.0, 1.0 - 0.2 * _golpes)
	_sprite.position.y = 20.0 * 0.2 * _golpes
	if _golpes >= GOLPES:
		romper()
	return true


func romper() -> void:
	remove_from_group("golpeables")
	remove_from_group("interactuables")
	remove_from_group("cortina")
	Estado.marcar("cortina_abierta")
	var t := create_tween()
	t.tween_property(self, "modulate:a", 0.0, 0.6)
	t.tween_callback(queue_free)
	CHARLA.hablar(get_parent(), "cueva_cortina_rota")
