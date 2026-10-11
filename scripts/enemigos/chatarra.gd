extends StaticBody2D
## BLOQUE DE CHATARRA que deja una tuerca de la Cosechadora al caer: estorba el paso (a Maisha y a las babosas).
## El cetro rebota; una semilla lo deshace. Se oxida y se desmorona solo al cabo de un rato.
## La Cosechadora lo aplasta si se lo encuentra delante.

const R := preload("res://scripts/combate/reglas_combate.gd")
const TEXTURA := preload("res://arte/mundos/raiz/campo/chatarra.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

var dura: float = R.COSECHADORA_CHATARRA_DURA
var _t := 0.0
var _rota := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("chatarra")
	add_to_group("golpeables")
	add_to_group("daniables")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -9)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)
	# cae desde arriba con un golpe
	_sprite.position.y = -10
	var t := create_tween()
	t.tween_property(_sprite, "position:y", 0.0, 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	t.tween_callback(func() -> void: Impacto.temblar(1.2, 0.1))


func _process(delta: float) -> void:
	_t += delta
	if _t > dura and not _rota:
		romper()
	elif _t > dura - 2.0 and not _rota:
		_sprite.position.x = sin(_t * 40.0) * 0.6           # tiembla antes de desmoronarse


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo == "explosion":
		romper()


func romper() -> void:
	if _rota:
		return
	_rota = true
	remove_from_group("chatarra")
	remove_from_group("golpeables")
	remove_from_group("daniables")
	Sonido.efecto("piedra_rompe", 0.0, global_position)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.fuerza = 60.0
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	_sprite.frame = 1
	for h in get_children():
		if h is CollisionShape2D:
			h.set_deferred("disabled", true)
	var t := create_tween()
	t.tween_property(self, "modulate:a", 0.0, 1.2).set_delay(0.6)
	t.tween_callback(queue_free)
