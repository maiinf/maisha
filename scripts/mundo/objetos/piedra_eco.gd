extends StaticBody2D
## PIEDRA-ECO: al golpearla con el cetro se enciende su runa.
## Cuando todas las piedras-eco de la región están encendidas, el escondite se abre
## (la roca marcada con Q se aparta).

signal encendida

const TEXTURA := preload("res://arte/mundos/raiz/objetos/piedra_eco.png")

var encendida_ya := false
var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("piedras_eco")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -8)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(10, 6)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)


func _process(delta: float) -> void:
	if encendida_ya:
		_tiempo += delta
		_sprite.modulate = Color(1, 1, 1).lerp(Color(1.25, 1.15, 0.95), 0.5 + 0.5 * sin(_tiempo * 4.0))


## El cetro la enciende. Devuelve false: no cuenta como acierto contra un enemigo.
func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if not encendida_ya:
		encendida_ya = true
		_sprite.frame = 1
		var t := create_tween()
		t.tween_property(_sprite, "scale", Vector2(1.15, 0.9), 0.05)
		t.tween_property(_sprite, "scale", Vector2.ONE, 0.12)
		encendida.emit()
	return false


## Ya se encendió en otra visita: encendida, sin sonido ni aviso
func encender_sin_aviso() -> void:
	encendida_ya = true
	_sprite.frame = 1
