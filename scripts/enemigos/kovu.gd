extends Node2D
## KOVU DE ESCORIA, LA SALAMANDRA DE HIERRO FUNDIDO (Asterhaul, la Fundición): nada por la escoria con la cresta de
## hierro meteórico fuera.
##   - NADA entre los puntos de su `nado` (en la escoria). Ahí no hay forma de darle.
##   - Si Maisha se acerca (VE px), ASOMA la cabeza (el aviso: la boca al rojo) y ESCUPE una bola de escoria hacia
##     donde está (1 hoja; la paran los bloques-imán: «paran_escoria»). Luego se SUMERGE un rato.
##   - Su cresta es de hierro: el PULSO MAGNÉTICO (está en «magneticos»), con el Kovu a menos de TIRA px, lo saca de
##     un tirón a la piedra, al lado de Maisha. FUERA, en piedra fría, la coraza se le enfría y se agrieta (FUERA s):
##     ahí entran el cetro (1) y las semillas (2). 3 de vida. Si no se le vence a tiempo, vuelve a la escoria.
## Dibujo: arte/mundos/asterhaul/fundicion/kovu.png (herramientas/pintar_fundicion.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/kovu.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 3
const NADA := 26.0
const VE := 118.0
const TIRA := 120.0
const AVISO := 0.8
const SUMERGIDO := 2.2
const FUERA := 5.0
const BOLA_VEL := 96.0

enum Fase { NADA, ASOMA, SUMERGE, SALTA, FUERA }

## por dónde nada (puntos en px, en la escoria)
var nado: Array[Vector2] = []
var vida := VIDA
var fase := Fase.NADA
var _hacia := 0
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _muriendo := false
var _desde := Vector2.ZERO
var _cae := Vector2.ZERO
var _casa := Vector2.ZERO
var _bolas: Array[Dictionary] = []     # {p, v, t}
var _filas: PackedStringArray
var _sprite: Sprite2D
var _efectos: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("magneticos")
	add_to_group("kovus")
	_filas = get_tree().current_scene.get_node("Region")._filas
	_casa = position
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	_efectos = Node2D.new()
	_efectos.top_level = true
	_efectos.z_index = 2
	_efectos.draw.connect(_dibujar_bolas)
	add_child(_efectos)
	_tiempo = randf() * 3.0


func _es_piedra(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() and not (_filas[y][x] in ["0", "≈", "="])


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _process(delta: float) -> void:
	_mover_bolas(delta)
	_efectos.queue_redraw()
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.NADA:
			if not nado.is_empty():
				if global_position.distance_to(nado[_hacia]) < 3.0:
					_hacia = (_hacia + 1) % nado.size()
				global_position = global_position.move_toward(nado[_hacia], NADA * delta)
				_sprite.flip_h = nado[_hacia].x < global_position.x
			if maisha and not maisha.get("esta_caida") and d.length() < VE and _t > 1.0:
				_cambiar(Fase.ASOMA)
				Sonido.efecto("kovu_sumerge", -4.0, global_position, 0.2)
		Fase.ASOMA:
			if _t >= AVISO:
				if maisha:
					_bolas.append({"p": global_position + Vector2(0, -12), "v": (maisha.global_position + Vector2(0, -8) - global_position - Vector2(0, -12)).normalized() * BOLA_VEL, "t": 0.0})
				Sonido.efecto("fuego_quema", -4.0, global_position, 0.2)
				_cambiar(Fase.SUMERGE)
		Fase.SUMERGE:
			if _t >= SUMERGIDO:
				_cambiar(Fase.NADA)
		Fase.SALTA:
			var f := clampf(_t / 0.35, 0.0, 1.0)
			global_position = _desde.lerp(_cae, f) + Vector2(0, -sin(f * PI) * 22.0)
			if f >= 1.0:
				_cambiar(Fase.FUERA)
				Sonido.efecto("kovu_enfria", 0.0, global_position)
				Impacto.temblar(1.5, 0.12)
		Fase.FUERA:
			if _t >= FUERA:
				# vuelve a la escoria de un salto
				global_position = _casa
				Sonido.efecto("kovu_sumerge", -2.0, global_position)
				_cambiar(Fase.SUMERGE)
	_dibujar()


func _dibujar() -> void:
	_sprite.rotation = 0.0
	_sprite.visible = true
	match fase:
		Fase.NADA:
			_sprite.frame = int(_tiempo * 3.0) % 2
		Fase.ASOMA:
			_sprite.frame = 2
			_sprite.flip_h = false
		Fase.SUMERGE:
			_sprite.frame = int(_tiempo * 3.0) % 2
			_sprite.visible = _t < 0.3 or _t > SUMERGIDO - 0.4       # bajo la escoria no se le ve
		Fase.SALTA:
			_sprite.frame = 3
			_sprite.rotation = _t * 14.0
		Fase.FUERA:
			_sprite.frame = 4 if _destello > 0.0 else 3
			_sprite.rotation = sin(_tiempo * (5.0 if _t < FUERA - 1.0 else 18.0)) * 0.06


## Las bolas de escoria: vuelan en línea recta; las paran Maisha (1 hoja), los bloques-imán y la roca
func _mover_bolas(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	for b in _bolas:
		b["t"] += delta
		b["p"] += b["v"] * delta
		var p: Vector2 = b["p"]
		var fin := float(b["t"]) > 3.0
		if maisha and maisha.global_position.distance_to(p + Vector2(0, 8)) < 9.0:
			maisha.call("recibir_danio", 1, p, "escoria")
			fin = true
		for n in get_tree().get_nodes_in_group("paran_escoria"):
			if (n as Node2D).global_position.distance_to(p + Vector2(0, 6)) < 12.0:
				Sonido.efecto("clinc", -6.0, p, 0.2)
				fin = true
		if fin:
			b["t"] = 99.0
			Impacto.chispa(p, -(b["v"] as Vector2).normalized(), Color("f88a20"))
	_bolas = _bolas.filter(func(b: Dictionary) -> bool: return float(b["t"]) < 50.0)


func _dibujar_bolas() -> void:
	for b in _bolas:
		var p: Vector2 = b["p"]
		_efectos.draw_circle(p, 4.5, Color(0.98, 0.54, 0.12, 0.45))
		_efectos.draw_circle(p, 3.0, Color("f88a20"))
		_efectos.draw_circle(p + Vector2(-0.8, -0.8), 1.4, Color("fff0b0"))
		_efectos.draw_circle(p - (b["v"] as Vector2).normalized() * 5.0, 1.6, Color(0.88, 0.29, 0.06, 0.6))


# --- Pulso y daño --------------------------------------------------------------

## El Pulso Magnético tira de su cresta y lo saca a la piedra, al lado de Maisha
func recibir_pulso(origen: Vector2) -> bool:
	if _muriendo or fase in [Fase.SALTA, Fase.FUERA] or origen.distance_to(global_position) > TIRA:
		return false
	var hacia := (global_position - origen).normalized()
	_cae = origen + hacia * 24.0
	if not _es_piedra(_cae):
		_cae = origen + Vector2(0, 2)
	_desde = global_position
	_cambiar(Fase.SALTA)
	Sonido.efecto("bloque_atraer", 2.0, global_position)
	return true


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or fase != Fase.FUERA:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde_: Vector2, tipo: String) -> void:
	if _muriendo or fase != Fase.FUERA:
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -8), Vector2.UP, Color("b4b6c0"))
	if vida > 0:
		Sonido.efecto("roca_romper", -8.0, global_position, 0.3)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("kovu", self)
	Sonido.efecto("roca_romper", -2.0, global_position)
	for g in ["enemigos", "golpeables", "daniables", "magneticos", "kovus"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.15), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.4)
	t.chain().tween_interval(3.0)
	t.chain().tween_callback(queue_free)
