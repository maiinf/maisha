extends CharacterBody2D
## CUERVO DE ÓXIDO: el enemigo de la Senda de los Surcos. Un cuervo de plumas de hierro con un ojo de Giza.
##   - VUELA en círculos, alto (solo se ve su sombra en el suelo justo debajo): ahí no se le puede dar.
##   - Cuando tiene a Maisha cerca, se para en el aire y APUNTA: en el suelo sale una raya violeta que marca por
##     dónde va a pasar. Luego se lanza EN PICADO en línea recta, rasante, y hace daño a quien esté en la raya.
##   - Al acabar el picado se queda POSADO picoteando el suelo: ahí el cetro le quita 2. Luego vuelve a subir.
##   - Las raíces de una semilla lo sujetan si está posado (no puede despegar). La explosión le da aunque vuele.
## Dibujo: arte/mundos/raiz/senda/cuervo.png (herramientas/pintar_senda.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIOLETA := Color("a855d6")

enum Fase { VUELA, APUNTA, PICADO, POSADO, DESPEGA }

var variante := "raiz"
var zona: Node = null
var vida := R.CUERVO_VIDA
var fase := Fase.VUELA
var _t := 0.0
var _tiempo := 0.0
var _espera := 1.0
var _centro := Vector2.ZERO        # alrededor de qué da vueltas
var _angulo := 0.0
var _desde := Vector2.ZERO
var _hasta := Vector2.ZERO
var _alto := R.CUERVO_ALTURA
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _muriendo := false
var _ya_pico := false
var _sprite: Sprite2D
var _sombra: Node2D
var _marca: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 0
	collision_mask = 0
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_marca = Node2D.new()
	_marca.top_level = true
	_marca.z_index = -3
	_marca.draw.connect(_dibujar_marca)
	add_child(_marca)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 8.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/senda/cuervo.png")
	_sprite.hframes = 6
	_sprite.centered = false
	_sprite.offset = Vector2(-13, -21)
	add_child(_sprite)
	_centro = global_position
	_angulo = randf() * TAU
	_espera = randf_range(0.8, 1.6)
	Sonido.efecto("cuervo_graznido", 0.0, global_position, 0.15)


func en_el_aire() -> bool:
	return fase in [Fase.VUELA, Fase.APUNTA, Fase.DESPEGA] or (fase == Fase.PICADO and _alto > 8.0)


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	var en_suelo := nueva == Fase.POSADO
	collision_layer = 2 if en_suelo else 0
	collision_mask = 1 if en_suelo else 0


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	if _muriendo:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	match fase:
		Fase.VUELA:
			_alto = move_toward(_alto, R.CUERVO_ALTURA, 60.0 * delta)
			_angulo += delta * 1.3
			var hacia := _limitar(_centro + Vector2(cos(_angulo) * 46.0, sin(_angulo) * 26.0))
			global_position = global_position.move_toward(hacia, R.CUERVO_VUELO * delta)
			_espera -= delta
			if maisha:
				var lejos := maisha.global_position.distance_to(global_position)
				if lejos < R.CUERVO_VE * 1.6:
					_centro = _centro.move_toward(maisha.global_position, 30.0 * delta)
				if _espera <= 0.0 and lejos < R.CUERVO_VE:
					# apunta: la raya pasa por donde está Maisha y sigue un poco más allá
					var dir := (maisha.global_position - global_position).normalized()
					_desde = global_position
					_hasta = _limitar(maisha.global_position + dir * 36.0)
					_cambiar(Fase.APUNTA)
					Sonido.efecto("cuervo_graznido", 0.0, global_position)
		Fase.APUNTA:
			_alto = move_toward(_alto, R.CUERVO_ALTURA + 6.0, 40.0 * delta)
			if _t >= R.CUERVO_APUNTA:
				_ya_pico = false
				_cambiar(Fase.PICADO)
				Sonido.efecto("cuervo_picado", 0.0, global_position)
		Fase.PICADO:
			var dura := maxf(0.15, _desde.distance_to(_hasta) / R.CUERVO_PICADO)
			var f := clampf(_t / dura, 0.0, 1.0)
			global_position = _desde.lerp(_hasta, f)
			_alto = lerpf(R.CUERVO_ALTURA + 6.0, 2.0, clampf(f * 3.0, 0.0, 1.0))
			if not _ya_pico and maisha and _alto < 10.0 and maisha.global_position.distance_to(global_position) < 11.0:
				_ya_pico = true
				if maisha.call("recibir_danio", 1, global_position, "contacto"):
					_empuje = Vector2.ZERO
			if f >= 1.0:
				_alto = 0.0
				_cambiar(Fase.POSADO)
				var astillas: Node2D = ASTILLAS.new()
				astillas.cantidad = 4
				astillas.fuerza = 35.0
				astillas.position = global_position
				get_parent().add_child(astillas)
		Fase.POSADO:
			if _t >= R.CUERVO_POSADO and _enraizado <= 0.0:
				_cambiar(Fase.DESPEGA)
				Sonido.efecto("cuervo_graznido", 0.0, global_position)
		Fase.DESPEGA:
			_alto = lerpf(0.0, R.CUERVO_ALTURA, clampf(_t / 0.5, 0.0, 1.0))
			if _t >= 0.5:
				_centro = global_position
				_espera = R.CUERVO_ESPERA
				_cambiar(Fase.VUELA)
	if fase == Fase.POSADO:
		velocity = _empuje
		_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
		move_and_slide()
		global_position = _limitar(global_position)
	_animar()
	_marca.queue_redraw()


func _limitar(p: Vector2) -> Vector2:
	return zona.limitar(p) if zona else p


func _animar() -> void:
	var frame := 0
	match fase:
		Fase.VUELA, Fase.DESPEGA:
			frame = 0 if fmod(_tiempo * (6.0 if fase == Fase.DESPEGA else 4.0), 1.0) < 0.5 else 1
		Fase.APUNTA:
			frame = 0 if fmod(_tiempo * 9.0, 1.0) < 0.5 else 1
		Fase.PICADO:
			frame = 2
		Fase.POSADO:
			frame = 3 if fmod(_t, 0.5) < 0.3 else 4
			if _enraizado > 0.0:
				frame = 4
	if _destello > 0.0:
		frame = 5
	_sprite.frame = frame
	_sprite.position.y = -_alto + (sin(_tiempo * 4.0) * 1.5 if fase == Fase.VUELA else 0.0)
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	var mira := 0.0
	if fase in [Fase.APUNTA, Fase.PICADO]:
		mira = _hasta.x - _desde.x
	elif fase == Fase.VUELA:
		mira = -sin(_angulo)
	if absf(mira) > 0.01:
		_sprite.flip_h = mira < 0.0
	# la sombra se encoge cuanto más alto va
	_sombra.scale = Vector2.ONE * (1.0 - clampf(_alto / 60.0, 0.0, 0.5))


func _dibujar_marca() -> void:
	# por dónde va a pasar: una raya violeta en el suelo que parpadea más deprisa justo antes de lanzarse
	if fase != Fase.APUNTA:
		return
	var f := clampf(_t / R.CUERVO_APUNTA, 0.0, 1.0)
	var a := 0.25 + 0.35 * f + 0.2 * sin(_tiempo * (10.0 + f * 20.0))
	var dir := (_hasta - _desde).normalized()
	var normal := Vector2(-dir.y, dir.x)
	var largo := _desde.distance_to(_hasta)
	var pasos := int(largo / 3.0)
	for i in pasos:
		var p := _desde + dir * (i * 3.0)
		if i * 3.0 > largo * f + 10.0:
			break
		_marca.draw_rect(Rect2((p + normal * 3.0).round(), Vector2.ONE * 2), Color(0.05, 0.03, 0.08, a * 0.7))
		_marca.draw_rect(Rect2((p - normal * 3.0).round(), Vector2.ONE * 2), Color(0.05, 0.03, 0.08, a * 0.7))
		_marca.draw_rect(Rect2(p.round() - Vector2.ONE, Vector2.ONE * 2), Color(VIOLETA, minf(1.0, a + 0.25)))
		_marca.draw_rect(Rect2(p.round(), Vector2.ONE), Color(1.0, 0.85, 1.0, a * 0.8))
	_marca.draw_arc(_hasta, 6.0, 0, TAU, 16, Color(VIOLETA, a), 1.0)


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo or en_el_aire():
		return false
	_empuje = direccion * R.GOLPE_EMPUJE * 0.6
	recibir_danio(danio + 1, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	if fase == Fase.POSADO:
		_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	if fase == Fase.POSADO:
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
	Bestiario.vencido("cuervo", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_marca.queue_free()
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.chispas = 4
	astillas.position = global_position + Vector2(0, -6 - _alto)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.3), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
