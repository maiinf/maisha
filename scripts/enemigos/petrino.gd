extends CharacterBody2D
## PETRINO: un trozo de raíz que Giza ha vuelto de piedra y obliga a caminar. El enemigo común de Raíz.
## Vaga por la zona y persigue a Maisha cuando la ve. Hace daño al tocarla.
## El golpe del cetro le quita 1 de vida, lo empuja y lo aturde; una explosión lo rompe.
## No puede entrar en casillas con brotes.

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
## fotogramas de arte/zonas/<variante>/petrino.png
const QUIETO := [0, 1]
const ANDAR := [2, 3, 4, 5]
const EMBESTIDA := 6
const GOLPEADO := 7

var variante := "raiz"            # el mundo (arte/zonas/<variante>/petrino.png)
var zona: Node = null            # la zona corrupta a la que pertenece (lo mantiene dentro)
var vida: int = R.PETRINO_VIDA
var _aturdido := 0.0
var _enraizado := 0.0            # atrapado por las raíces de una semilla
var _destello := 0.0
var _empuje := Vector2.ZERO
var _rumbo := Vector2.ZERO
var _cambio_rumbo := 0.0
var _tiempo := 0.0
var _muriendo := false
var _ultimo_grunido := -9.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 2           # no choca con Maisha (el daño es por contacto)
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var circulo := CircleShape2D.new()
	circulo.radius = 5.0
	forma.shape = circulo
	forma.position = Vector2(0, -3)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 8.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/petrino.png" % variante)
	_sprite.hframes = 8
	_sprite.offset = Vector2(0, -11)
	add_child(_sprite)
	_tiempo = randf() * 2.0
	Sonido.efecto("petrino_aparece", 0.0, global_position, 0.1)        # brota del suelo


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_aturdido = maxf(0.0, _aturdido - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D

	var deseo := Vector2.ZERO
	if _aturdido <= 0.0 and _enraizado <= 0.0:
		var distancia := global_position.distance_to(maisha.global_position) if maisha else 9999.0
		if maisha and not maisha.get("esta_caida") and distancia < R.PETRINO_VE_A:
			deseo = (maisha.global_position - global_position).normalized()
			# mientras Maisha parpadea tras un golpe, guarda las distancias (no se queda pegado)
			if maisha.call("es_invulnerable") and distancia < 22.0:
				deseo = -deseo * 0.5
		else:
			_cambio_rumbo -= delta
			if _cambio_rumbo <= 0.0:
				_cambio_rumbo = randf_range(1.0, 2.5)
				_rumbo = Vector2.from_angle(randf() * TAU) if randf() < 0.7 else Vector2.ZERO
			deseo = _rumbo * 0.6
	var mov := deseo * R.PETRINO_VELOCIDAD
	mov = _evitar_brotes(mov, delta)
	velocity = mov + _empuje
	if _enraizado > 0.0:
		velocity = Vector2.ZERO
	queue_redraw()
	_empuje = _empuje.move_toward(Vector2.ZERO, 500.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)

	# daño por contacto
	if maisha and global_position.distance_to(maisha.global_position) < 11.0:
		if maisha.call("recibir_danio", R.PETRINO_DANIO, global_position, "contacto"):
			# tras morder, rebota hacia atrás y se queda un instante quieto
			_empuje = (global_position - maisha.global_position).normalized() * 110.0
			_aturdido = 0.5

	# dibujo: anda con sus patas de raíz; embiste cuando tiene a Maisha cerca; blanco al recibir daño
	var cerca := maisha != null and global_position.distance_to(maisha.global_position) < 34.0
	if _destello > 0.0:
		_sprite.frame = GOLPEADO
	elif cerca and _aturdido <= 0.0 and _enraizado <= 0.0:
		if _sprite.frame != EMBESTIDA and _tiempo - _ultimo_grunido > 2.0:
			_ultimo_grunido = _tiempo
			Sonido.efecto("petrino_embiste", 0.0, global_position, 0.12)
		_sprite.frame = EMBESTIDA
	elif velocity.length() > 2.0:
		_sprite.frame = ANDAR[int(_tiempo * 8.0) % 4]
	else:
		_sprite.frame = QUIETO[int(_tiempo * 1.5) % 2]
	if velocity.x != 0.0:
		_sprite.flip_h = velocity.x < 0.0


func _evitar_brotes(mov: Vector2, delta: float) -> Vector2:
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	if registro == null or mov == Vector2.ZERO:
		return mov
	var aqui := R.casilla_de(global_position)
	var siguiente := R.casilla_de(global_position + mov.normalized() * 6.0 + mov * delta)
	if siguiente != aqui and registro.hay_brote(siguiente):
		# prueba a moverse solo en horizontal o solo en vertical
		var solo_x := R.casilla_de(global_position + Vector2(sign(mov.x) * 6.0, 0))
		var solo_y := R.casilla_de(global_position + Vector2(0, sign(mov.y) * 6.0))
		if mov.x != 0.0 and not registro.hay_brote(solo_x):
			return Vector2(mov.x, 0)
		if mov.y != 0.0 and not registro.hay_brote(solo_y):
			return Vector2(0, mov.y)
		return Vector2.ZERO
	return mov


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_aturdido = R.GOLPE_ATURDE
	_empuje = direccion * R.GOLPE_EMPUJE
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


## Las raíces de una semilla lo sujetan unos segundos
func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)
	_empuje = Vector2.ZERO


func esta_enraizado() -> bool:
	return _enraizado > 0.0


## Raíces alrededor de la base mientras está atrapado
func _draw() -> void:
	if _muriendo:
		return
	# un halo violeta en el suelo: la luz de Giza que lo mueve (y que se vea sobre la piedra)
	var pulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
	for y in range(-2, 3):
		var ancho := int(round(9.0 * sqrt(1.0 - (y / 3.0) * (y / 3.0))))
		draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.66, 0.33, 0.84, 0.18 + 0.1 * pulso))
	if _enraizado <= 0.0:
		return
	var vaiven := int(_tiempo * 6.0) % 2
	for p in [Vector2(-7, 0), Vector2(-6, -2 - vaiven), Vector2(-4, 1), Vector2(6, 0), Vector2(5, -2 + vaiven - 1), Vector2(3, 1), Vector2(0, 1)]:
		draw_rect(Rect2(p, Vector2.ONE), Color("3e9a35"))
	for p in [Vector2(-7, -1 - vaiven), Vector2(6, -1 - vaiven)]:
		draw_rect(Rect2(p, Vector2.ONE), Color("6fcf4f"))


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_aturdido = maxf(_aturdido, 0.3)


func recibir_danio(cantidad: int, desde: Vector2, _tipo: String) -> void:
	if _muriendo:
		return
	vida -= cantidad
	_destello = 0.1
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
	var lejos := global_position - desde
	if lejos.length() > 0.1 and _empuje == Vector2.ZERO:
		_empuje = lejos.normalized() * 120.0
	if vida <= 0:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("petrino", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	Impacto.temblar(1.2, 0.12)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = GOLPEADO
	# se desmorona en trocitos de piedra
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.position = global_position + Vector2(0, -2)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.4, 0.2), 0.25)
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.chain().tween_callback(queue_free)
