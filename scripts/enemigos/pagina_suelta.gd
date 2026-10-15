extends CharacterBody2D
## PÁGINA SUELTA (Sigilia, Paso de la Escarcha): una hoja escrita con Tinta Quieta que vuela sola. Va a la deriva
## alrededor de donde nació, aleteando; si ve a Maisha cerca, se le echa encima en curva y, al tocarla, le quita una
## hoja y se aparta revoloteando. Las rachas de la ventisca la arrastran. Vuela por encima de todo.
##   - El cetro: 2 golpes. Una semilla: 2. EL SIGILO DE FUEGO la quema de un trazo (es papel).

const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/paso/pagina.png")
const VIDA := 2
const VE_A := 110.0
const VELOCIDAD := 58.0
const PICADO := 84.0

var zona: Node = null
var vida := VIDA
var _casa := Vector2.ZERO
var _tiempo := 0.0
var _empuje := Vector2.ZERO
var _huye := 0.0
var _aturdido := 0.0
var _enraizado := 0.0
var _destello := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _fase := 0.0


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("paginas")
	collision_layer = 2
	collision_mask = 0                         # vuela: no choca con nada
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = 6.0
	forma.shape = c
	forma.position = Vector2(0, -14)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 7.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -16)
	add_child(_sprite)
	_casa = global_position
	_fase = randf() * TAU
	_tiempo = randf() * 4.0


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_huye = maxf(0.0, _huye - delta)
	_aturdido = maxf(0.0, _aturdido - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mov := Vector2.ZERO
	var picando := false
	if _enraizado > 0.0 or _aturdido > 0.0:
		mov = Vector2.ZERO
	elif _huye > 0.0 and maisha:
		mov = (global_position - maisha.global_position).normalized() * VELOCIDAD
	elif maisha and not maisha.get("esta_caida") and global_position.distance_to(maisha.global_position) < VE_A:
		# se le echa encima en curva (de lado y luego de frente)
		var hacia := maisha.global_position - global_position
		var lado := hacia.orthogonal().normalized() * sin(_tiempo * 3.0 + _fase) * 0.6
		mov = (hacia.normalized() + lado).normalized() * (PICADO if hacia.length() < 44.0 else VELOCIDAD)
		picando = hacia.length() < 44.0
	else:
		# a la deriva alrededor de su casa
		var objetivo := _casa + Vector2(sin(_tiempo * 0.7 + _fase) * 40.0, cos(_tiempo * 0.9 + _fase) * 22.0)
		mov = (objetivo - global_position).limit_length(30.0)
	# las rachas de la ventisca la arrastran
	var ventisca := get_tree().current_scene.get_node_or_null("Ventisca")
	if ventisca and ventisca.activa and ventisca.fase == ventisca.Fase.RACHA:
		mov.x += -ventisca.desde * 70.0
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 300.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	# al tocarla, le quita una hoja y se aparta
	if maisha and _huye <= 0.0 and _aturdido <= 0.0 and global_position.distance_to(maisha.global_position) < 11.0:
		if maisha.call("recibir_danio", 1, global_position, "contacto"):
			_huye = 1.0
	# el dibujo: aletea (y en picado, doblada en punta); blanca al recibir un golpe
	if _destello > 0.0:
		_sprite.frame = 5
	elif picando:
		_sprite.frame = 4
	else:
		_sprite.frame = int(_tiempo * 10.0) % 4
	if absf(velocity.x) > 4.0:
		_sprite.flip_h = velocity.x < 0.0
	_sprite.position.y = sin(_tiempo * 4.0 + _fase) * 2.0


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_empuje = direccion * 90.0
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_aturdido = maxf(_aturdido, 0.4)


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	vida -= VIDA if tipo == "fuego" else (2 if tipo == "explosion" else cantidad)
	_destello = 0.12
	_huye = maxf(_huye, 0.5)
	if vida > 0:
		Sonido.efecto("pagina", -2.0, global_position, 0.2)
	else:
		morir(tipo == "fuego")


func morir(quemada := false) -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("pagina", self)
	Sonido.efecto("fuego_quema" if quemada else "pagina", -4.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	remove_from_group("paginas")
	# quemada: se ennegrece y se deshace en ceniza; si no, se rompe en trocitos de papel
	var t := create_tween().set_parallel(true)
	if quemada:
		t.tween_property(_sprite, "modulate", Color(0.25, 0.12, 0.08), 0.25)
	t.tween_property(_sprite, "scale", Vector2(0.4, 1.3), 0.35)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
