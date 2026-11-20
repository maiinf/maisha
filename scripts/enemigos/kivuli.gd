extends Node2D
## KIVULI MENOR, EL ALACRÁN DE SOMBRA (el Valle del Ocaso): una sombra con pinzas que corretea por su meseta
## (`zona`, px: nunca la deja; es de sombra, no se cae).
##   - EN PENUMBRA no se le puede hacer nada: el cetro y las semillas lo atraviesan. Si ve a Maisha (VE px), la
##     persigue y le pica al tocarla (1 hoja).
##   - AL SOL (ocaso/sol.gd → `iluminado()`) se queda DESLUMBRADO: pálido, encogido, quieto. Ahí entran el cetro (1)
##     y las semillas (2). 3 de vida. Si se mete en la sombra de un obelisco, vuelve a estar a salvo.
## Dibujo: arte/mundos/ocaso/mirador/kivuli.png (pintar_mirador.py): 0-1 anda · 2 en penumbra · 3 deslumbrado
## · 4 golpeado.

signal destruido

const DIBUJO := preload("res://arte/mundos/ocaso/mirador/kivuli.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 3
const VE := 110.0
const VEL := 38.0
const PERSIGUE := 62.0
const PICA_CADA := 1.1

enum Fase { ANDA, PERSIGUE, DESLUMBRADO }

var zona := Rect2(-100000, -100000, 200000, 200000)
var vida := VIDA
var fase := Fase.ANDA
var _puesto := Vector2.ZERO
var _meta := Vector2.ZERO
var _tiempo := 0.0
var _pica := 0.0
var _destello := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _sol: Node


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("kivulis")
	_puesto = position
	_meta = position
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 12.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -10)
	add_child(_sprite)
	_sol = get_tree().get_first_node_in_group("sol")
	_tiempo = randf() * 3.0


func al_sol() -> bool:
	return _sol != null and _sol.iluminado(global_position)


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_pica = maxf(0.0, _pica - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	if al_sol():
		if fase != Fase.DESLUMBRADO:
			fase = Fase.DESLUMBRADO
			Sonido.efecto("kivuli_deslumbra", -2.0, global_position, 0.08)
	elif fase == Fase.DESLUMBRADO:
		fase = Fase.ANDA
	match fase:
		Fase.ANDA:
			if global_position.distance_to(_meta) < 3.0:
				_meta = _puesto + Vector2(randf_range(-40, 40), randf_range(-24, 24))
			_andar(_meta, VEL, delta)
			if maisha and not maisha.get("esta_caida") and d.length() < VE:
				fase = Fase.PERSIGUE
		Fase.PERSIGUE:
			if maisha == null or d.length() > VE * 1.5:
				fase = Fase.ANDA
			else:
				_andar(maisha.global_position, PERSIGUE, delta)
				if d.length() < 12.0 and _pica <= 0.0:
					_pica = PICA_CADA
					Sonido.efecto("kivuli_pica", -1.5, global_position, 0.1)
					maisha.call("recibir_danio", 1, global_position, "contacto")
	_dibujar()


func _andar(hacia: Vector2, vel: float, delta: float) -> void:
	var p := global_position.move_toward(hacia, vel * delta)
	p.x = clampf(p.x, zona.position.x, zona.end.x)
	p.y = clampf(p.y, zona.position.y, zona.end.y)
	if p.x < global_position.x - 0.01:
		_sprite.flip_h = true
	elif p.x > global_position.x + 0.01:
		_sprite.flip_h = false
	global_position = p


func _dibujar() -> void:
	if _destello > 0.0:
		_sprite.frame = 4
	elif fase == Fase.DESLUMBRADO:
		_sprite.frame = 3
		_sprite.position.x = roundf(sin(_tiempo * 40.0) * 0.6)
	else:
		_sprite.position.x = 0.0
		# en la sombra de un obelisco casi no se le ve
		_sprite.frame = 2 if (_sol and _sol.en_sombra(global_position)) else int(_tiempo * 8.0) % 2


# --- Daño ------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or not al_sol():
		return false                                  # (en penumbra el cetro lo atraviesa)
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or not al_sol():
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -6), Vector2.UP, Color("f0c0ff"))
	if vida <= 0:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("kivuli_menor", self)
	Sonido.efecto("kivuli_muere", -1.5, global_position, 0.12)
	for g in ["enemigos", "golpeables", "daniables", "kivulis"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.4, 0.1), 0.35)
	t.tween_property(self, "modulate:a", 0.0, 0.45)
	t.chain().tween_callback(queue_free)
