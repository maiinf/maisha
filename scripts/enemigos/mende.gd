extends CharacterBody2D
## MENDE, EL BICHO DE ÓXIDO: el escarabajo que invoca Buibui, la araña-bruja. Sale del nido de un salto, corretea muy
## deprisa hacia Maisha y le hace daño al tocarla. Muere de un golpe (o con el Latido, si choca contra algo).
## Dibujo: arte/mundos/raiz/hechiceros/mende.png (0-1 corre, 2 golpeado).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/raiz/hechiceros/mende.png")

var variante := "raiz"
var zona: Node = null
var vida: int = R.MENDE_VIDA
var salto := Vector2.ZERO          # el saltito al salir del nido (hacia dónde cae)
var _saltando := 0.0
var _aturdido := 0.0
var _enraizado := 0.0
var _empuje := Vector2.ZERO
var _tiempo := 0.0
var _ruido := 0.0
var _muriendo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var circulo := CircleShape2D.new()
	circulo.radius = 3.0
	forma.shape = circulo
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 5.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.offset = Vector2(0, -4)
	add_child(_sprite)
	if salto != Vector2.ZERO:
		_saltando = 0.4
	_tiempo = randf()


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_aturdido = maxf(0.0, _aturdido - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if _saltando > 0.0:
		# sale del nido en un arco
		_saltando -= delta
		var k := 1.0 - _saltando / 0.4
		global_position += salto * delta / 0.4
		_sprite.position.y = -sin(k * PI) * 10.0
		return
	_sprite.position.y = 0.0
	var deseo := Vector2.ZERO
	if _aturdido <= 0.0 and _enraizado <= 0.0 and maisha and not maisha.get("esta_caida") \
			and global_position.distance_to(maisha.global_position) < R.MENDE_VE:
		deseo = (maisha.global_position - global_position).normalized()
		# corretea en zigzag, como un bicho
		deseo = deseo.rotated(sin(_tiempo * 9.0) * 0.6)
		if maisha.call("es_invulnerable") and global_position.distance_to(maisha.global_position) < 18.0:
			deseo = -deseo * 0.6
	velocity = deseo * R.MENDE_VELOCIDAD + _empuje
	if _enraizado > 0.0:
		velocity = Vector2.ZERO
	_empuje = _empuje.move_toward(Vector2.ZERO, 500.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	if maisha and global_position.distance_to(maisha.global_position) < 8.0:
		if maisha.call("recibir_danio", 1, global_position, "contacto"):
			_empuje = (global_position - maisha.global_position).normalized() * 120.0
			_aturdido = 0.6
	if velocity.length() > 5.0:
		_sprite.frame = int(_tiempo * 14.0) % 2
		_ruido -= delta
		if _ruido <= 0.0:
			_ruido = 0.5
			Sonido.efecto("mende_corre", 0.0, global_position, 0.2)
		_sprite.flip_h = velocity.x < 0.0
	else:
		_sprite.frame = 0


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo or _saltando > 0.0:
		return false
	_empuje = direccion * R.GOLPE_EMPUJE
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, _tipo: String) -> void:
	if _muriendo:
		return
	vida -= cantidad
	if vida <= 0:
		morir()


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_aturdido = maxf(_aturdido, 0.4)


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("mende", self)
	Sonido.efecto("mende_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = 2
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 4
	astillas.position = global_position
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.5, 0.2), 0.15)
	t.tween_property(self, "modulate:a", 0.0, 0.2)
	t.chain().tween_callback(queue_free)
