extends CharacterBody2D
## TOPO DE PIEDRA: el enemigo del Camino Cobrizo. Un topo de roca con grietas de Giza y zarpas de cavar.
##   - Va BAJO TIERRA: solo se ve un montoncito de tierra que avanza (y el rastro que deja). Ahí no se le puede dar.
##   - Si oye a Maisha cerca, va a por ella. Cuando la alcanza (o se cansa de buscar), se para: el suelo TIEMBLA y
##     se agrieta donde va a salir (aviso) y SALE de golpe con un mordisco que hace daño si Maisha está encima.
##   - Al salir se queda ATONTADO, fuera, un momento: ahí el cetro le quita 2. Luego se vuelve a HUNDIR.
##   - Las raíces de una semilla lo sacan a la fuerza aunque esté bajo tierra (y sale atontado); la explosión le
##     quita 2. El Latido lo empuja si está fuera.
## Dibujo: arte/mundos/raiz/camino/topo.png (herramientas/pintar_camino.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIOLETA := Color("a855d6")
const TIERRA := [Color("2b1e17"), Color("533b2d"), Color("7c5843"), Color("a57559")]

enum Fase { BAJO, AVISO, SALE, ATONTADO, HUNDE }

var variante := "raiz"
var zona: Node = null
var vida := R.TOPO_VIDA
var fase := Fase.BAJO
var _t := 0.0
var _tiempo := 0.0
var _espera := 0.6
var _busca := 0.0
var _rumbo := Vector2.ZERO
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _sombra: Node2D
var _suelo: Node2D               # el montoncito, el rastro y las grietas del aviso (debajo de todo)
var _rastro: Array[Dictionary] = []
var _paso_rastro := 0.0


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 0
	collision_mask = 0
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_suelo = Node2D.new()
	_suelo.top_level = true
	_suelo.z_index = -3
	_suelo.draw.connect(_dibujar_suelo)
	add_child(_suelo)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 9.0)
	_sombra.visible = false
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/camino/topo.png")
	_sprite.hframes = 6
	_sprite.centered = false
	_sprite.offset = Vector2(-12, -21)
	_sprite.visible = false
	add_child(_sprite)
	_tiempo = randf() * 3.0
	_espera = randf_range(0.4, 1.0)
	_rumbo = Vector2.from_angle(randf() * TAU)
	Sonido.efecto("topo_excava", 0.0, global_position, 0.15)


func bajo_tierra() -> bool:
	return fase in [Fase.BAJO, Fase.AVISO]


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	var fuera := not bajo_tierra()
	_sprite.visible = fuera
	_sombra.visible = fuera
	collision_layer = 2 if fuera else 0
	collision_mask = 1 if fuera else 0


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_rastro = _rastro.filter(func(r: Dictionary) -> bool: return _tiempo - float(r["t"]) < 1.6)
	if _muriendo:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	match fase:
		Fase.BAJO:
			if _enraizado > 0.0:
				# las raíces de la semilla lo sacan a la fuerza
				_salir(maisha, false)
			else:
				_espera -= delta
				if _espera <= 0.0:
					var cerca := maisha and maisha.global_position.distance_to(global_position) < R.TOPO_VE
					var dir := _rumbo
					if cerca:
						_busca += delta
						dir = (maisha.global_position - global_position).normalized()
					else:
						_busca = 0.0
						_rumbo = _rumbo.rotated(sin(_tiempo * 1.7) * delta * 2.0)
					var antes := global_position
					global_position = _limitar(global_position + dir * R.TOPO_VELOCIDAD * (1.0 if cerca else 0.45) * delta)
					if global_position.distance_to(antes) < R.TOPO_VELOCIDAD * 0.2 * delta and not cerca:
						_rumbo = -_rumbo.rotated(randf_range(-0.8, 0.8))
					_paso_rastro -= global_position.distance_to(antes)
					if _paso_rastro <= 0.0:
						_paso_rastro = 5.0
						_rastro.append({"pos": global_position + Vector2(randf_range(-2, 2), randf_range(-1, 1)), "t": _tiempo})
					if cerca and (maisha.global_position.distance_to(global_position) < 8.0 or _busca > R.TOPO_BUSCA):
						_busca = 0.0
						_cambiar(Fase.AVISO)
						Sonido.efecto("topo_excava", 0.0, global_position)
		Fase.AVISO:
			if _t >= R.TOPO_AVISO or _enraizado > 0.0:
				_salir(maisha, _enraizado <= 0.0)
		Fase.SALE:
			if _t >= 0.28:
				_cambiar(Fase.ATONTADO)
		Fase.ATONTADO:
			if _t >= R.TOPO_ATONTADO and _enraizado <= 0.0:
				_cambiar(Fase.HUNDE)
				Sonido.efecto("topo_excava", 0.0, global_position)
		Fase.HUNDE:
			if _t >= 0.4:
				_espera = R.TOPO_ESPERA
				_cambiar(Fase.BAJO)
	if not bajo_tierra():
		velocity = _empuje
		_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
		move_and_slide()
		global_position = _limitar(global_position)
	_animar()
	_suelo.queue_redraw()


func _limitar(p: Vector2) -> Vector2:
	return zona.limitar(p) if zona else p


## Sale de la tierra: con mordisco (si ha avisado) o arrancado por las raíces (atontado directamente)
func _salir(maisha: Node2D, morder: bool) -> void:
	Sonido.efecto("topo_sale", 0.0, global_position)
	Impacto.temblar(1.5 if morder else 0.8, 0.15)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 7
	astillas.fuerza = 55.0
	astillas.position = global_position
	get_parent().add_child(astillas)
	if morder:
		_cambiar(Fase.SALE)
		if maisha and maisha.global_position.distance_to(global_position) < R.TOPO_MORDISCO:
			maisha.call("recibir_danio", 1, global_position, "contacto")
	else:
		_cambiar(Fase.ATONTADO)


func _animar() -> void:
	var frame := 1
	match fase:
		Fase.SALE:
			frame = 2
			_sprite.position.y = -sin(clampf(_t / 0.28, 0.0, 1.0) * PI) * 6.0
		Fase.ATONTADO:
			frame = 3 if _t < 0.2 or fmod(_t, 0.6) < 0.45 else 1
			_sprite.position = Vector2(sin(_t * 9.0) * 0.8, 0)
			_sprite.rotation = sin(_t * 7.0) * 0.06
		Fase.HUNDE:
			frame = 0 if _t < 0.2 else 4
			_sprite.position = Vector2(0, _t * 6.0)
	if fase != Fase.ATONTADO:
		_sprite.rotation = 0.0
	if fase == Fase.SALE or fase == Fase.ATONTADO:
		if fase == Fase.SALE:
			_sprite.position.x = 0.0
	if _destello > 0.0:
		frame = 5
	_sprite.frame = frame
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and absf(maisha.global_position.x - global_position.x) > 2.0:
		_sprite.flip_h = maisha.global_position.x < global_position.x


## Bajo tierra: el rastro de tierra removida, el montoncito que avanza y, al avisar, las grietas que se abren
func _dibujar_suelo() -> void:
	for r in _rastro:
		var vida := 1.0 - (_tiempo - float(r["t"])) / 1.6
		var p: Vector2 = Vector2(r["pos"]).round()
		_suelo.draw_rect(Rect2(p + Vector2(-2, -1), Vector2(4, 2)), Color(TIERRA[1], 0.55 * vida))
		_suelo.draw_rect(Rect2(p + Vector2(-1, -2), Vector2(2, 1)), Color(TIERRA[2], 0.5 * vida))
	if not bajo_tierra() and fase != Fase.HUNDE:
		return
	var c := global_position.round()
	if fase == Fase.BAJO or fase == Fase.AVISO:
		# el montoncito: tres hileras de tierra con luz arriba, que tiembla un poco al avanzar
		var vaiven := roundf(sin(_tiempo * 14.0) * 0.6)
		_suelo.draw_rect(Rect2(c + Vector2(-6, -1), Vector2(12, 3)), TIERRA[0])
		_suelo.draw_rect(Rect2(c + Vector2(-5, -3 + vaiven), Vector2(10, 3)), TIERRA[1])
		_suelo.draw_rect(Rect2(c + Vector2(-3, -5 + vaiven), Vector2(6, 3)), TIERRA[2])
		_suelo.draw_rect(Rect2(c + Vector2(-2, -5 + vaiven), Vector2(3, 1)), TIERRA[3])
		for k in 3:
			var a := _tiempo * 6.0 + k * 2.1
			_suelo.draw_rect(Rect2(c + Vector2(cos(a) * 6.0, -3.0 - absf(sin(a)) * 3.0).round(), Vector2.ONE), TIERRA[2])
	if fase == Fase.AVISO:
		# las grietas que se abren donde va a salir, con un brillo violeta
		var f := clampf(_t / R.TOPO_AVISO, 0.0, 1.0)
		for k in 6:
			var a := TAU * k / 6.0 + 0.3
			var largo := 4.0 + f * 10.0
			var p0 := c + Vector2(cos(a), sin(a) * 0.5) * 3.0
			var p1 := c + Vector2(cos(a + 0.2), sin(a + 0.2) * 0.5) * largo
			_suelo.draw_line(p0, p1, Color(0.05, 0.03, 0.06, 0.8), 1.0)
		_suelo.draw_arc(c, R.TOPO_MORDISCO * (1.2 - f * 0.4), 0, TAU, 24, Color(VIOLETA, 0.35 + 0.35 * sin(_tiempo * 20.0)), 1.0)


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo or bajo_tierra():
		return false
	var atontado := fase == Fase.ATONTADO
	_empuje = direccion * R.GOLPE_EMPUJE * (0.8 if atontado else 0.4)
	recibir_danio(danio + (1 if atontado else 0), global_position - direccion * 10.0, "golpe")
	if not atontado and not _muriendo and fase != Fase.HUNDE:
		# se mete bajo tierra para escapar
		_cambiar(Fase.HUNDE)
		Sonido.efecto("topo_excava", 0.0, global_position)
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	if not bajo_tierra():
		_empuje = fuerza


func recibir_danio(cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	if _muriendo or (bajo_tierra() and tipo != "explosion"):
		return
	vida -= cantidad + (1 if tipo == "explosion" else 0)
	_destello = 0.12
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
		if bajo_tierra():
			_salir(null, false)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("topo", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_suelo.queue_free()
	_sprite.visible = true
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.chispas = 4
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.3), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
