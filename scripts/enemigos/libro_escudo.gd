extends CharacterBody2D
## LIBRO ESCUDO (Las Estanterías Colgantes, Sigilia): uno de los tres tomos encantados que orbitan
## alrededor del Bibliotecario Hueco protegiéndole.
##   - Mientras orbita, absorbe cualquier golpe directo contra el Bibliotecario.
##   - Vulnerable al cetro (1) y al Sigilo de Fuego / Semilla de Asili (2: arde al instante).
##   - El Bibliotecario puede lanzarlo en línea recta como proyectil cortante.

const DIBUJO := preload("res://arte/mundos/sigilia/estanterias/libro_escudo.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

var bibliotecario: Node2D = null
var angulo := 0.0
var radio_x := 44.0
var radio_y := 20.0
var vida := 2
var lanzado := false
var dir_lanzado := Vector2.ZERO
var velocidad := 150.0

var _t := 0.0
var _destello := 0.0
var _muriendo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("libros_escudo")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING

	var col := CollisionShape2D.new()
	var circ := CircleShape2D.new()
	circ.radius = 9.0
	col.shape = circ
	add_child(col)

	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	add_child(_sprite)


func _process(delta: float) -> void:
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_sprite.frame = int(_t * 8.0) % 4
	_sprite.modulate = Color(2.0, 1.8, 1.8) if _destello > 0.0 else Color.WHITE

	if lanzado:
		var col := move_and_collide(dir_lanzado * velocidad * delta)
		if col:
			var obj := col.get_collider() as Node
			if obj and obj.is_in_group("maisha"):
				obj.call("recibir_danio", 1, global_position)
			destruir()
	elif is_instance_valid(bibliotecario):
		angulo += delta * 2.2
		global_position = bibliotecario.global_position + Vector2(cos(angulo) * radio_x, sin(angulo) * radio_y - 20.0)


func lanzar(hacia: Vector2) -> void:
	lanzado = true
	dir_lanzado = hacia.normalized()
	add_to_group("proyectiles_enemigos")
	Sonido.efecto("cetro_golpe", -2.0, global_position)


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	var danio_real := 2 if tipo in ["fuego", "explosion"] else cantidad
	vida -= danio_real
	_destello = 0.15
	Impacto.chispa(global_position, Vector2.UP, Color("c084fc"))
	if vida > 0:
		Sonido.efecto("golpe_acierto", -2.0, global_position)
	else:
		destruir()


func destruir() -> void:
	if _muriendo:
		return
	_muriendo = true
	remove_from_group("daniables")
	remove_from_group("golpeables")
	remove_from_group("libros_escudo")
	Sonido.efecto("cristal", -3.0, global_position)
	Impacto.chispa(global_position, Vector2.UP, Color("fde047"))
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.position = global_position
	if get_parent():
		get_parent().add_child(astillas)
	if is_instance_valid(bibliotecario):
		bibliotecario.call("libro_destruido", self)
	queue_free()
