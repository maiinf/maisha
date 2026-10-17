extends CharacterBody2D
## TINTERO RABIOSO (Sigilia, Las Estanterías Colgantes): el «cazador» de Sigilia. Un tintero de cristal lleno de
## tinta de Giza, con patitas y muy mal genio.
##   - Deambula despacio. Si ve a Maisha en su misma fila o columna (y no muy lejos), se agacha un instante (el aviso)
##     y EMBISTE en línea recta, dejando detrás MANCHAS DE TINTA que pringan (frenan a Maisha un rato).
##   - Al chocar con algo se queda ATURDIDO (bizco, con el tapón torcido): es el momento de golpearle.
##   - 3 golpes de cetro; una semilla, 2; EL SIGILO DE FUEGO le hace 2 (la tinta hierve).
## Dibujo: arte/mundos/sigilia/estanterias/tintero.png (herramientas/pintar_estanterias.py).

const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/estanterias/tintero.png")
const MANCHA := preload("res://arte/mundos/sigilia/estanterias/mancha.png")

const VIDA := 3
const VELOCIDAD := 20.0
const EMBESTIDA := 150.0
const VE_A := 140.0
const ALINEADO := 9.0
const PREPARA := 0.6
const ATURDIDO := 1.4
const DESCANSO := 1.0
const DURA_MANCHA := 6.0

enum Fase { ANDAR, PREPARAR, EMBESTIR, ATURDIDO }

var zona: Node = null
var vida := VIDA
var fase := Fase.ANDAR
var _t := 0.0
var _dir := Vector2.RIGHT
var _rumbo := Vector2.ZERO
var _cambio := 0.0
var _descanso := 0.0
var _enraizado := 0.0
var _destello := 0.0
var _empuje := Vector2.ZERO
var _tiempo := 0.0
var _ultima_mancha := Vector2.INF
var _manchas: Array[Dictionary] = []      # {pos (global), t}
var _muriendo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("tinteros")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = 6.0
	forma.shape = c
	forma.position = Vector2(0, -4)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 7.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -11)
	add_child(_sprite)
	_tiempo = randf() * 3.0


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_descanso = maxf(0.0, _descanso - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mov := Vector2.ZERO
	match fase:
		Fase.ANDAR:
			_cambio -= delta
			if _cambio <= 0.0:
				_cambio = randf_range(1.2, 2.5)
				_rumbo = [Vector2.RIGHT, Vector2.LEFT, Vector2.UP, Vector2.DOWN, Vector2.ZERO].pick_random()
			mov = _rumbo * VELOCIDAD
			if maisha and _descanso <= 0.0 and _enraizado <= 0.0 and not maisha.get("esta_caida"):
				var d := maisha.global_position - global_position
				if d.length() < VE_A and (absf(d.x) < ALINEADO or absf(d.y) < ALINEADO):
					_dir = Vector2(signf(d.x), 0) if absf(d.y) < ALINEADO else Vector2(0, signf(d.y))
					_cambiar(Fase.PREPARAR)
		Fase.PREPARAR:
			if _t >= PREPARA:
				_cambiar(Fase.EMBESTIR)
				Sonido.efecto("jabali_grunido", -2.0, global_position, 0.25)
		Fase.EMBESTIR:
			mov = _dir * EMBESTIDA
			if global_position.distance_to(_ultima_mancha) > 14.0:
				_ultima_mancha = global_position
				_manchas.append({"pos": global_position, "t": 0.0})
		Fase.ATURDIDO:
			if _t >= ATURDIDO:
				_cambiar(Fase.ANDAR)
				_descanso = DESCANSO
	if _enraizado > 0.0:
		mov = Vector2.ZERO
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 500.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	if fase == Fase.EMBESTIR and (get_slide_collision_count() > 0 or _t > 2.5):
		_cambiar(Fase.ATURDIDO)
		Sonido.efecto("clinc", -2.0, global_position)
		Impacto.temblar(1.5, 0.12)
	# al tocar a Maisha, le hace daño (más si embiste)
	if maisha and fase != Fase.ATURDIDO and global_position.distance_to(maisha.global_position) < 12.0:
		maisha.call("recibir_danio", 2 if fase == Fase.EMBESTIR else 1, global_position, "contacto")
	# las manchas: pringan a Maisha si las pisa, y se secan
	for m in _manchas:
		m["t"] += delta
		if maisha and (m["pos"] as Vector2).distance_to(maisha.global_position) < 10.0:
			maisha.call("pisar_oxido", 0.3)
	_manchas = _manchas.filter(func(m: Dictionary) -> bool: return m["t"] < DURA_MANCHA)
	# el dibujo
	if _destello > 0.0:
		_sprite.frame = 5
	elif fase == Fase.ATURDIDO:
		_sprite.frame = 4
	elif fase == Fase.EMBESTIR:
		_sprite.frame = 3
	elif fase == Fase.PREPARAR:
		_sprite.frame = 2
	else:
		_sprite.frame = int(_tiempo * 6.0) % 2 if mov != Vector2.ZERO else 0
	if fase == Fase.EMBESTIR or mov.x != 0.0:
		_sprite.flip_h = (_dir.x if fase == Fase.EMBESTIR else mov.x) > 0.0
	queue_redraw()


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _draw() -> void:
	for m in _manchas:
		var a: float = clampf((DURA_MANCHA - float(m["t"])) / 1.5, 0.0, 1.0)
		draw_texture(MANCHA, (m["pos"] as Vector2) - global_position - Vector2(16, 8), Color(1, 1, 1, a))


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_empuje = direccion * 70.0
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_cambiar(Fase.ATURDIDO)


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	vida -= 2 if tipo in ["explosion", "fuego"] else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -10), Vector2.UP, Color("8a70c0"))
	if vida > 0:
		Sonido.efecto("petrino_golpeado", -2.0, global_position)
		if fase != Fase.EMBESTIR:
			_cambiar(Fase.ATURDIDO)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("tintero", self)
	Sonido.efecto("cristal", -2.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	remove_from_group("tinteros")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.3), 0.25)
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.chain().tween_callback(queue_free)
