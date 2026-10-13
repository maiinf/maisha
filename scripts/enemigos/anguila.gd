extends Node2D
## ANGUILA DE ÓXIDO: el enemigo de La Travesía. Sale del río por un lado del transbordador y cruza la cubierta de un
## SALTO en arco hasta el otro lado (una sombra marca por dónde va a pasar). Si cae encima de Maisha, le hace daño.
##   - Un golpe de cetro mientras salta la tumba: cae a la cubierta ATURDIDA, coleteando, y el cetro le quita vida.
##   - Si no, se zambulle por el otro lado y vuelve a saltar (tres veces); luego se cansa y se va.
## Vive en coordenadas de la barca (viaje.gd): se mueve con ella. Dibujo: arte/mundos/raiz/travesia/anguila.png.

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const SALTO := 1.0                         # segundos en el aire
const AVISO := 0.7                         # la sombra avisa antes de saltar
const ATURDIDA := 2.4

enum Fase { AVISA, SALTA, BUCEA, ATURDIDA, FUERA }

var viaje: Node2D
var vida := 2
var fase: int = Fase.AVISA
var _t := 0.0
var _tiempo := 0.0
var _desde := Vector2.ZERO                 # (en coordenadas de la barca)
var _hasta := Vector2.ZERO
var _local := Vector2.ZERO
var _saltos := 3
var _blanco := 0.0
var _pillo := false
var _sprite: Sprite2D
var _sombra: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 12.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/travesia/anguila.png")
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -10)
	add_child(_sprite)
	_elegir_salto(1.0 if randf() < 0.5 else -1.0)


## De un lado de la cubierta al otro, pasando cerca de donde está Maisha
func _elegir_salto(lado: float) -> void:
	var y := randf_range(-34.0, 16.0)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and viaje:
		y = clampf(maisha.global_position.y - viaje.position.y + randf_range(-10.0, 10.0), -36.0, 18.0)
	_desde = Vector2(-84.0 * lado, y + randf_range(-8.0, 8.0))
	_hasta = Vector2(84.0 * lado, y + randf_range(-8.0, 8.0))
	_local = _desde
	fase = Fase.AVISA
	_t = 0.0
	visible = true
	_sprite.visible = false


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	if viaje == null or not is_instance_valid(viaje):
		queue_free()
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	match fase:
		Fase.AVISA:
			if _t >= AVISO:
				fase = Fase.SALTA
				_t = 0.0
				_pillo = false
				_sprite.visible = true
				Sonido.efecto("mamba_salta", -8.0, global_position)
		Fase.SALTA:
			var f := clampf(_t / SALTO, 0.0, 1.0)
			_local = _desde.lerp(_hasta, f)
			_sprite.position.y = -sin(f * PI) * 34.0
			_sprite.flip_h = _hasta.x < _desde.x
			if maisha and not _pillo and f > 0.35 and f < 0.65 and maisha.global_position.distance_to(viaje.position + _local) < 14.0:
				_pillo = true
				maisha.call("recibir_danio", 1, viaje.position + _local, "contacto")
			if f >= 1.0:
				Sonido.efecto("mamba_salta", -10.0, global_position)
				fase = Fase.BUCEA
				_t = 0.0
				_sprite.visible = false
		Fase.BUCEA:
			if _t >= 0.9:
				_saltos -= 1
				if _saltos <= 0:
					fase = Fase.FUERA
					queue_free()
					return
				_elegir_salto(-signf(_hasta.x))
		Fase.ATURDIDA:
			_sprite.position.y = 0.0
			if _t >= ATURDIDA:
				# vuelve al agua de un coletazo, por el lado más cerca
				_desde = _local
				_hasta = Vector2(84.0 * signf(_local.x if _local.x != 0.0 else 1.0), _local.y)
				fase = Fase.SALTA
				_t = 0.0
	global_position = viaje.position + _local
	_animar()
	queue_redraw()


func _animar() -> void:
	match fase:
		Fase.SALTA:
			_sprite.frame = int(_tiempo * 8.0) % 2
		Fase.ATURDIDA:
			_sprite.frame = 4 if fmod(_t, 0.8) < 0.3 else 2 + int(_tiempo * 10.0) % 2
	_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color.WHITE
	_sombra.visible = fase in [Fase.SALTA, Fase.ATURDIDA]


func _draw() -> void:
	# el aviso: la sombra de por dónde pasará, en la cubierta, y unas burbujas en el agua de donde saldrá
	if fase == Fase.AVISA:
		var f := clampf(_t / AVISO, 0.0, 1.0)
		var medio := (_hasta - _desde) / 2.0
		draw_line(Vector2.ZERO + medio * 0.5, medio * 1.5, Color(0.1, 0.05, 0.12, 0.25 + 0.3 * f), 5.0)
		for k in 3:
			var b := fmod(_tiempo * 2.0 + k * 0.33, 1.0)
			draw_circle(Vector2(k * 4.0 - 4.0, -b * 6.0), 1.5 * (1.0 - b) + 0.5, Color(0.8, 0.9, 0.9, 0.8 * (1.0 - b)))


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if fase == Fase.SALTA:
		# en el aire: cae a la cubierta, aturdida
		fase = Fase.ATURDIDA
		_t = 0.0
		_local.x = clampf(_local.x, -50.0, 50.0)
		_herir(danio)
		return true
	if fase == Fase.ATURDIDA:
		_herir(danio)
		return true
	return false


func recibir_danio(_cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	if tipo == "explosion" and fase == Fase.ATURDIDA:
		_herir(2)


func empujar(fuerza: Vector2) -> void:
	if fase == Fase.ATURDIDA:
		_local += fuerza.normalized() * 20.0


func _herir(cuanto: int) -> void:
	vida -= cuanto
	_blanco = 0.12
	Sonido.efecto("petrino_golpeado", 0.0, global_position)
	if vida <= 0:
		morir()


func morir() -> void:
	if is_in_group("enemigos"):
		Bestiario.vencido("anguila", self)
	remove_from_group("enemigos")
	remove_from_group("golpeables")
	remove_from_group("daniables")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.chispas = 3
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	queue_free()
