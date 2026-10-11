extends CharacterBody2D
## RANA DE PIEDRA: el enemigo de Las Pasarelas. Una rana de roca con grietas de Giza.
##   - Da saltitos por la zona. Si ve a Maisha cerca, se AGAZAPA (y en el suelo sale una sombra que marca dónde
##     caerá) y SALTA hacia ella. En el aire no se le puede dar.
##   - Al caer hace una ONDA que hace daño si Maisha está debajo, y se queda ATONTADA un momento:
##     ahí el cetro le quita 2. Si se le da sin estar atontada, le quita 1 y da un salto para apartarse.
##   - Una semilla le quita 2. Las raíces de la semilla la sujetan; el Latido la empuja.
## Dibujo: arte/mundos/raiz/pasarelas/rana.png (herramientas/pintar_pasarelas.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIOLETA := Color("a855d6")

enum Fase { ACECHA, AGAZAPA, VUELA, ATONTADA, ESQUIVA }

var variante := "raiz"
var zona: Node = null
var vida := R.RANA_VIDA
var fase := Fase.ACECHA
var _t := 0.0
var _tiempo := 0.0
var _espera := 0.8
var _desde := Vector2.ZERO
var _hasta := Vector2.ZERO
var _alto := 28.0
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _sombra: Node2D
var _marca: Node2D               # la sombra de aviso en el suelo (donde va a caer)


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 9.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/pasarelas/rana.png")
	_sprite.hframes = 6
	_sprite.centered = false
	_sprite.offset = Vector2(-11, -19)
	add_child(_sprite)
	_marca = Node2D.new()
	_marca.top_level = true
	_marca.z_index = -3
	_marca.draw.connect(_dibujar_marca)
	add_child(_marca)
	_tiempo = randf() * 3.0
	_espera = randf_range(0.6, 1.4)
	Sonido.efecto("rana_croa", 0.0, global_position, 0.15)


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0


func en_el_aire() -> bool:
	return fase in [Fase.VUELA, Fase.ESQUIVA]


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	if _muriendo:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	match fase:
		Fase.ACECHA:
			_espera -= delta
			if _enraizado <= 0.0 and _espera <= 0.0:
				if maisha and maisha.global_position.distance_to(global_position) < R.RANA_VE:
					_hasta = _limitar(maisha.global_position)
					_cambiar(Fase.AGAZAPA)
					Sonido.efecto("rana_croa", 0.0, global_position)
				else:
					# un saltito por la zona
					_saltar_a(_limitar(global_position + Vector2.from_angle(randf() * TAU) * randf_range(16, 30)), 10.0, Fase.ESQUIVA)
			# toca a Maisha: le hace daño
			if maisha and maisha.global_position.distance_to(global_position) < 10.0:
				if maisha.call("recibir_danio", 1, global_position, "contacto"):
					_empuje = (global_position - maisha.global_position).normalized() * 70.0
		Fase.AGAZAPA:
			if _enraizado > 0.0:
				_cambiar(Fase.ACECHA)
			elif _t >= R.RANA_AGAZAPA:
				Sonido.efecto("rana_salta", 0.0, global_position)
				_saltar_a(_hasta, 30.0, Fase.VUELA)
		Fase.VUELA, Fase.ESQUIVA:
			var dura := R.RANA_VUELO if fase == Fase.VUELA else 0.35
			var f := clampf(_t / dura, 0.0, 1.0)
			global_position = _desde.lerp(_hasta, f)
			_sprite.position.y = -sin(f * PI) * _alto
			if f >= 1.0:
				_sprite.position.y = 0.0
				if fase == Fase.VUELA:
					_aterrizar(maisha)
				else:
					_espera = randf_range(0.6, 1.2)
					_cambiar(Fase.ACECHA)
		Fase.ATONTADA:
			if _t >= R.RANA_ATONTADA:
				_espera = R.RANA_ESPERA
				_cambiar(Fase.ACECHA)
	if not en_el_aire():
		velocity = _empuje
		_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
		move_and_slide()
		global_position = _limitar(global_position)
	_animar()
	_marca.queue_redraw()


func _limitar(p: Vector2) -> Vector2:
	return zona.limitar(p) if zona else p


func _saltar_a(destino: Vector2, alto: float, como: int) -> void:
	_desde = global_position
	_hasta = destino
	_alto = alto
	_cambiar(como)


func _aterrizar(maisha: Node2D) -> void:
	Sonido.efecto("rana_cae", 0.0, global_position)
	Impacto.temblar(1.5, 0.15)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 5
	astillas.fuerza = 50.0
	astillas.position = global_position
	get_parent().add_child(astillas)
	if maisha and maisha.global_position.distance_to(global_position) < R.RANA_ONDA:
		maisha.call("recibir_danio", 1, global_position, "contacto")
	_cambiar(Fase.ATONTADA)


func _animar() -> void:
	var frame := 0
	match fase:
		Fase.ACECHA:
			frame = 0 if fmod(_tiempo, 2.2) > 0.25 else 1
		Fase.AGAZAPA:
			frame = 1
			_sprite.position.x = sin(_tiempo * 50.0) * 0.6
		Fase.VUELA, Fase.ESQUIVA:
			frame = 2
		Fase.ATONTADA:
			frame = 3 if _t < 0.18 else 4
	if fase != Fase.AGAZAPA:
		_sprite.position.x = 0.0
	if _destello > 0.0:
		frame = 5
	_sprite.frame = frame
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	if fase in [Fase.AGAZAPA, Fase.VUELA, Fase.ESQUIVA] and absf(_hasta.x - global_position.x) > 1.0:
		_sprite.flip_h = _hasta.x < global_position.x
	# la sombra se encoge cuanto más alto va
	_sombra.scale = Vector2.ONE * (1.0 - clampf(-_sprite.position.y / 40.0, 0.0, 0.5))


func _dibujar_marca() -> void:
	# dónde va a caer: un círculo que se cierra mientras se agazapa y vuela
	if fase not in [Fase.AGAZAPA, Fase.VUELA]:
		return
	var f := _t / R.RANA_AGAZAPA if fase == Fase.AGAZAPA else 1.0 + _t / R.RANA_VUELO
	var r := lerpf(R.RANA_ONDA + 6.0, R.RANA_ONDA * 0.6, clampf(f / 2.0, 0.0, 1.0))
	var a := 0.25 + 0.3 * clampf(f / 2.0, 0.0, 1.0)
	for y in range(-3, 4):
		var ancho := r * sqrt(1.0 - (y / 3.5) * (y / 3.5))
		_marca.draw_rect(Rect2(_hasta + Vector2(-ancho, y), Vector2(ancho * 2, 1)), Color(0.05, 0.03, 0.08, a))
	_marca.draw_arc(_hasta, r, 0, TAU, 24, Color(VIOLETA, 0.5 + 0.3 * sin(_tiempo * 18.0)), 1.0)


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo or en_el_aire():
		return false
	var atontada := fase == Fase.ATONTADA
	_empuje = direccion * R.GOLPE_EMPUJE * (0.8 if atontada else 0.4)
	recibir_danio(danio + (1 if atontada else 0), global_position - direccion * 10.0, "golpe")
	if not atontada and not _muriendo:
		# se aparta de un salto
		_saltar_a(_limitar(global_position + direccion * 40.0), 14.0, Fase.ESQUIVA)
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	if not en_el_aire():
		_empuje = fuerza


func recibir_danio(cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	if _muriendo or (en_el_aire() and tipo != "explosion"):
		return
	vida -= cantidad + (1 if tipo == "explosion" else 0)
	_destello = 0.12
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_marca.queue_free()
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.chispas = 4
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.3), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
