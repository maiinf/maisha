extends Node2D
## LA VENTISCA DE PÁGINAS (Sigilia, Paso de la Escarcha). Cada pocos segundos baja una racha de viento cargada de
## páginas sueltas:
##   CALMA (5,5-8 s) → AVISO (1,3 s: empiezan a pasar páginas y sube el silbido) → RACHA (2,6 s: empuja a Maisha).
## La racha viene casi siempre del oeste (a veces del este) y empuja a Maisha a favor del viento, fuera del sendero y
## hacia la nieve honda... salvo si está COBIJADA: con algo sólido (una estela, una roca, un pino, la peña) justo
## por el lado de donde viene el viento.
## Las páginas se dibujan aquí, delante de todo y con la pantalla (como la nevada).

signal racha_empieza(desde: int)        # -1 del oeste, 1 del este
signal racha_acaba

enum Fase { CALMA, AVISO, RACHA }
const AVISO := 1.3
const RACHA := 2.6
const FUERZA := 62.0                 # px/s: casi lo que anda Maisha (70); en la nieve honda, más que ella
const COBIJO := 34.0                 # lo lejos que mira, hacia el viento, si hay algo que la tape
const PAGINAS := 70

var activa := true
var fase := Fase.CALMA
var desde := -1                       # de dónde viene: -1 oeste, 1 este
var cobijada := false
var _t := 4.0                         # (la primera racha tarda un poco)
var _fuerza := 0.0                    # 0..1, sube y baja suave
var _tiempo := 0.0
var _paginas: Array[Dictionary] = []
var _ultima_pagina := 0.0


func _ready() -> void:
	z_index = 4
	for i in PAGINAS:
		_paginas.append({"p": Vector2(-100, -100), "v": Vector2.ZERO, "viva": false, "fase": randf() * TAU, "tam": randi() % 3})


func _process(delta: float) -> void:
	_tiempo += delta
	if not activa:
		_fuerza = move_toward(_fuerza, 0.0, delta * 2.0)
	else:
		_t -= delta
		match fase:
			Fase.CALMA:
				_fuerza = move_toward(_fuerza, 0.0, delta * 2.0)
				if _t <= 0.0:
					fase = Fase.AVISO
					_t = AVISO
					desde = -1 if randf() < 0.8 else 1
					Sonido.ambiente({"viento": 0.95})
			Fase.AVISO:
				_fuerza = move_toward(_fuerza, 0.25, delta * 0.6)
				if _t <= 0.0:
					fase = Fase.RACHA
					_t = RACHA
					racha_empieza.emit(desde)
			Fase.RACHA:
				_fuerza = move_toward(_fuerza, 1.0, delta * 2.5)
				if _t <= 0.0:
					fase = Fase.CALMA
					_t = randf_range(5.5, 8.0)
					Sonido.ambiente({"viento": 0.6})
					racha_acaba.emit()
	_empujar()
	_mover_paginas(delta)
	var cam := get_viewport().get_camera_2d()
	if cam:
		global_position = cam.get_screen_center_position() - Vector2(320, 180)
	queue_redraw()


## Empuja a Maisha a favor del viento, si no está cobijada
func _empujar() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if maisha == null:
		return
	cobijada = _esta_cobijada(maisha)
	if not activa or fase != Fase.RACHA or cobijada or maisha.get("esta_caida"):
		return
	maisha.set("viento", Vector2(-desde * FUERZA * _fuerza, 0.0))
	if _tiempo - _ultima_pagina > 0.5:
		_ultima_pagina = _tiempo
		Sonido.efecto("pagina", -10.0, maisha.global_position, 0.3)


## ¿Hay algo sólido a su lado de donde viene el viento (rayos a la altura de los pies y un poco más arriba), o un
## farol rúnico encendido cerca?
func _esta_cobijada(maisha: CharacterBody2D) -> bool:
	for f in get_tree().get_nodes_in_group("faroles_runicos"):
		if f.call("abriga", maisha.global_position):
			return true
	var espacio := get_world_2d().direct_space_state
	for alto in [-3.0, -9.0]:
		var desde_p := maisha.global_position + Vector2(0, alto)
		var q := PhysicsRayQueryParameters2D.create(desde_p, desde_p + Vector2(desde * COBIJO, 0))
		q.exclude = [maisha.get_rid()]
		q.collision_mask = 1
		var choque := espacio.intersect_ray(q)
		if not choque.is_empty() and not (choque["collider"] is CharacterBody2D):
			return true
	return false


func _mover_paginas(delta: float) -> void:
	# cuántas páginas vuelan: unas pocas en el aviso, muchas en la racha
	var quiero := 0
	if fase == Fase.AVISO:
		quiero = 14
	elif fase == Fase.RACHA:
		quiero = PAGINAS
	var vivas := 0
	for p in _paginas:
		if p["viva"]:
			vivas += 1
	for p in _paginas:
		if not p["viva"] and vivas < quiero and randf() < 0.25:
			p["viva"] = true
			vivas += 1
			p["p"] = Vector2(-20.0 if desde < 0 else 660.0, randf() * 340.0)
			p["v"] = Vector2(-desde * randf_range(160, 300), randf_range(-30, 30))
		if not p["viva"]:
			continue
		p["p"] += (p["v"] + Vector2(0, sin(_tiempo * 9.0 + p["fase"]) * 40.0)) * delta
		if p["p"].x < -40.0 or p["p"].x > 690.0:
			p["viva"] = false


func _draw() -> void:
	# la racha también se ve: unas líneas de viento muy suaves
	if _fuerza > 0.05:
		for k in 10:
			var y := fmod(k * 37.0 + _tiempo * 13.0, 360.0)
			var x := fmod(_tiempo * 420.0 * -desde + k * 97.0, 700.0)
			if x < 0.0:
				x += 700.0
			draw_line(Vector2(x - 30, y), Vector2(x + 30, y), Color(0.3, 0.26, 0.45, 0.18 * _fuerza), 1.0)
	for p in _paginas:
		if not p["viva"]:
			continue
		var pos: Vector2 = (p["p"] as Vector2).floor()
		var aleteo := sin(_tiempo * 14.0 + p["fase"])
		var ancho := 4 + int(p["tam"]) + (1 if aleteo > 0 else -1)
		var alto := 3 + (1 if aleteo < -0.3 else 0)
		draw_rect(Rect2(pos - Vector2.ONE, Vector2(ancho + 2, alto + 2)), Color(0.24, 0.2, 0.34, 0.85))   # el borde, oscuro
		draw_rect(Rect2(pos, Vector2(ancho, alto)), Color(0.97, 0.93, 0.84))
		if ancho > 3:
			draw_rect(Rect2(pos + Vector2(1, 1), Vector2(ancho - 2, 1)), Color(0.35, 0.3, 0.45, 0.7))   # un renglón
