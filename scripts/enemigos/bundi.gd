extends Node2D
## BUNDI, EL BÚHO-MAGO: un hechicero de Giza. Un búho de piedra con manto de musgo violeta y un bastón de rama.
##   - No pelea cuerpo a cuerpo. Guarda las distancias: si Maisha se le acerca, SE ESFUMA en plumas y aparece en otro
##     sitio de la zona.
##   - CONJURA (aviso: alza el bastón y la gema brilla) y LANZA una bola de Giza lenta que persigue a Maisha
##     (orbe_giza.gd). El Latido la deshace; el ESCUDO (J mantenida) se la DEVUELVE.
##   - Si su propia bola le da, se queda ATONTADO (frame 5) y no puede esfumarse: ahí el cetro le da. Sin atontar,
##     el cetro le quita 1 y se esfuma enseguida. Una explosión le quita 2.
## Dibujo: arte/mundos/raiz/hechiceros/bundi.png (0-1 quieto, 2 conjura, 3 lanza, 4 se esfuma, 5 golpeado).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ORBE := preload("res://scripts/enemigos/orbe_giza.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/raiz/hechiceros/bundi.png")
enum { ESPERA, CONJURA, LANZA, ESFUMA, VUELVE, ATONTADO }

var variante := "raiz"
var zona: Node = null
var vida: int = R.BUNDI_VIDA
var estado := ESPERA
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _visto := false
var _muriendo := false
var _sprite: Sprite2D
var _sombra: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 9.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -14)
	add_child(_sprite)
	_t = R.BUNDI_ESPERA * randf_range(0.5, 1.0)
	_tiempo = randf() * 2.0


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	_t -= delta
	var maisha := _maisha()
	var lejos := global_position.distance_to(maisha.global_position) if maisha else 9999.0
	var activa: bool = maisha != null and not maisha.get("esta_caida")
	match estado:
		ESPERA:
			if activa and lejos < R.BUNDI_VE:
				if not _visto:
					_visto = true
					Sonido.efecto("bundi_ulula", 0.0, global_position)
				if lejos < R.BUNDI_HUYE:
					_esfumarse()
				elif _t <= 0.0:
					estado = CONJURA
					_t = R.BUNDI_CONJURA
					Sonido.efecto("bundi_conjura", 0.0, global_position)
		CONJURA:
			if activa and lejos < R.BUNDI_HUYE * 0.6:
				_esfumarse()
			elif _t <= 0.0:
				_lanzar(maisha)
		LANZA:
			if _t <= 0.0:
				estado = ESPERA
				_t = R.BUNDI_ESPERA
		ESFUMA:
			if _t <= 0.0:
				_reaparecer()
		VUELVE:
			if _t <= 0.0:
				estado = ESPERA
				_t = R.BUNDI_ESPERA * 0.6
		ATONTADO:
			if _t <= 0.0:
				_esfumarse()
	_dibujar()


func _dibujar() -> void:
	modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	match estado:
		CONJURA:
			_sprite.frame = 2
		LANZA:
			_sprite.frame = 3
		ESFUMA, VUELVE:
			_sprite.frame = 4
		ATONTADO:
			_sprite.frame = 5
			_sprite.position.x = sin(_tiempo * 30.0) * 0.8
		_:
			_sprite.frame = int(_tiempo * 1.6) % 2
			_sprite.position.x = 0.0
	# flota un poquito: es un mago
	_sprite.position.y = round(sin(_tiempo * 2.2) * 1.0) if estado != ATONTADO else 0.0
	var maisha := _maisha()
	if maisha:
		_sprite.flip_h = maisha.global_position.x < global_position.x
	queue_redraw()


func _draw() -> void:
	if _muriendo:
		return
	# la gema del bastón echa luz al conjurar; en el suelo, un círculo de runas que gira
	if estado == CONJURA:
		var k := 1.0 - _t / R.BUNDI_CONJURA
		for i in 6:
			var a := _tiempo * 2.0 + i * TAU / 6.0
			var p := Vector2(cos(a) * 11.0, sin(a) * 4.0)
			draw_rect(Rect2(p.round() - Vector2(1, 1), Vector2(2, 2)), Color(0.75, 0.45, 0.95, 0.4 + 0.5 * k))
		draw_circle(Vector2(10 if not _sprite.flip_h else -10, -27), 2.0 + 3.0 * k, Color(0.8, 0.5, 1.0, 0.25 * k))


func _lanzar(maisha: Node2D) -> void:
	estado = LANZA
	_t = 0.35
	Sonido.efecto("bundi_lanza", 0.0, global_position)
	var orbe: Node2D = ORBE.new()
	orbe.dueno = self
	orbe.position = global_position + Vector2(-9 if _sprite.flip_h else 9, -24)
	if maisha:
		orbe.direccion = (maisha.global_position + Vector2(0, -8) - orbe.position).normalized()
	get_parent().add_child(orbe)


func _esfumarse() -> void:
	estado = ESFUMA
	_t = R.BUNDI_ESFUMA
	Sonido.efecto("bundi_esfuma", 0.0, global_position)
	remove_from_group("golpeables")
	remove_from_group("daniables")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 6
	astillas.position = global_position + Vector2(0, -10)
	get_parent().add_child(astillas)
	create_tween().tween_property(self, "modulate:a", 0.0, R.BUNDI_ESFUMA)


## Aparece lejos de Maisha, dentro de la zona
func _reaparecer() -> void:
	var maisha := _maisha()
	var centro: Vector2 = zona.global_position if zona else global_position
	var radios: Vector2 = zona.get("radios_umbral") * 0.65 if zona else Vector2(60, 40)
	var mejor := global_position
	for intento in 14:
		var p := centro + Vector2(randf_range(-1, 1) * radios.x, randf_range(-1, 1) * radios.y)
		if zona:
			p = zona.limitar(p)
		elif maisha:
			p = maisha.global_position + Vector2.from_angle(randf() * TAU) * randf_range(90.0, 120.0)
		mejor = p
		if maisha == null or p.distance_to(maisha.global_position) > 80.0:
			break
	global_position = mejor
	estado = VUELVE
	_t = R.BUNDI_ESFUMA
	add_to_group("golpeables")
	add_to_group("daniables")
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, R.BUNDI_ESFUMA)
	Sonido.efecto("bundi_esfuma", 0.0, global_position, 0.1)


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or estado in [ESFUMA, VUELVE]:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or estado in [ESFUMA, VUELVE]:
		return
	vida -= cantidad
	_destello = 0.12
	Impacto.temblar(1.0, 0.1)
	if vida <= 0:
		morir()
		return
	Sonido.efecto("petrino_golpeado", 0.0, global_position)
	if tipo == "magia":
		# su propia bola: se queda atontado, sin poder irse
		estado = ATONTADO
		_t = R.BUNDI_ATONTADO
	elif estado != ATONTADO:
		get_tree().create_timer(0.15, false).timeout.connect(func() -> void:
			if is_instance_valid(self) and not _muriendo and estado != ATONTADO:
				_esfumarse())


## Las raíces de una semilla lo sujetan: no puede esfumarse mientras tanto
func enraizar(segundos: float) -> void:
	if estado in [ESPERA, CONJURA, LANZA]:
		estado = ATONTADO
		_t = maxf(_t, segundos)


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("bundi", self)
	Sonido.efecto("bundi_esfuma", 0.0, global_position)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = 5
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -10)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.2), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
