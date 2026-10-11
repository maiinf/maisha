extends Node2D
## GALLINA DE LA GRANJA: picotea, da paseítos cortos y se aparta si Maisha se acerca.
## No choca con nada: es solo vida alrededor de la casa de Mzee Shamba.

const TEXTURA := preload("res://arte/mundos/kitovu/gallina.png")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const RADIO_PASEO := 26.0

var _sprite: Sprite2D
var _origen := Vector2.ZERO
var _destino := Vector2.ZERO
var _espera := 0.0
var _paso := 0.0
var _azar := RandomNumberGenerator.new()


func _ready() -> void:
	add_to_group("gallinas")
	_origen = position
	_destino = position
	_azar.seed = int(position.x * 31.0 + position.y * 7.0)
	_espera = _azar.randf_range(0.2, 2.0)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 4.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-5, -10)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)


func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < 20.0:
		# se asusta y sale corriendo un poco
		var huida := (global_position - maisha.global_position).normalized() * 18.0
		_destino = _origen + (position + huida - _origen).limit_length(RADIO_PASEO)
		_espera = 0.0
	if position.distance_to(_destino) > 0.5:
		var rapidez := 46.0 if maisha and maisha.global_position.distance_to(global_position) < 26.0 else 18.0
		var antes := position
		position = position.move_toward(_destino, rapidez * delta)
		_sprite.flip_h = position.x > antes.x
		_paso += delta * 10.0
		_sprite.frame = int(_paso) % 2
		_sprite.position.y = 0.0
		return
	# parada: picotear de vez en cuando
	_espera -= delta
	_paso += delta
	_sprite.frame = 0
	_sprite.position.y = 1.0 if fmod(_paso, 1.3) < 0.18 else 0.0
	if _espera <= 0.0:
		_espera = _azar.randf_range(1.0, 3.5)
		var a := _azar.randf() * TAU
		_destino = _origen + Vector2(cos(a), sin(a) * 0.6) * _azar.randf_range(6.0, RADIO_PASEO)
