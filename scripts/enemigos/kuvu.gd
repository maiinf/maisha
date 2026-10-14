extends Node2D
## KUVU, LA SETA QUE MANDA: el jefe de la cueva de las setas, bajo la casa de Nungu. Una seta enorme de Giza: en vez de
## comerse lo que cae (como las setas de Kimya), manda. Cuelga hilos de esporas y con uno tiene a NUNGU controlado.
##   1. NUNGU CONTROLADO (nungu_jefe.gd): Kuvu, cerrado e intocable, suelta NUBES DE ESPORAS (marean) cerca de Maisha.
##      Nungu rueda hecho bola hacia ella: con el ESCUDO de frente rebota y se marea, y un golpe de cetro le corta el hilo.
##   2. NUNGU LIBRE (2 contra 1): Nungu embiste el pie de Kuvu cada poco y Kuvu LEVANTA EL SOMBRERO (abrir): las
##      láminas al aire; ahí el cetro le quita 1 y una semilla 2. Kuvu responde con LATIGAZOS de hilo (aviso: una raya
##      violeta); el escudo, de frente, los para; si pillan, hacen daño y marean.
##   3. Con un tercio de vida, además, lanza un HILO LENTO hacia Nungu para volver a atraparlo: Maisha tiene que
##      ponerse en medio con el escudo. Si llega, Nungu vuelve a estar controlado (y hay que liberarlo otra vez).
## Al vencerlo, se marchita; Nungu se queda libre y habla (marcas «kuvu_vencido», «nungu_libre»).
## Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "kuvu"). Dibujo: arte/zonas/raiz/kuvu.png.

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, PELEA, ABIERTO, LATIGO, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NUNGU := preload("res://scripts/enemigos/nungu_jefe.gd")
const NUBE := preload("res://scripts/mundo/cueva/nube_esporas.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Kuvu, la seta que manda"
const VIOLETA := Color("c890f0")

var zona: Node2D
var variante := "raiz"
var vida: int = R.KUVU_VIDA
var fase: int = Fase.DORMIDO
var nungu: Node2D

var _t := 0.0
var _tiempo := 0.0
var _blanco := 0.0
var _esporas := 2.0
var _latigo := 3.0
var _latigo_hacia := Vector2.DOWN
var _latigo_pillo := false
var _hilo := -1.0                     # (fase 3) lo que ha avanzado el hilo lento hacia Nungu (-1: no hay)
var _hilo_cada := 6.0
var _sprite: Sprite2D
var _capa: Node2D
var _barra: CanvasLayer
var _luz: PointLight2D


func _ready() -> void:
	add_to_group("jefes")
	_capa = Node2D.new()
	_capa.top_level = true
	_capa.z_index = 2
	_capa.draw.connect(_dibujar_capa)
	add_child(_capa)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 30.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/kuvu.png" % variante)
	_sprite.hframes = 7
	_sprite.offset = Vector2(0, -38)
	_sprite.scale = Vector2(1.3, 1.3)              # (grande: es el jefe)
	add_child(_sprite)
	_luz = PointLight2D.new()
	_luz.texture = OSCURIDAD.textura_luz()
	_luz.texture_scale = 1.4
	_luz.color = Color(0.75, 0.5, 1.0)
	_luz.energy = 0.5
	_luz.position = Vector2(0, -40)
	add_child(_luz)


func _centro() -> Vector2:
	return zona.global_position if zona else global_position


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.KUVU_VIDA
	global_position = _centro() + Vector2(0, -34)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("bundi_ulula", -2.0, global_position)
	Impacto.temblar(3.0, 0.6)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.KUVU_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	if not is_instance_valid(nungu):
		nungu = NUNGU.new()
		nungu.kuvu = self
		nungu.position = _centro() + Vector2(0, 10)
		get_parent().add_child(nungu)
	nungu.atrapar()


func reiniciar() -> void:
	vida = R.KUVU_VIDA
	_hilo = -1.0
	if _barra:
		_barra.queue_free()
		_barra = null
	if is_instance_valid(nungu):
		nungu.queue_free()
		nungu = null
	_cambiar(Fase.DORMIDO)
	global_position = _centro() + Vector2(0, -34)


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	if nueva == Fase.ABIERTO:
		add_to_group("golpeables")
		add_to_group("daniables")
	else:
		remove_from_group("golpeables")
		remove_from_group("daniables")


func _fase_pelea() -> int:
	return 3 if vida <= R.KUVU_VIDA / 3 else (2 if vida <= R.KUVU_VIDA * 2 / 3 else 1)


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	_capa.queue_redraw()
	var maisha := _maisha()
	match fase:
		Fase.PRESENTACION:
			if _t > 2.0:
				_cambiar(Fase.PELEA)
		Fase.PELEA:
			_pelear(delta, maisha)
		Fase.LATIGO:
			if _t >= R.KUVU_LATIGO_AVISO and _t - delta < R.KUVU_LATIGO_AVISO:
				_latigazo(maisha)
			if _t >= R.KUVU_LATIGO_AVISO + 0.35:
				_cambiar(Fase.PELEA)
		Fase.ABIERTO:
			if _t >= R.KUVU_ABIERTO:
				_cambiar(Fase.PELEA)
		Fase.VENCIDO:
			_proceso_vencido()
	if fase in [Fase.PELEA, Fase.ABIERTO, Fase.LATIGO]:
		_mover_hilo(delta)
	var luz_meta := 0.5 if fase == Fase.DORMIDO else (1.3 if fase == Fase.ABIERTO else 0.9)
	if fase == Fase.VENCIDO:
		luz_meta = 0.2
	_luz.energy = move_toward(_luz.energy, luz_meta, delta * 2.0)
	_animar()


func _pelear(delta: float, maisha: Node2D) -> void:
	if maisha == null:
		return
	# las nubes de esporas, siempre
	_esporas -= delta
	if _esporas <= 0.0:
		_esporas = R.KUVU_ESPORAS_CADA * (0.75 if _fase_pelea() == 3 else 1.0)
		var nube: Node2D = NUBE.new()
		nube.dura = 6.0
		nube.position = maisha.global_position + Vector2(randf_range(-40, 40), randf_range(-30, 10))
		if zona:
			nube.position = zona.limitar(nube.position)
		get_parent().add_child(nube)
		Sonido.efecto("buibui_invoca", -4.0, global_position)
	if not is_instance_valid(nungu) or nungu.controlado():
		return
	# con Nungu libre: latigazos de hilo hacia Maisha, y (fase 3) el hilo lento hacia Nungu
	_latigo -= delta
	if _latigo <= 0.0:
		_latigo = R.KUVU_LATIGO_CADA * (0.7 if _fase_pelea() == 3 else 1.0)
		_latigo_hacia = (maisha.global_position - (global_position + Vector2(0, -30))).normalized()
		_latigo_pillo = false
		_cambiar(Fase.LATIGO)
		Sonido.efecto("bundi_conjura", -4.0, global_position)
	if _fase_pelea() == 3 and _hilo < 0.0:
		_hilo_cada -= delta
		if _hilo_cada <= 0.0:
			_hilo_cada = 7.0
			_hilo = 0.0


func _latigazo(maisha: Node2D) -> void:
	Sonido.efecto("raiz_azota", 0.0, global_position)
	if maisha == null:
		return
	var desde := global_position + Vector2(0, -30)
	var hacia := maisha.global_position + Vector2(0, -8) - desde
	# ¿está Maisha en la raya del latigazo?
	var a_lo_largo := hacia.dot(_latigo_hacia)
	var de_lado := absf(hacia.cross(_latigo_hacia))
	if a_lo_largo > 0.0 and a_lo_largo < 260.0 and de_lado < 14.0:
		if maisha.call("recibir_danio", 1, maisha.global_position - _latigo_hacia * 10.0, "latigo"):
			maisha.set("mareo", 2.0)


## (fase 3) el hilo lento: va de Kuvu a la cabeza de Nungu; si Maisha se pone en medio con el escudo, lo corta
func _mover_hilo(delta: float) -> void:
	if _hilo < 0.0 or not is_instance_valid(nungu) or nungu.controlado():
		_hilo = -1.0
		return
	var desde := global_position + Vector2(0, -30)
	var meta: Vector2 = nungu.cabeza()
	var largo := desde.distance_to(meta)
	_hilo += R.KUVU_HILO_LENTO * delta
	var punta := desde + (meta - desde).normalized() * minf(_hilo, largo)
	var maisha := _maisha()
	if maisha and maisha.get("escudo") and maisha.global_position.distance_to(punta + Vector2(0, 14)) < 18.0:
		_hilo = -1.0
		Sonido.efecto("clinc", 0.0, punta)
		Impacto.chispa(punta, -(meta - desde).normalized(), Color("f9d77a"))
		return
	if _hilo >= largo:
		_hilo = -1.0
		nungu.atrapar()


## Nungu le ha embestido el pie: levanta el sombrero (y se le puede dar)
func abrir() -> void:
	if fase in [Fase.PELEA, Fase.LATIGO]:
		_cambiar(Fase.ABIERTO)
		Sonido.efecto("kambare_cae", -2.0, global_position)
		Impacto.temblar(3.0, 0.3)


func puede_abrirse() -> bool:
	return fase == Fase.PELEA


func nungu_libre() -> void:
	_latigo = 2.0
	if zona:
		zona.mensaje.emit("Nungu: «¡Uf! ¡Mi cabeza vuelve a ser mía! ¡Te ayudo: yo le abro el sombrero!»")


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.ABIERTO:
		_herir(danio)
		return true
	_blanco = 0.04
	return false


func recibir_danio(_cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	if tipo == "explosion" and fase == Fase.ABIERTO:
		_herir(R.KUVU_DANIO_SEMILLA)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	Impacto.pausa(0.07)
	Sonido.efecto("petrino_golpeado", 0.0, global_position)
	if vida <= 0:
		_vencer()


func _vencer() -> void:
	_cambiar(Fase.VENCIDO)
	_hilo = -1.0
	Sonido.efecto("mascara_rompe")
	Sonido.musica("", 1.5)
	for n in get_tree().get_nodes_in_group("esporas"):
		n.call("disipar")
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	if is_instance_valid(nungu):
		nungu.calmar()
	Impacto.temblar(4.0, 1.0)
	Impacto.fogonazo(Color("d6a8f0"), 0.5, 0.6)


func _proceso_vencido() -> void:
	if _t < 1.6:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		if int(_t * 12.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 4
			astillas.position = global_position + Vector2(randf_range(-26, 26), -50)
			get_parent().add_child(astillas)
	elif is_in_group("jefes"):
		remove_from_group("jefes")
		if _barra:
			_barra.call("cerrar")
		Estado.marcar("kuvu_vencido")
		if zona and zona.get("modo_eco") and is_instance_valid(nungu):
			var t := nungu.create_tween()
			t.tween_interval(1.5)
			t.tween_property(nungu, "modulate:a", 0.0, 1.0)
			t.tween_callback(nungu.queue_free)
		destruido.emit()


# --- Dibujo ---------------------------------------------------------------------------

func _animar() -> void:
	modulate = Color(3, 3, 3) if _blanco > 0.0 else Color.WHITE
	match fase:
		Fase.ABIERTO:
			_sprite.frame = 4 if _blanco > 0.0 else 3
		Fase.LATIGO:
			_sprite.frame = 5
		Fase.VENCIDO:
			_sprite.frame = 6 if _t > 1.2 else 4
		_:
			_sprite.frame = 2 if _esporas < 0.6 and fase == Fase.PELEA else int(_tiempo * 1.5) % 2


func _dibujar_capa() -> void:
	if fase in [Fase.DORMIDO, Fase.VENCIDO]:
		return
	var desde := global_position + Vector2(0, -40)
	# el hilo que tiene a Nungu (de su sombrero a la cabeza de Nungu), con un brillo que corre
	if is_instance_valid(nungu) and nungu.controlado():
		var meta: Vector2 = nungu.cabeza()
		var medio := (desde + meta) / 2.0 + Vector2(0, 18)
		var puntos := PackedVector2Array()
		for k in 13:
			var t := k / 12.0
			puntos.append(desde.lerp(medio, t).lerp(medio.lerp(meta, t), t))
		_capa.draw_polyline(puntos, Color(0.9, 0.78, 1.0, 0.85), 1.0)
		var c := puntos[int(fmod(_tiempo * 8.0, 13.0))]
		_capa.draw_circle(c, 1.5, Color(1, 0.9, 1, 0.9))
	# el aviso del latigazo y el latigazo
	if fase == Fase.LATIGO:
		var largo := 260.0
		if _t < R.KUVU_LATIGO_AVISO:
			var a := 0.3 + 0.4 * sin(_t * 30.0)
			_capa.draw_line(desde, desde + _latigo_hacia * largo, Color(VIOLETA, a), 2.0)
		else:
			_capa.draw_line(desde, desde + _latigo_hacia * largo, Color(0.95, 0.85, 1.0, 0.9), 3.0)
	# el hilo lento de la fase 3, que va a por Nungu
	if _hilo >= 0.0 and is_instance_valid(nungu):
		var meta2: Vector2 = nungu.cabeza()
		var punta := desde + (meta2 - desde).normalized() * minf(_hilo, desde.distance_to(meta2))
		_capa.draw_line(desde, punta, Color(0.95, 0.75, 1.0, 0.8), 1.5)
		_capa.draw_circle(punta, 3.0 + sin(_tiempo * 10.0), Color(VIOLETA, 0.8))
