extends Node2D
## UN CENTINELA DE RELOJ (la Calzada de los Obeliscos): un guardián de bronce con un reloj de arena por cabeza. Solo
## se mueve EN PENUMBRA: anda por su viaducto (`zona`, px), persigue a Maisha si la ve (VE px) y le da con la
## alabarda (1 hoja). El cetro rebota en su bronce.
##   - AL SOL (ocaso/sol.gd → `iluminado()`) se queda de PIEDRA, quieto como una estatua.
##   - De piedra, una CARGA SÍSMICA lo vuelca y se rompe. Si vuelve la penumbra antes, se despierta.
## Dibujo: arte/mundos/ocaso/calzada/centinela.png (0-1 anda · 2 golpea · 3 estatua · 4 roto).

signal destruido

const DIBUJO := preload("res://arte/mundos/ocaso/calzada/centinela.png")
const VE := 120.0
const VEL := 26.0
const PERSIGUE := 44.0
const ALCANCE := 22.0
const AVISO := 0.55

enum Fase { ANDA, PERSIGUE, GOLPEA, ESTATUA, ROTO }

var zona := Rect2(-100000, -100000, 200000, 200000)
var fase := Fase.ANDA
var _puesto := Vector2.ZERO
var _meta := Vector2.ZERO
var _t := 0.0
var _tiempo := 0.0
var _sprite: Sprite2D
var _sol: Node


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("sismicos")
	add_to_group("centinelas")
	_puesto = position
	_meta = position
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 12.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -19)
	add_child(_sprite)
	_sol = get_tree().get_first_node_in_group("sol")
	_tiempo = randf() * 3.0


func al_sol() -> bool:
	return _sol != null and _sol.iluminado(global_position)


func estatua() -> bool:
	return fase == Fase.ESTATUA


func _process(delta: float) -> void:
	if fase == Fase.ROTO:
		return
	_tiempo += delta
	_t += delta
	if al_sol():
		if fase != Fase.ESTATUA:
			fase = Fase.ESTATUA
			Sonido.efecto("centinela_piedra", -2.0, global_position, 0.08)
	elif fase == Fase.ESTATUA:
		fase = Fase.ANDA
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.ANDA:
			if global_position.distance_to(_meta) < 3.0:
				_meta = _puesto + Vector2(randf_range(-40, 40), randf_range(-20, 20))
			_andar(_meta, VEL, delta)
			if maisha and not maisha.get("esta_caida") and d.length() < VE:
				fase = Fase.PERSIGUE
		Fase.PERSIGUE:
			if maisha == null or d.length() > VE * 1.5:
				fase = Fase.ANDA
			elif d.length() < ALCANCE - 4.0:
				fase = Fase.GOLPEA
				_t = 0.0
			else:
				_andar(maisha.global_position, PERSIGUE, delta)
		Fase.GOLPEA:
			if _t >= AVISO:
				Sonido.efecto("centinela_golpe", -1.0, global_position, 0.1)
				if maisha and d.length() < ALCANCE:
					maisha.call("recibir_danio", 1, global_position, "contacto")
				fase = Fase.PERSIGUE
				_t = -0.6
	_dibujar()


func _andar(hacia: Vector2, vel: float, delta: float) -> void:
	var p := global_position.move_toward(hacia, vel * delta)
	p.x = clampf(p.x, zona.position.x, zona.end.x)
	p.y = clampf(p.y, zona.position.y, zona.end.y)
	if absf(p.x - global_position.x) > 0.01:
		_sprite.flip_h = p.x < global_position.x
	global_position = p


func _dibujar() -> void:
	match fase:
		Fase.ESTATUA:
			_sprite.frame = 3
		Fase.GOLPEA:
			_sprite.frame = 2 if _t >= 0.0 else 0
		_:
			_sprite.frame = int(_tiempo * 5.0) % 2


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	Sonido.efecto("clinc", -2.0, global_position, 0.2)
	return false                                   # (bronce o piedra: el cetro rebota)


func recibir_carga(direccion: Vector2) -> bool:
	if not estatua():
		return false
	fase = Fase.ROTO
	for g in ["enemigos", "golpeables", "sismicos", "centinelas"]:
		remove_from_group(g)
	Bestiario.vencido("centinela", self)
	Sonido.efecto("centinela_rompe", 0.0, global_position, 0.1)
	Impacto.chispa(global_position + Vector2(0, -16), direccion, Color("d8c89a"))
	_sprite.frame = 4
	_sprite.flip_h = direccion.x < 0.0
	destruido.emit()
	return true
