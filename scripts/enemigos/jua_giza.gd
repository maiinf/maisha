extends Node2D
## JUA-GIZA, EL SOL ENCADENADO (el jefe final, El Horizonte Inmóvil; opción A elegida por Iam): el sol del Valle del
## Ocaso, atado al altar por tres cadenas para que el día no terminara nunca. No se le mata: se le SUELTA.
## 12 de vida (la barra), cuatro por cadena:
##   1. LA CADENA DEL OESTE (Sombra): cada poco avisa y suelta una LLAMARADA: quita 1 hoja si Maisha no está a la
##      sombra de un obelisco (ocaso/sol.gd). La cadena tira de un CONTRAPESO (ocaso/contrapeso.gd): dos Cargas
##      Sísmicas lo rompen (2 cada una).
##   2. LA CADENA DEL ESTE (Luz): el VELO de Giza lo envuelve. Con los DOS espejos altos (ocaso/espejo_alto.gd)
##      echándole su rayo a la vez, el velo se abre y se ve el BROCHE: cetro 1, semillas 2 (EXPUESTO s). Sigue
##      habiendo llamaradas.
##   3. LA CADENA DEL SUR (Calma): OLAS de penumbra que salen de él en corro (con un hueco por donde pasar) y dos
##      RAYOS cruzados que giran. Tras cada dos olas, el CANDADO del sur (ocaso/candado_sur.gd) brilla (BRILLA s):
##      cada golpe, 1.
##   Al soltar la tercera, se queda en CALMA (`calmado`): lo que pasa después lo cuenta la escena.
## Dibujo: arte/mundos/ocaso/horizonte/jua_giza.png (herramientas/pintar_horizonte.py). Música: «jefe_jua_giza».

signal calmado
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/horizonte/jua_giza.png")
const NOMBRE := "Jua-Giza, el Sol Encadenado"
const VIDA_MAX := 12
const LLAMARADA_CADA := 5.0
const AVISO := 1.3
const EXPUESTO := 3.5
const GOLPES_EXPUESTO := 2
const OLA_CADA := 3.2
const OLA_VEL := 95.0
const OLA_LARGO := 240.0
const HUECO := 0.6                      # (medio hueco de la ola, en radianes)
const RAYO_LARGO := 230.0
const RAYO_GIRO := 0.55                  # (rad/s)
const BRILLA := 3.0

enum Fase { DORMIDO, OESTE, ESTE, SUR, CALMA }

var espejos: Array = []                  # los dos espejos altos (los pone la escena)
var contrapeso: Node2D
var candado: Node2D
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var _t := 0.0                            # para la llamarada (y las olas)
var _aviso := false
var _expuesto := 0.0
var _ambos := false
var _golpes := 0
var _destello := 0.0
var _olas: Array = []                    # [{r, hueco}]
var _n_olas := 0
var _angulo := 0.0
var _brilla := 0.0
var _sprite: Sprite2D
var _efectos: Node2D
var _barra: CanvasLayer = null
var _sol: Node


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("jua_giza")
	var cuerpo := StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var bola := CircleShape2D.new()
	bola.radius = 22.0
	forma.shape = bola
	forma.position = Vector2(0, -6)
	cuerpo.add_child(forma)
	add_child(cuerpo)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -62)
	add_child(_sprite)
	_efectos = Node2D.new()
	_efectos.z_index = 2
	_efectos.draw.connect(_dibujar_efectos)
	add_child(_efectos)
	_sol = get_tree().get_first_node_in_group("sol")


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_jua_giza" if ResourceLoader.exists("res://audio/musica/jefe_jua_giza.ogg") else "jefe_saa")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	contrapeso.golpeado.connect(_al_cargar_contrapeso)
	candado.golpeado.connect(_al_golpear_candado)
	_pasar(Fase.OESTE)


func _pasar(f: Fase) -> void:
	fase = f
	_t = 0.0
	_aviso = false
	contrapeso.activo = f == Fase.OESTE
	if f == Fase.CALMA:
		_olas.clear()
		candado.brilla = false
		if _barra:
			_barra.queue_free()
			_barra = null
		calmado.emit()


func _quitar(n: int) -> void:
	vida = maxi(0, vida - n)
	_destello = 0.15
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -60), Vector2.UP, Color("ffd878"))


## Cada cadena que se suelta, con su ruido y su temblor
func _soltar_cadena(siguiente: Fase) -> void:
	Sonido.efecto("cadena_suelta", 0.0, global_position)
	Impacto.temblar(5.0, 0.6)
	Impacto.fogonazo(Color(1.0, 0.9, 0.6), 0.4, 0.6)
	_pasar(siguiente)


func _al_cargar_contrapeso() -> void:
	if fase != Fase.OESTE:
		return
	_quitar(2)
	if vida <= VIDA_MAX - 4:
		contrapeso.romper()
		_soltar_cadena(Fase.ESTE)


func _al_golpear_candado() -> void:
	if fase != Fase.SUR:
		return
	_brilla = 0.0                                       # (un golpe por cada vez que brilla)
	candado.brilla = false
	_quitar(1)
	if vida <= 0:
		_soltar_cadena(Fase.CALMA)


func expuesto() -> bool:
	return fase == Fase.ESTE and _expuesto > 0.0


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if not expuesto():
		if fase != Fase.DORMIDO and fase != Fase.CALMA:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if not expuesto():
		return
	_quitar(2 if tipo == "explosion" else cantidad)
	_golpes += 1
	if vida <= VIDA_MAX - 8:
		_expuesto = 0.0
		_soltar_cadena(Fase.SUR)
	elif _golpes >= GOLPES_EXPUESTO:
		_expuesto = 0.0


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _dar(m: Node2D) -> void:
	if m and not m.get("esta_caida"):
		m.call("recibir_danio", 1, global_position, "rayo")


func _process(delta: float) -> void:
	_destello = maxf(0.0, _destello - delta)
	var m := _maisha()
	match fase:
		Fase.OESTE, Fase.ESTE:
			_t += delta
			if not _aviso and _t >= LLAMARADA_CADA - AVISO:
				_aviso = true
				Sonido.efecto("jua_aviso", -1.0, global_position)
			if _t >= LLAMARADA_CADA:
				_t = 0.0
				_aviso = false
				Sonido.efecto("jua_llamarada", 0.0, global_position)
				Impacto.fogonazo(Color(1.0, 0.85, 0.5), 0.35, 0.4)
				if m and not _sol.en_sombra(m.global_position):
					_dar(m)
			if fase == Fase.ESTE:
				_expuesto = maxf(0.0, _expuesto - delta)
				var ambos := espejos.size() == 2 and espejos.all(func(e: Node) -> bool: return e.toca(global_position))
				if ambos and not _ambos:
					_expuesto = EXPUESTO                    # (los dos rayos a la vez: el velo se abre)
					_golpes = 0
					Sonido.efecto("velo_abre", 0.0, global_position)
				_ambos = ambos
		Fase.SUR:
			_t += delta
			_angulo += RAYO_GIRO * delta
			_brilla = maxf(0.0, _brilla - delta)
			candado.brilla = _brilla > 0.0
			if _t >= OLA_CADA:
				_t = 0.0
				_olas.append({"r": 20.0, "hueco": randf() * TAU, "dio": false})
				Sonido.efecto("jua_ola", -1.0, global_position)
			for o in _olas.duplicate():
				var antes: float = o["r"]
				o["r"] += OLA_VEL * delta
				if m and not o["dio"]:
					var d := m.global_position - global_position
					if d.length() > antes and d.length() <= o["r"] and absf(angle_difference(d.angle(), o["hueco"])) > HUECO:
						o["dio"] = true
						_dar(m)
				if o["r"] > OLA_LARGO:
					_olas.erase(o)
					_n_olas += 1
					if _n_olas % 2 == 0:
						_brilla = BRILLA
						Sonido.efecto("candado_brilla", 0.0, candado.global_position)
			if m:
				for punta in _rayos():
					if Geometry2D.get_closest_point_to_segment(m.global_position, global_position, global_position + punta).distance_to(m.global_position) < 8.0:
						_dar(m)
	_dibujar()
	_efectos.queue_redraw()


func _rayos() -> Array:
	if fase != Fase.SUR:
		return []
	var a := Vector2.from_angle(_angulo) * RAYO_LARGO
	return [a, -a, a.orthogonal(), -a.orthogonal()]


func _dibujar() -> void:
	match fase:
		Fase.CALMA:
			_sprite.frame = 5
		Fase.DORMIDO:
			_sprite.frame = 0
		_:
			if _destello > 0.0:
				_sprite.frame = 4
			elif _aviso and fmod(_t * 8.0, 1.0) < 0.5:
				_sprite.frame = 1
			elif fase == Fase.ESTE:
				_sprite.frame = 3 if expuesto() else 2
			else:
				_sprite.frame = 0
	_sprite.position.y = roundf(sin(Time.get_ticks_msec() / 400.0) * 2.0)


func _dibujar_efectos() -> void:
	for o in _olas:
		var r: float = o["r"]
		var a := clampf(1.0 - r / OLA_LARGO, 0.0, 1.0)
		var h: float = o["hueco"]
		_efectos.draw_arc(Vector2.ZERO, r, h + HUECO, h + TAU - HUECO, 64, Color(0.35, 0.15, 0.55, 0.55 * a + 0.2), 7.0)
		_efectos.draw_arc(Vector2.ZERO, r, h + HUECO, h + TAU - HUECO, 64, Color(0.85, 0.6, 1.0, 0.7 * a), 2.0)
	for punta in _rayos():
		_efectos.draw_line(Vector2.ZERO, punta, Color(1.0, 0.85, 0.45, 0.2), 14.0)
		_efectos.draw_line(Vector2.ZERO, punta, Color(1.0, 0.95, 0.8, 0.9), 2.0)
