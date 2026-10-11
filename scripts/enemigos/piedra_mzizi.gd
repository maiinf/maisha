extends Node2D
## PIEDRA QUE ESCUPE MZIZI: un trozo de raíz de piedra que vuela girando, con una estela violeta.
## Hace daño a Maisha si la toca. El golpe del cetro la rompe en el aire.

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const TEXTURA := preload("res://arte/zonas/raiz/piedra.png")

var direccion := Vector2.DOWN
var velocidad: float = R.MZIZI_PIEDRA_VELOCIDAD
var altura := 14.0               # vuela por encima del suelo (la sombra va abajo)
var _vida := 0.0
var _sprite: Sprite2D
var _estela: Array[Vector2] = []


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("piedras_mzizi")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 4
	_sprite.position = Vector2(0, -altura)
	add_child(_sprite)


func _process(delta: float) -> void:
	_vida += delta
	position += direccion * velocidad * delta
	_sprite.frame = int(_vida * 14.0) % 4
	# baja un poco al final de su vuelo
	altura = maxf(4.0, 14.0 - _vida * 4.0)
	_sprite.position = Vector2(0, -altura)
	_estela.push_front(global_position + Vector2(0, -altura))
	if _estela.size() > 6:
		_estela.pop_back()
	queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < 9.0:
		maisha.call("recibir_danio", R.MZIZI_PIEDRA_DANIO, global_position - direccion * 8.0, "contacto")
		romper()
		return
	var zona := get_tree().get_first_node_in_group("arena_jefe") as Node2D
	if _vida > 3.5 or (zona and zona.call("distancia_normal", global_position) > 1.0):
		romper()


func _draw() -> void:
	# sombra en el suelo y estela violeta
	draw_rect(Rect2(Vector2(-3, -1), Vector2(6, 2)), Color(0.04, 0.06, 0.03, 0.35))
	for i in _estela.size():
		var p := (_estela[i] - global_position).round()
		var a := 0.45 * (1.0 - float(i) / _estela.size())
		draw_rect(Rect2(p - Vector2(1, 1), Vector2(2, 2)), Color(0.66, 0.33, 0.84, a))


## El cetro la rompe en el aire
func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	romper()
	return true


func romper() -> void:
	if not is_inside_tree():
		return
	Sonido.efecto("piedra_rompe", 0.0, global_position)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 6
	astillas.chispas = 2
	astillas.fuerza = 50.0
	astillas.position = global_position + Vector2(0, -altura * 0.5)
	get_parent().add_child(astillas)
	queue_free()
