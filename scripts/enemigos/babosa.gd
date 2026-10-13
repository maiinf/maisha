extends CharacterBody2D
## BABOSA DE ÓXIDO: el «errante» de la Ciénaga Quieta. Giza la ha llenado de herrumbre.
##   - Se arrastra despacio por la zona y deja un RASTRO de óxido: si Maisha lo pisa, anda más despacio
##     un momento. El rastro se seca a los pocos segundos.
##   - Hace daño al tocarla. El cetro le quita 1 (y la encoge un instante); una explosión la deshace.
##   - No puede cruzar los brotes de una semilla.
## Dibujo: arte/mundos/raiz/cienaga/babosa.png (herramientas/dibujar_cienaga.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 2
const VELOCIDAD := 14.0
const RASTRO_DURA := 6.0
const RASTRO_CADA := 5.0          # píxeles entre mancha y mancha
const COLOR_RASTRO := Color("9c4f24")

var variante := "raiz"
var zona: Node = null
var vida := VIDA
var _rumbo := Vector2.RIGHT
var _cambio := 0.0
var _encogida := 0.0
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _tiempo := 0.0
var _muriendo := false
var _rastro: Array[Dictionary] = []        # {p (global), t}
var _ultimo := Vector2.INF
var _sprite: Sprite2D
var _capa_rastro: Node2D


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
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 9.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/cienaga/babosa.png")
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -6)
	add_child(_sprite)
	# el rastro se dibuja aparte, por debajo de todo (en el suelo)
	_capa_rastro = Node2D.new()
	_capa_rastro.top_level = true
	_capa_rastro.z_index = -3
	_capa_rastro.draw.connect(_dibujar_rastro)
	add_child(_capa_rastro)
	_rumbo = Vector2.from_angle(randf() * TAU)
	_tiempo = randf() * 3.0
	Sonido.efecto("petrino_aparece", 0.0, global_position, 0.1)


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	_encogida = maxf(0.0, _encogida - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	# el rastro se seca
	for r in _rastro:
		r["t"] += delta
	_rastro = _rastro.filter(func(r: Dictionary) -> bool: return r["t"] < RASTRO_DURA)
	_capa_rastro.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha:
		for r in _rastro:
			if maisha.global_position.distance_to(r["p"]) < 7.0:
				maisha.call("pisar_oxido")
				break
	if _muriendo:
		return
	var mov := Vector2.ZERO
	if _encogida <= 0.0 and _enraizado <= 0.0:
		_cambio -= delta
		if _cambio <= 0.0:
			_cambio = randf_range(1.5, 3.0)
			# a veces va hacia Maisha (despacio), a veces vaga
			if maisha and randf() < 0.55:
				_rumbo = (maisha.global_position - global_position).normalized()
			else:
				_rumbo = Vector2.from_angle(randf() * TAU)
		# se arrastra a impulsos (como una babosa)
		var impulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
		mov = _rumbo * VELOCIDAD * (0.4 + impulso)
		var registro := get_tree().get_first_node_in_group("registro_brotes")
		if registro and registro.hay_brote(R.casilla_de(global_position + _rumbo * 8.0)):
			_rumbo = -_rumbo
			mov = Vector2.ZERO
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
	move_and_slide()
	if get_slide_collision_count() > 0 and mov != Vector2.ZERO:
		_cambio = minf(_cambio, 0.25)          # se ha topado con algo: pronto cambia de rumbo
	if zona:
		global_position = zona.limitar(global_position)
	if global_position.distance_to(_ultimo) > RASTRO_CADA:
		_ultimo = global_position
		_rastro.append({"p": global_position, "t": 0.0})
	if maisha and global_position.distance_to(maisha.global_position) < 10.0 and _encogida <= 0.0:
		if maisha.call("recibir_danio", 1, global_position, "contacto"):
			_empuje = (global_position - maisha.global_position).normalized() * 70.0
	# dibujo
	if _destello > 0.0:
		_sprite.frame = 5
	elif _encogida > 0.0 or _enraizado > 0.0:
		_sprite.frame = 4
	else:
		_sprite.frame = int(_tiempo * 5.0) % 4
	if absf(mov.x) > 0.5:
		_sprite.flip_h = mov.x < 0.0


func _dibujar_rastro() -> void:
	for r in _rastro:
		var vida_r: float = 1.0 - r["t"] / RASTRO_DURA
		var p: Vector2 = r["p"]
		_capa_rastro.draw_circle(p + Vector2(0, -1), 4.0, Color(COLOR_RASTRO, 0.35 * vida_r))
		_capa_rastro.draw_circle(p + Vector2(1, -1), 2.0, Color(0.88, 0.6, 0.36, 0.25 * vida_r))


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_encogida = 0.6
	_empuje = direccion * R.GOLPE_EMPUJE * 0.7
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_encogida = maxf(_encogida, 0.3)


func recibir_danio(cantidad: int, desde: Vector2, _tipo: String) -> void:
	if _muriendo:
		return
	vida -= cantidad
	_destello = 0.1
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
	if vida <= 0:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("babosa", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.position = global_position + Vector2(0, -3)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.4, 0.2), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	t.chain().tween_interval(RASTRO_DURA * 0.5)     # el rastro tarda un poco en secarse
	t.chain().tween_callback(queue_free)
