extends CharacterBody2D
## MURCIÉLAGO DE ECO: el enemigo de la Cañada del Eco. Un murciélago de piedra con las alas rotas de Giza.
##   - Aparece COLGADO boca abajo y despierta con un chillido.
##   - REVOLOTEA en zigzag, a media altura, cerca de Maisha: en el aire el cetro no le da.
##   - AVISA: se para, abre las alas y se le carga un anillo; en el suelo sale la línea por donde irá el grito.
##   - GRITA: suelta una ONDA (onda_eco.gd) que va en línea recta y VUELVE a él, como un eco. Hace daño a la ida y
##     a la vuelta. El Latido la deshace.
##   - Al tragarse su propio eco se queda ATURDIDO en el suelo: ahí el cetro le quita 2. Luego vuelve a volar.
##   - Las raíces de una semilla lo sujetan si está en el suelo. La explosión le da aunque vuele.
## Dibujo: arte/mundos/raiz/canada/murcielago.png (herramientas/pintar_canada.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const ONDA := preload("res://scripts/enemigos/onda_eco.gd")
const VIOLETA := Color("a855d6")

enum Fase { COLGADO, REVOLOTEA, AVISA, GRITA, ATURDIDO, DESPEGA }

var variante := "raiz"
var zona: Node = null
var vida := R.MURCIELAGO_VIDA
var fase := Fase.COLGADO
var _t := 0.0
var _tiempo := 0.0
var _espera := 1.0
var _hacia := Vector2.ZERO          # adónde revolotea ahora
var _direccion := Vector2.RIGHT     # hacia dónde gritará
var _alto := R.MURCIELAGO_ALTURA
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _muriendo := false
var _onda: Node2D = null
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
	_sombra.set("ancho", 7.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/canada/murcielago.png")
	_sprite.hframes = 6
	_sprite.centered = false
	_sprite.offset = Vector2(-12, -18)
	add_child(_sprite)
	_hacia = global_position
	_espera = randf_range(0.9, 1.5)


func en_el_aire() -> bool:
	return fase != Fase.ATURDIDO


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	var en_suelo := nueva == Fase.ATURDIDO
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
		Fase.COLGADO:
			if _t >= R.MURCIELAGO_DESPIERTA:
				Sonido.efecto("murcielago_chillido", 0.0, global_position, 0.2)
				_cambiar(Fase.DESPEGA)
		Fase.DESPEGA:
			_alto = move_toward(_alto, R.MURCIELAGO_ALTURA, 70.0 * delta)
			if _t < delta * 1.5:
				Sonido.efecto("murcielago_aleteo", 0.0, global_position, 0.2)
			if _t >= 0.4 and absf(_alto - R.MURCIELAGO_ALTURA) < 0.5:
				_espera = R.MURCIELAGO_ESPERA
				_cambiar(Fase.REVOLOTEA)
		Fase.REVOLOTEA:
			# zigzag: elige un punto cerca de Maisha (ni encima ni lejos) y va a por él a tirones
			if global_position.distance_to(_hacia) < 4.0 or _t > 0.7:
				_t = 0.0
				var centro := maisha.global_position if maisha else global_position
				var ang := randf() * TAU
				_hacia = _limitar(centro + Vector2(cos(ang), sin(ang) * 0.7) * randf_range(40.0, 70.0))
			global_position = global_position.move_toward(_hacia, R.MURCIELAGO_VUELO * delta)
			_espera -= delta
			if maisha and _espera <= 0.0 and maisha.global_position.distance_to(global_position) < R.MURCIELAGO_VE:
				_direccion = (maisha.global_position - global_position).normalized()
				_cambiar(Fase.AVISA)
				Sonido.efecto("murcielago_chillido", -4.0, global_position, 0.15)
		Fase.AVISA:
			if maisha and _t < R.MURCIELAGO_AVISO * 0.5:
				_direccion = (maisha.global_position - global_position).normalized()    # apunta hasta la mitad
			if _t >= R.MURCIELAGO_AVISO:
				_gritar()
		Fase.GRITA:
			# quieto en el aire mientras la onda va y vuelve; al tragársela, se marea y cae
			if not is_instance_valid(_onda):
				_onda = null                       # (el Latido la deshizo: no se marea)
				_cambiar(Fase.DESPEGA)
		Fase.ATURDIDO:
			_alto = move_toward(_alto, 0.0, 120.0 * delta)
			if _t >= R.MURCIELAGO_ATURDIDO and _enraizado <= 0.0:
				_cambiar(Fase.DESPEGA)
	if fase == Fase.ATURDIDO:
		velocity = _empuje
		_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
		move_and_slide()
		global_position = _limitar(global_position)
	_animar()
	_marca.queue_redraw()


func _gritar() -> void:
	_cambiar(Fase.GRITA)
	Sonido.efecto("murcielago_grito", 0.0, global_position, 0.1)
	Impacto.temblar(0.8, 0.12)
	_onda = ONDA.new()
	_onda.direccion = _direccion
	_onda.dueno = self
	_onda.alcance = R.MURCIELAGO_ALCANCE
	_onda.zona = zona
	_onda.global_position = global_position
	get_parent().add_child(_onda)


## La onda vuelve a él: se la traga y se marea (la llama onda_eco.gd)
func tragar_eco() -> void:
	if _muriendo:
		return
	_onda = null
	_alto = maxf(_alto, 6.0)
	_cambiar(Fase.ATURDIDO)
	Sonido.efecto("murcielago_mareo", 0.0, global_position, 0.1)


func _limitar(p: Vector2) -> Vector2:
	return zona.limitar(p) if zona else p


func _animar() -> void:
	var frame := 1
	match fase:
		Fase.COLGADO:
			frame = 0
		Fase.REVOLOTEA, Fase.DESPEGA:
			frame = 1 if fmod(_tiempo * 9.0, 1.0) < 0.5 else 2
		Fase.AVISA:
			frame = 3 if fmod(_tiempo * 14.0, 1.0) < 0.5 else 1
		Fase.GRITA:
			frame = 3
		Fase.ATURDIDO:
			frame = 4
	if _destello > 0.0:
		frame = 5
	_sprite.frame = frame
	var aleteo := sin(_tiempo * 9.0) * 1.5 if fase in [Fase.REVOLOTEA, Fase.AVISA, Fase.GRITA] else 0.0
	_sprite.position.y = -_alto + aleteo
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	if fase in [Fase.AVISA, Fase.GRITA]:
		_sprite.flip_h = _direccion.x < 0.0
	elif fase == Fase.REVOLOTEA and absf(_hacia.x - global_position.x) > 1.0:
		_sprite.flip_h = _hacia.x < global_position.x
	_sombra.scale = Vector2.ONE * (1.0 - clampf(_alto / 60.0, 0.0, 0.5))


func _dibujar_marca() -> void:
	if fase == Fase.ATURDIDO:
		# mareado: tres estrellitas que dan vueltas sobre la cabeza
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := global_position + Vector2(cos(a) * 7.0, -14.0 - _alto + sin(a) * 2.5)
			var c := Color(1.0, 0.95, 0.6, 0.9)
			_marca.draw_rect(Rect2(p.round() - Vector2(1, 0), Vector2(3, 1)), c)
			_marca.draw_rect(Rect2(p.round() - Vector2(0, 1), Vector2(1, 3)), c)
		return
	# el aviso: un anillo que se cierra alrededor del murciélago y, en el suelo, la línea del grito (ida y vuelta)
	if fase != Fase.AVISA:
		return
	var f := clampf(_t / R.MURCIELAGO_AVISO, 0.0, 1.0)
	var a := 0.45 + 0.4 * f + 0.15 * sin(_tiempo * (12.0 + f * 24.0))
	var arriba := global_position + Vector2(0, -_alto - 8)
	_marca.draw_arc(arriba, 16.0 - f * 9.0, 0, TAU, 24, Color(VIOLETA, a), 2.0)
	_marca.draw_arc(arriba, 16.0 - f * 9.0, 0, TAU, 24, Color(1.0, 1.0, 1.0, a * 0.8), 1.0)
	var largo := R.MURCIELAGO_ALCANCE * f
	var n := Vector2(-_direccion.y, _direccion.x)
	var pasos := int(largo / 4.0)
	for i in pasos:
		var p := global_position + _direccion * (i * 4.0 + 6.0)
		_marca.draw_rect(Rect2((p + n * 2.0).round() - Vector2.ONE, Vector2.ONE * 2), Color(0.05, 0.03, 0.08, a * 0.6))
		_marca.draw_rect(Rect2((p - n * 2.0).round() - Vector2.ONE, Vector2.ONE * 2), Color(0.05, 0.03, 0.08, a * 0.6))
		_marca.draw_rect(Rect2(p.round() - Vector2.ONE, Vector2.ONE * 2), Color(1.0, 1.0, 1.0, a))
		if i % 3 == 0:
			_marca.draw_rect(Rect2((p + n * 4.0).round(), Vector2.ONE), Color(VIOLETA, a))
			_marca.draw_rect(Rect2((p - n * 4.0).round(), Vector2.ONE), Color(VIOLETA, a))
	# al final, una muesca: ahí rebota y vuelve
	var fin := global_position + _direccion * (largo + 6.0)
	_marca.draw_arc(fin, 4.0, _direccion.angle() - 1.6, _direccion.angle() + 1.6, 8, Color(1.0, 1.0, 1.0, a), 1.0)


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo or en_el_aire():
		return false
	_empuje = direccion * R.GOLPE_EMPUJE * 0.6
	recibir_danio(danio + 1, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	if fase == Fase.ATURDIDO:
		_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	if fase == Fase.ATURDIDO:
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
	if is_instance_valid(_onda):
		_onda.disipar()
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
