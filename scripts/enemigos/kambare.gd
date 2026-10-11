extends Node2D
## KAMBARE, EL SILURO DE CIENO: el minijefe del Lago Espejo.
## Un pez gato enorme al que Giza llenó de barro y óxido; mientras vive, remueve el fondo y el lago no se calma.
##
##   - NADA en su CHARCA de cieno, en medio de la arena: solo se ven las burbujas y la aleta. Ahí no se le puede dar.
##     Si Maisha pisa la charca, el barro la frena.
##   - APUNTA: una sombra en el suelo marca dónde va a caer, y SALTA hacia Maisha. Al caer levanta una OLA DE BARRO
##     en anillo que hace daño cerca.
##   - Queda VARADO coleteando en la orilla: el cetro le quita 1; una semilla que le estalle al lado, 2.
##     Luego VUELVE a la charca arrastrándose.
##   - Fase 2 (con la mitad de vida): desde la charca ESCUPE chorros de cieno en abanico (dejan charcos que frenan),
##     y a veces salta dos veces seguidas.
## Al vencerlo se le cae el barro: queda un siluro limpio, pardo dorado, que se va nadando, y el lago se aclara
## (marca «kambare_vencido»). Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "kambare").

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, NADA, APUNTA, SALTO, VARADO, VUELVE, ESCUPE, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const BOLA := preload("res://scripts/enemigos/bola_oxido.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "Kambare, el siluro de cieno"
const ASOMA := 0
const SALTA := 1
const VARADO_F := [2, 3]
const ESCUPE_F := 4
const ATURDIDO := 5
const LIBRE := 6
const CHARCA := Vector2(46, 22)          # semiejes de la charca de cieno (píxeles)

var zona: Node2D
var variante := "raiz"
var vida: int = R.KAMBARE_VIDA
var fase: int = Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _mira := 1.0
var _blanco := 0.0
var _desde := Vector2.ZERO               # de dónde salta / de dónde vuelve
var _hasta := Vector2.ZERO               # dónde caerá
var _alto := 0.0
var _saltos := 0                         # saltos seguidos que le quedan (fase 2: dos)
var _ola := -1.0                         # radio de la ola de barro (-1: no hay)
var _ola_pillo := false
var _nado := Vector2.ZERO                # adónde nada dentro de la charca
var _espera := 1.5
var _charcos: Array[Dictionary] = []     # charcos de cieno de los chorros (frenan)
var _sprite: Sprite2D
var _sombra: Node2D
var _capa: Node2D                        # la charca, la sombra del salto, la ola y los charcos (bajo todo)
var _barra: CanvasLayer


func _ready() -> void:
	add_to_group("jefes")
	_capa = Node2D.new()
	_capa.top_level = true
	_capa.z_index = -3
	_capa.draw.connect(_dibujar_capa)
	add_child(_capa)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 30.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/kambare.png" % variante)
	_sprite.hframes = 7
	_sprite.offset = Vector2(-8, -30)
	add_child(_sprite)
	visible = false


func _charca() -> Vector2:
	return zona.global_position if zona else global_position


func en_charca(p: Vector2) -> bool:
	var d := p - _charca()
	return (d.x / CHARCA.x) ** 2 + (d.y / CHARCA.y) ** 2 < 1.0


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.KAMBARE_VIDA
	visible = true
	modulate.a = 1.0
	global_position = _charca()
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("kambare_ruge")
	Impacto.temblar(3.0, 0.6)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.KAMBARE_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	vida = R.KAMBARE_VIDA
	_charcos.clear()
	_ola = -1.0
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
	return vida <= R.KAMBARE_VIDA / 2


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	_secar_charcos(delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta, maisha)
	_capa.queue_redraw()
	if fase == Fase.DORMIDO:
		return
	if maisha and fase != Fase.VENCIDO and en_charca(maisha.global_position):
		maisha.call("pisar_oxido", 0.2)                 # el cieno de la charca frena
	match fase:
		Fase.PRESENTACION:
			if _t > 1.8:
				_espera = 1.2
				_cambiar(Fase.NADA)
		Fase.NADA:
			_nadar(delta)
			_espera -= delta
			if _espera <= 0.0 and maisha:
				if _en_fase_2() and randf() < 0.45:
					_cambiar(Fase.ESCUPE)
				else:
					_saltos = 2 if _en_fase_2() and randf() < 0.5 else 1
					_apuntar(maisha)
		Fase.APUNTA:
			if maisha and _t < R.KAMBARE_AVISO * 0.4:
				_hasta = _donde_caer(maisha.global_position)    # sigue a Maisha un poco, luego se fija
			if _t >= R.KAMBARE_AVISO:
				_desde = global_position
				_cambiar(Fase.SALTO)
				Sonido.efecto("kambare_salta", 0.0, global_position)
		Fase.SALTO:
			var f := clampf(_t / R.KAMBARE_SALTO, 0.0, 1.0)
			global_position = _desde.lerp(_hasta, f)
			_alto = sin(f * PI) * 46.0
			if absf(_hasta.x - _desde.x) > 2.0:
				_mira = signf(_hasta.x - _desde.x)
			if f >= 1.0:
				_alto = 0.0
				_caer()
		Fase.VARADO:
			if _t >= R.KAMBARE_VARADO:
				_saltos -= 1
				if _saltos > 0 and maisha:
					_apuntar(maisha)
				else:
					_desde = global_position
					_cambiar(Fase.VUELVE)
		Fase.VUELVE:
			var f := clampf(_t / 0.9, 0.0, 1.0)
			global_position = _desde.lerp(_charca(), f)
			if absf(_charca().x - _desde.x) > 2.0:
				_mira = signf(_charca().x - _desde.x)
			if f >= 1.0:
				_espera = R.KAMBARE_ESPERA * (0.7 if _en_fase_2() else 1.0)
				_cambiar(Fase.NADA)
		Fase.ESCUPE:
			if _t >= 0.6 and _t - delta < 0.6:
				_escupir(maisha)
			if _t >= 1.3:
				_espera = R.KAMBARE_ESPERA
				_cambiar(Fase.NADA)
		Fase.VENCIDO:
			_proceso_vencido()
	_mover_ola(delta, maisha)
	_animar()


## Dentro de la charca, nada despacio de un lado a otro (solo asoman la aleta y las burbujas)
func _nadar(delta: float) -> void:
	if global_position.distance_to(_nado) < 3.0 or _nado == Vector2.ZERO:
		var a := randf() * TAU
		_nado = _charca() + Vector2(cos(a) * CHARCA.x, sin(a) * CHARCA.y) * randf_range(0.2, 0.6)
	var paso := (_nado - global_position).normalized() * 22.0 * delta
	if absf(paso.x) > 0.01:
		_mira = signf(paso.x)
	global_position += paso


func _apuntar(maisha: Node2D) -> void:
	_hasta = _donde_caer(maisha.global_position)
	_cambiar(Fase.APUNTA)
	Sonido.efecto("kambare_ruge", -6.0, global_position)


## Dónde caerá: donde está Maisha, dentro de la arena y fuera de la charca
func _donde_caer(p: Vector2) -> Vector2:
	if zona.distancia_normal(p) > 0.8:
		p = zona.global_position + (p - zona.global_position) * (0.8 / zona.distancia_normal(p))
	if en_charca(p):
		var d := (p - _charca())
		if d.length() < 1.0:
			d = Vector2.RIGHT
		p = _charca() + d.normalized() * Vector2(CHARCA.x + 14, CHARCA.y + 10).length() * 0.8
	return p


func _caer() -> void:
	_cambiar(Fase.VARADO)
	_ola = 4.0
	_ola_pillo = false
	Sonido.efecto("kambare_cae", 0.0, global_position)
	Impacto.temblar(3.5, 0.35)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.fuerza = 70.0
	astillas.position = global_position
	get_parent().add_child(astillas)


## La ola de barro: un anillo que se abre desde donde ha caído; hace daño a quien pille en el borde
func _mover_ola(delta: float, maisha: Node2D) -> void:
	if _ola < 0.0:
		return
	_ola += delta * 110.0
	if maisha and not _ola_pillo:
		var d := maisha.global_position.distance_to(_desde_ola())
		if absf(d - _ola) < 7.0:
			_ola_pillo = true
			maisha.call("recibir_danio", 1, _desde_ola(), "contacto")
	if _ola > R.KAMBARE_OLA:
		_ola = -1.0


func _desde_ola() -> Vector2:
	return _hasta


func _escupir(maisha: Node2D) -> void:
	if maisha == null:
		return
	Sonido.efecto("kambare_escupe", 0.0, global_position)
	var hacia := (maisha.global_position - global_position)
	for k in R.KAMBARE_CHORROS:
		var bola: Node2D = BOLA.new()
		bola.add_to_group("bolas_oxido")
		var ang := (k - (R.KAMBARE_CHORROS - 1) / 2.0) * 0.4
		var objetivo := global_position + hacia.rotated(ang)
		if zona.distancia_normal(objetivo) > 0.85:
			objetivo = zona.global_position + (objetivo - zona.global_position) * 0.7
		bola.desde = global_position + Vector2(_mira * 20.0, -14)
		bola.hasta = objetivo
		bola.al_caer = func(p: Vector2) -> void: _charcos.append({"p": p, "t": 0.0})
		get_parent().add_child(bola)


func _secar_charcos(delta: float) -> void:
	for c in _charcos:
		c["t"] += delta
	_charcos = _charcos.filter(func(c: Dictionary) -> bool: return c["t"] < 7.0)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha:
		for c in _charcos:
			if maisha.global_position.distance_to(c["p"]) < 12.0:
				maisha.call("pisar_oxido")
				break


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.VARADO:
		_herir(danio)
		return true
	_blanco = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	# las semillas solo le hacen daño fuera de la charca (varado)
	if tipo == "explosion" and fase == Fase.VARADO:
		_herir(R.KAMBARE_DANIO_SEMILLA)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	Impacto.pausa(0.07)
	Sonido.efecto("kambare_dolor", 0.0, global_position)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.chispas = 3
	astillas.fuerza = 70.0
	astillas.position = global_position + Vector2(0, -18)
	get_parent().add_child(astillas)
	if vida <= 0:
		_vencer()


func _vencer() -> void:
	_cambiar(Fase.VENCIDO)
	_ola = -1.0
	Sonido.efecto("kambare_vencido")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	for b in get_tree().get_nodes_in_group("bolas_oxido"):
		b.queue_free()
	_charcos.clear()
	Impacto.temblar(4.5, 0.9)
	Estado.marcar("kambare_vencido")


func _proceso_vencido() -> void:
	if _t < 1.4:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_sprite.frame = ATURDIDO
		if int(_t * 18.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 4
			astillas.fuerza = 60.0
			astillas.position = global_position + Vector2(randf_range(-30, 30), -randf_range(6, 30))
			get_parent().add_child(astillas)
	elif _t < 3.4:
		_sprite.frame = LIBRE
	else:
		# vuelve a la charca nadando y se hunde
		_sprite.frame = LIBRE
		global_position = global_position.move_toward(_charca(), 30.0 * get_process_delta_time())
		modulate.a = maxf(0.0, 1.0 - (_t - 3.4) / 1.6)
	if _t > 5.0 and is_in_group("jefes"):
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
	_sprite.visible = true
	match fase:
		Fase.PRESENTACION:
			_sprite.frame = ASOMA if _t < 1.0 else ESCUPE_F
		Fase.NADA:
			_sprite.frame = ASOMA
		Fase.APUNTA:
			_sprite.frame = ASOMA
		Fase.SALTO:
			_sprite.frame = SALTA
			_sprite.rotation = (0.4 - _t / R.KAMBARE_SALTO * 0.8) * _mira
		Fase.VARADO:
			_sprite.frame = VARADO_F[int(_tiempo * 6.0) % 2]
		Fase.VUELVE:
			_sprite.frame = VARADO_F[int(_tiempo * 9.0) % 2]
		Fase.ESCUPE:
			_sprite.frame = ESCUPE_F if _t > 0.3 else ASOMA
	# nadando, está medio hundido en la charca: solo asoman la cabeza, el lomo y la aleta
	var hundido := 9.0 if fase in [Fase.NADA, Fase.APUNTA] or (fase == Fase.PRESENTACION and _t < 1.0) else 0.0
	_sprite.position.y = -_alto + hundido + (sin(_tiempo * 2.0) * 1.0 if hundido > 0.0 else 0.0)
	_sombra.scale = Vector2.ONE * (1.0 - clampf(_alto / 90.0, 0.0, 0.5))
	_sombra.visible = fase != Fase.NADA
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color(1.0 + 0.05 * pulso, 1.0, 1.0 + 0.1 * pulso)
	queue_redraw()


func _draw() -> void:
	if fase == Fase.VARADO:
		# coletea mareado: estrellitas sobre la cabeza
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(_mira * 22.0 + cos(a) * 7.0, -46.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))


func _dibujar_capa() -> void:
	if fase == Fase.DORMIDO:
		return
	var c := _charca()
	# la charca de cieno, con su borde de barro, burbujas y brillos de Giza (se seca al vencerlo)
	var seca := clampf((_t - 1.4) / 2.5, 0.0, 1.0) if fase == Fase.VENCIDO else 0.0
	var pts := PackedVector2Array()
	for k in 40:
		var a := k * TAU / 40.0
		var r := 1.0 + 0.06 * sin(a * 5.0 + _tiempo * 0.8)
		pts.append(c + Vector2(cos(a) * CHARCA.x, sin(a) * CHARCA.y) * r)
	_capa.draw_colored_polygon(pts, Color(0.24, 0.17, 0.11, 0.9 * (1.0 - seca * 0.6)))
	pts.append(pts[0])
	_capa.draw_polyline(pts, Color(0.42, 0.3, 0.18, 0.9), 2.0)
	for k in 9:
		var f := fmod(_tiempo * 0.7 + k * 0.37, 1.0)
		var p := c + Vector2(sin(k * 2.3) * CHARCA.x * 0.7, cos(k * 1.7) * CHARCA.y * 0.6)
		_capa.draw_arc(p, 1.0 + f * 4.0, 0, TAU, 10, Color(0.62, 0.5, 0.34, (1.0 - f) * 0.7 * (1.0 - seca)), 1.0)
	if fase == Fase.NADA:
		# burbujas que siguen a Kambare bajo el cieno
		for k in 3:
			var f := fmod(_tiempo * 1.6 + k * 0.33, 1.0)
			_capa.draw_circle(global_position + Vector2(-_mira * k * 6.0, -2 - f * 4.0), 1.5 * (1.0 - f) + 0.5, Color(0.8, 0.7, 0.5, 0.8 * (1.0 - f)))
	# la sombra de dónde va a caer: crece y parpadea más deprisa justo antes de saltar
	if fase in [Fase.APUNTA, Fase.SALTO]:
		var f := clampf(_t / (R.KAMBARE_AVISO if fase == Fase.APUNTA else R.KAMBARE_SALTO), 0.0, 1.0)
		var r := 10.0 + (f * 18.0 if fase == Fase.APUNTA else 18.0)
		var a := 0.3 + 0.3 * sin(_tiempo * (10.0 + f * 20.0))
		_capa.draw_circle(_hasta, r, Color(0.1, 0.05, 0.03, 0.35 + 0.2 * f))
		_capa.draw_arc(_hasta, R.KAMBARE_OLA * 0.5, 0, TAU, 28, Color(0.66, 0.33, 0.84, a), 1.0)
	# la ola de barro
	if _ola >= 0.0:
		var alfa := 1.0 - _ola / R.KAMBARE_OLA
		_capa.draw_arc(_desde_ola(), _ola, 0, TAU, 36, Color(0.36, 0.25, 0.14, alfa), 4.0)
		_capa.draw_arc(_desde_ola(), _ola - 2.0, 0, TAU, 36, Color(0.7, 0.55, 0.36, alfa * 0.8), 1.5)
	# los charcos de los chorros
	for ch in _charcos:
		var v: float = clampf(1.0 - ch["t"] / 7.0, 0.0, 1.0)
		_capa.draw_circle(ch["p"], 11.0, Color(0.3, 0.21, 0.13, 0.55 * v))
		_capa.draw_circle(ch["p"] + Vector2(3, -2), 4.0, Color(0.6, 0.45, 0.3, 0.3 * v))


## Durante la pelea, la cámara enseña la arena entera
func _encuadrar(delta: float, maisha: Node2D) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase != Fase.DORMIDO and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (zona.global_position + Vector2(0, -10) - maisha.global_position) * 0.85
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()
