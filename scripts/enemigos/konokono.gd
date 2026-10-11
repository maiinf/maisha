extends Node2D
## KONOKONO, LA CARACOLA DE ÓXIDO: el minijefe de la Ciénaga Quieta.
## La vieja caracola que guardaba el agua de la ciénaga. Giza le llenó la concha de herrumbre y hierro.
##
##   - Se ARRASTRA hacia Maisha dejando un rastro de óxido que la frena. Su concha lo aguanta todo.
##   - Se TRAGA las semillas que encuentra en su camino (¡le encantan!). La semilla le ESTALLA DENTRO:
##     le quita 2 y la deja MAREADA un rato, fuera de la concha: entonces el cetro le quita 1.
##   - Si se le golpea sin estar mareada, se ESCONDE en la concha un momento.
##   - Fase 2 (con la mitad de vida): a veces se esconde y RUEDA en línea recta (rebota en el borde),
##     y escupe bolas de óxido que caen con su sombra de aviso y dejan charcos que frenan.
## Al vencerla, la herrumbre se le cae: la concha vuelve a tener musgo y flores, y la niebla se levanta.
## Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "konokono").

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, ARRASTRA, MAREADA, ESCONDIDA, PREPARA_RUEDA, RUEDA, ESCUPE, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const EXPLOSION := preload("res://scripts/combate/explosion.gd")
const BOLA := preload("res://scripts/enemigos/bola_oxido.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "Konokono, la caracola de óxido"
const ARRASTRA_F := [0, 1]
const BOCA := 2
const CONCHA := 3
const MAREO := 4
const RUEDA_F := 5
const LIBRE := 6
const CONTENTA := 7

var zona: Node2D
var variante := "raiz"
var vida: int = R.KONOKONO_VIDA
var fase: int = Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _mira := 1.0
var _dir := Vector2.RIGHT
var _rebotes := 0
var _blanco := 0.0
var _dentro: Array[float] = []           # semillas tragadas: segundos que les quedan para estallar
var _rastro: Array[Dictionary] = []
var _ultimo := Vector2.INF
var _desde_ataque := 0.0
var _sprite: Sprite2D
var _capa_rastro: Node2D
var _barra: CanvasLayer


func _ready() -> void:
	add_to_group("jefes")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 36.0)
	add_child(sombra)
	_capa_rastro = Node2D.new()
	_capa_rastro.top_level = true
	_capa_rastro.z_index = -3
	_capa_rastro.draw.connect(_dibujar_rastro)
	add_child(_capa_rastro)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/konokono.png" % variante)
	_sprite.hframes = 8
	_sprite.offset = Vector2(0, -34)
	add_child(_sprite)
	visible = false


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.KONOKONO_VIDA
	_dentro.clear()
	visible = true
	modulate.a = 1.0
	global_position = zona.global_position + Vector2(zona.radios_umbral.x * 0.35, -zona.radios_umbral.y * 0.2)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("konokono_despierta")
	Impacto.temblar(3.0, 0.6)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.KONOKONO_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	vida = R.KONOKONO_VIDA
	_dentro.clear()
	_rastro.clear()
	if _barra:
		_barra.queue_free()
		_barra = null
	for b in get_tree().get_nodes_in_group("bolas_oxido"):
		b.queue_free()
	fase = Fase.DORMIDO
	visible = false
	remove_from_group("golpeables")
	remove_from_group("daniables")


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	if nueva in [Fase.DORMIDO, Fase.VENCIDO]:
		remove_from_group("golpeables")
		remove_from_group("daniables")
	else:
		add_to_group("golpeables")
		add_to_group("daniables")


func _en_fase_2() -> bool:
	return vida <= R.KONOKONO_VIDA / 2


func _boca() -> Vector2:
	return global_position + Vector2(39.0 * _mira, -8)


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	_secar_rastro(delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta, maisha)
	if fase == Fase.DORMIDO:
		return
	# las semillas tragadas estallan dentro
	for i in range(_dentro.size() - 1, -1, -1):
		_dentro[i] -= delta
		if _dentro[i] <= 0.0:
			_dentro.remove_at(i)
			_estallar_dentro()
	match fase:
		Fase.PRESENTACION:
			if _t > 1.8:
				_cambiar(Fase.ARRASTRA)
		Fase.ARRASTRA:
			_arrastrar(delta, maisha)
		Fase.MAREADA:
			if _t >= R.KONOKONO_ATURDIDA:
				_cambiar(Fase.ARRASTRA)
		Fase.ESCONDIDA:
			if _t >= R.KONOKONO_ESCONDIDA:
				_cambiar(Fase.ARRASTRA)
		Fase.PREPARA_RUEDA:
			if _t >= 0.8:
				_cambiar(Fase.RUEDA)
				_rebotes = 0
				Sonido.efecto("konokono_rueda")
		Fase.RUEDA:
			_rodar(delta)
		Fase.ESCUPE:
			if _t >= 0.6 and _t - delta < 0.6:
				_escupir(maisha)
			if _t >= 1.2:
				_cambiar(Fase.ARRASTRA)
		Fase.VENCIDO:
			_proceso_vencido()
	# daño por contacto (más fuerte si rueda)
	if maisha and fase in [Fase.ARRASTRA, Fase.RUEDA] and _toca(maisha.global_position):
		maisha.call("recibir_danio", 2 if fase == Fase.RUEDA else 1, global_position, "contacto")
	_animar()


func _arrastrar(delta: float, maisha: Node2D) -> void:
	_desde_ataque += delta
	if maisha:
		var hacia := maisha.global_position - global_position
		if absf(hacia.x) > 6.0:
			_mira = signf(hacia.x)
		var mov := hacia.normalized() * R.KONOKONO_VELOCIDAD * (0.5 + 0.5 * sin(_tiempo * 3.0) ** 2)
		var nueva := global_position + mov * delta
		if zona.distancia_normal(nueva) < 0.82:
			global_position = nueva
	if global_position.distance_to(_ultimo) > 6.0:
		_ultimo = global_position
		_rastro.append({"p": global_position + Vector2(-_mira * 8.0, 0), "t": 0.0})
	# se traga las semillas que tiene delante de la boca o por las que pasa por encima (¡le encantan!)
	for s in get_tree().get_nodes_in_group("semillas"):
		var d: Vector2 = s.global_position - global_position
		if s.global_position.distance_to(_boca() + Vector2(0, 6)) < R.KONOKONO_TRAGA_A \
				or (d.x / 41.0) ** 2 + (d.y / 15.0) ** 2 < 1.0:
			_tragar(s)
			break
	# fase 2: rueda o escupe de vez en cuando
	if _en_fase_2() and _desde_ataque > 4.0:
		_desde_ataque = 0.0
		if randf() < 0.5:
			_cambiar(Fase.PREPARA_RUEDA)
			if maisha:
				_dir = (maisha.global_position - global_position).normalized()
			Sonido.efecto("konokono_escondida")
		else:
			_cambiar(Fase.ESCUPE)


func _tragar(semilla: Node2D) -> void:
	var queda: float = semilla.get("_mecha") if semilla.get("_mecha") != null else 1.0
	semilla.remove_from_group("semillas")
	semilla.queue_free()
	_dentro.append(maxf(0.25, queda))
	_cambiar(Fase.ARRASTRA)
	_t = 0.0
	Sonido.efecto("konokono_traga")
	_sprite.frame = BOCA


func _estallar_dentro() -> void:
	Sonido.efecto("explosion", 0.0, global_position)
	Impacto.onda(global_position + Vector2(0, -16))
	Impacto.temblar(3.5, 0.3)
	var fx: Node2D = EXPLOSION.new()
	fx.position = global_position + Vector2(0, -8)
	get_parent().add_child(fx)
	_herir(R.KONOKONO_DANIO_DENTRO)
	if vida > 0:
		_cambiar(Fase.MAREADA)


func _rodar(delta: float) -> void:
	var nueva := global_position + _dir * R.KONOKONO_RUEDA * delta
	if zona.distancia_normal(nueva) > 0.86:
		_rebotes += 1
		Impacto.temblar(2.5, 0.2)
		Sonido.efecto("piedra_rompe", 0.0, global_position)
		# rebota hacia el centro (con un poco de giro)
		_dir = (zona.global_position - global_position).normalized().rotated(randf_range(-0.6, 0.6))
		if _rebotes >= 3:
			_cambiar(Fase.MAREADA)
			return
	else:
		global_position = nueva
	if absf(_dir.x) > 0.1:
		_mira = signf(_dir.x)
	if global_position.distance_to(_ultimo) > 6.0:
		_ultimo = global_position
		_rastro.append({"p": global_position, "t": 0.0})


func _escupir(maisha: Node2D) -> void:
	if maisha == null:
		return
	Sonido.efecto("konokono_escupe")
	for k in R.KONOKONO_ESCUPE:
		var bola: Node2D = BOLA.new()
		bola.add_to_group("bolas_oxido")
		var objetivo := maisha.global_position + Vector2(randf_range(-40, 40), randf_range(-28, 28)) * (0.3 if k == 0 else 1.0)
		if zona.distancia_normal(objetivo) > 0.85:
			objetivo = zona.global_position + (objetivo - zona.global_position) * 0.7
		bola.desde = _boca()
		bola.hasta = objetivo
		bola.al_caer = func(p: Vector2) -> void: _rastro_charco(p)
		get_parent().add_child(bola)


func _rastro_charco(p: Vector2) -> void:
	for k in 7:
		_rastro.append({"p": p + Vector2.from_angle(k * TAU / 7.0) * 7.0, "t": -3.0})
	_rastro.append({"p": p, "t": -3.0})


func _toca(p: Vector2) -> bool:
	var d := p - global_position
	return (d.x / 39.0) ** 2 + (d.y / 13.0) ** 2 < 1.0


func _secar_rastro(delta: float) -> void:
	for r in _rastro:
		r["t"] += delta
	_rastro = _rastro.filter(func(r: Dictionary) -> bool: return r["t"] < 7.0)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha:
		for r in _rastro:
			if maisha.global_position.distance_to(r["p"]) < 9.0:
				maisha.call("pisar_oxido")
				break
	_capa_rastro.queue_redraw()


func _dibujar_rastro() -> void:
	for r in _rastro:
		var vida_r: float = clampf(1.0 - r["t"] / 7.0, 0.0, 1.0)
		var p: Vector2 = r["p"]
		_capa_rastro.draw_circle(p, 7.0, Color(0.61, 0.31, 0.14, 0.3 * vida_r))
		_capa_rastro.draw_circle(p + Vector2(2, -1), 3.0, Color(0.88, 0.6, 0.36, 0.22 * vida_r))


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.MAREADA:
		_herir(danio)
		return true
	_blanco = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	if fase == Fase.ARRASTRA:
		_cambiar(Fase.ESCONDIDA)
		Sonido.efecto("konokono_escondida")
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	# las explosiones de fuera rebotan en la concha... salvo si está mareada (fuera de la concha)
	if tipo == "explosion" and fase == Fase.MAREADA:
		_herir(R.KONOKONO_DANIO_DENTRO)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	var antes := _en_fase_2()
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	Impacto.pausa(0.07)
	Sonido.efecto("konokono_dolor")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.chispas = 4
	astillas.fuerza = 80.0
	astillas.position = global_position + Vector2(0, -31)
	get_parent().add_child(astillas)
	if vida <= 0:
		_vencer()
	elif _en_fase_2() and not antes:
		# llama a dos babosas
		for k in 2:
			var p: Vector2 = zona.global_position + Vector2(-1 + k * 2, -0.4) * zona.radios_umbral * 0.5
			zona.call("invocar_en", p, "babosa")


func _vencer() -> void:
	_cambiar(Fase.VENCIDO)
	Sonido.efecto("konokono_vencida")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	for b in get_tree().get_nodes_in_group("bolas_oxido"):
		b.queue_free()
	_dentro.clear()
	Impacto.temblar(4.5, 0.9)


func _proceso_vencido() -> void:
	if _t < 1.4:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_sprite.frame = MAREO
		if int(_t * 18.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 4
			astillas.fuerza = 60.0
			astillas.position = global_position + Vector2(randf_range(-24, 24), -randf_range(12, 57))
			get_parent().add_child(astillas)
	elif _t < 3.6:
		_sprite.frame = LIBRE if _t < 2.4 else CONTENTA
	else:
		# se aleja despacio hacia el agua y se desvanece
		_sprite.frame = LIBRE
		global_position += Vector2(_mira, 0) * 12.0 * get_process_delta_time()
		modulate.a = maxf(0.0, 1.0 - (_t - 3.6) / 1.6)
	if _t > 5.2 and is_in_group("jefes"):
		remove_from_group("jefes")
		if _barra:
			_barra.call("cerrar")
		destruido.emit()
		visible = false


# --- Dibujo -----------------------------------------------------------------------

func _animar() -> void:
	if fase == Fase.VENCIDO:
		return
	_sprite.flip_h = _mira < 0.0
	_sprite.rotation = 0.0
	match fase:
		Fase.PRESENTACION:
			_sprite.frame = CONCHA if _t < 0.8 else ARRASTRA_F[0]
		Fase.ARRASTRA:
			_sprite.frame = BOCA if _boca_abierta() else ARRASTRA_F[int(_tiempo * 2.5) % 2]
		Fase.MAREADA:
			_sprite.frame = MAREO
		Fase.ESCONDIDA, Fase.PREPARA_RUEDA:
			_sprite.frame = CONCHA
		Fase.RUEDA:
			_sprite.frame = RUEDA_F
			_sprite.rotation = _tiempo * 14.0 * _mira
		Fase.ESCUPE:
			_sprite.frame = BOCA
	_sprite.position.x = (sin(_tiempo * 50.0) * 1.0) if fase == Fase.PREPARA_RUEDA else 0.0
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color(1.0 + 0.06 * pulso, 1.0, 1.0 + 0.12 * pulso)
	queue_redraw()


func _boca_abierta() -> bool:
	# abre la boca cuando tiene una semilla cerca (¡aviso de que se la va a comer!)
	for s in get_tree().get_nodes_in_group("semillas"):
		if s.global_position.distance_to(_boca()) < 40.0:
			return true
	return false


func _draw() -> void:
	if fase == Fase.DORMIDO:
		return
	if fase != Fase.VENCIDO:
		var pulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
		for y in range(-3, 4):
			var ancho := int(round(34.0 * sqrt(1.0 - (y / 4.0) * (y / 4.0))))
			draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.66, 0.33, 0.84, 0.14 + 0.08 * pulso))
	# semillas que lleva dentro: brillan a través de la concha
	for i in _dentro.size():
		var p := Vector2(-4 + i * 6, -34)
		var parpadeo := 0.5 + 0.5 * sin(_tiempo * 20.0)
		draw_circle(p, 3.0, Color(1.0, 0.85, 0.4, 0.5 * parpadeo))
	if fase == Fase.MAREADA:
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(_mira * 34.0 + cos(a) * 7.0, -60.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))


## Durante la pelea, la cámara enseña el remanso entero
func _encuadrar(delta: float, maisha: Node2D) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase != Fase.DORMIDO and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (zona.global_position + Vector2(0, -10) - maisha.global_position) * 0.85
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()
