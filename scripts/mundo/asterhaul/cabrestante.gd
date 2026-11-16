extends StaticBody2D
## UN CABRESTANTE (Asterhaul, la Fundición): el torno de cadena de una barcaza. Un golpe de cetro (o una Carga) le
## da una vuelta a la manivela y, al cabo de ESPERA s (lo justo para subirse), la `barcaza` sale hacia el otro lado.
## Es la manera de cruzar ANTES de saber el Pulso Magnético.
## Dibujo: arte/mundos/asterhaul/fundicion/cabrestante.png (dos posiciones de la manivela).

const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/cabrestante.png")
const ESPERA := 1.3

var barcaza: Node2D
var radio_carga := 6.0
var _sprite: Sprite2D
var _girando := 0.0


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("sismicos")
	add_to_group("cabrestantes")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -15)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(20, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)


func _process(delta: float) -> void:
	if _girando <= 0.0:
		return
	_girando -= delta
	_sprite.frame = int(_girando * 10.0) % 2
	if _girando <= 0.0 and is_instance_valid(barcaza):
		barcaza.call("cruzar")


func _usar() -> bool:
	if _girando > 0.0 or not is_instance_valid(barcaza) or barcaza.moviendose:
		return false
	_girando = ESPERA
	Sonido.efecto("rueda_abrir", 0.0, global_position)
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje("La cadena se suelta: ¡a la barcaza!")
	return true


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	return _usar()


func recibir_carga(_direccion: Vector2) -> bool:
	_usar()
	return true
