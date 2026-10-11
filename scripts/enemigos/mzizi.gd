extends Node2D
## MZIZI, LA RAÍZ DEL ARCO: el miniboss del Kitovu.
## La raíz que alimenta el Arco de Raíz. Giza se metió dentro, la volvió de piedra y la mueve como una serpiente.
##
## Ciclo:  ESCONDIDO → AVISO (el agujero se agrieta y brilla) → SALIENDO → FUERA (escupe piedras) → METIÉNDOSE
## Solo le hacen daño las semillas: una explosión que alcance su agujero mientras está fuera.
## Fase 2 (con la mitad de vida): avisa más rápido, escupe en abanico y llama a Petrinos.
## Al vencerla, la piedra se cae a trozos y debajo aparece madera viva; se hunde y el Arco despierta.
## Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "mzizi"): emite «destruido» al vencerla.

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, ESCONDIDO, AVISO, SALIENDO, FUERA, METIENDOSE, DOLOR, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const PIEDRA := preload("res://scripts/enemigos/piedra_mzizi.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "Mzizi, la raíz del Arco"
## Dónde están los agujeros, en proporción al tamaño de la arena (el primero, en el centro)
const AGUJEROS := [Vector2(0, 0.05), Vector2(-0.5, -0.32), Vector2(0.5, -0.36), Vector2(-0.45, 0.42), Vector2(0.48, 0.4)]
const ESCUPE_EN := [0.8, 2.0]     # segundos (desde que sale) en los que escupe
const SEGMENTOS := 7
const PASO := 7.5                 # píxeles entre segmento y segmento cuando está fuera del todo
const TIERRA := [Color("2b1e17"), Color("533b2d"), Color("7c5843"), Color("525649")]

var zona: Node2D
var variante := "raiz"
var vida: int = R.MZIZI_VIDA
var fase: int = Fase.DORMIDO

var _agujeros: Array[Sprite2D] = []
var _agujero := 0                 # en qué agujero está
var _tiempo_fase := 0.0
var _tiempo := 0.0
var _altura := 0.0                # 0 = bajo tierra, 1 = fuera del todo
var _escupidas := 0
var _boca_abierta := 0.0
var _blanco := 0.0
var _madera := 0.0                # al vencerla: 0 piedra, 1 madera
var _hoja_brilla := 0.0
var _cuerpo: Node2D
var _segmentos: Array[Sprite2D] = []
var _cabeza: Sprite2D
var _sombra: Node2D
var _barra: CanvasLayer
var _brillo: Node2D


func _ready() -> void:
	add_to_group("jefes")
	_cuerpo = Node2D.new()
	add_child(_cuerpo)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 15.0)
	_cuerpo.add_child(_sombra)
	var textura_cuerpo: Texture2D = load("res://arte/zonas/%s/mzizi_cuerpo.png" % variante)
	for i in SEGMENTOS:
		var s := Sprite2D.new()
		s.texture = textura_cuerpo
		s.hframes = 9
		_cuerpo.add_child(s)
		_segmentos.append(s)
	_cabeza = Sprite2D.new()
	_cabeza.texture = load("res://arte/zonas/%s/mzizi_cabeza.png" % variante)
	_cabeza.hframes = 11
	_cuerpo.add_child(_cabeza)
	_brillo = Node2D.new()
	_cuerpo.add_child(_brillo)
	_brillo.draw.connect(_dibujar_brillo)
	_crear_agujeros.call_deferred()
	_colocar_cuerpo()


func _crear_agujeros() -> void:
	var textura: Texture2D = load("res://arte/zonas/%s/agujero.png" % variante)
	for rel in AGUJEROS:
		var a := Sprite2D.new()
		a.texture = textura
		a.hframes = 4
		a.z_index = 2
		a.position = Vector2(rel) * zona.radios_umbral
		zona.add_child(a)
		_agujeros.append(a)
	global_position = _pos_agujero(0)


func _pos_agujero(i: int) -> Vector2:
	return zona.global_position + Vector2(AGUJEROS[i]) * zona.radios_umbral


# --- La pelea -------------------------------------------------------------------

## La zona se ha cerrado: sale por el agujero del centro y se presenta
func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.MZIZI_VIDA
	_agujero = 0
	global_position = _pos_agujero(0)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("mzizi_sale")
	Sonido.efecto("mzizi_rugido")
	_temblar(4.0, 1.2)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.MZIZI_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	# Maisha ha caído: vuelve a esconderse y espera a que vuelva a entrar
	for p in get_tree().get_nodes_in_group("piedras_mzizi"):
		p.queue_free()
	vida = R.MZIZI_VIDA
	_altura = 0.0
	_madera = 0.0
	if _barra:
		_barra.queue_free()
		_barra = null
	for a in _agujeros:
		a.frame = 0
	remove_from_group("daniables")
	remove_from_group("golpeables")
	fase = Fase.DORMIDO
	_colocar_cuerpo()


func _cambiar(nueva: int) -> void:
	fase = nueva
	_tiempo_fase = 0.0
	var fuera := nueva in [Fase.SALIENDO, Fase.FUERA, Fase.PRESENTACION]
	if fuera:
		add_to_group("golpeables")
	else:
		remove_from_group("golpeables")
	# en DOLOR y al meterse sigue pudiendo recibir los estallidos de las otras semillas
	# (recibir_danio comprueba que aún asome lo bastante del agujero)
	if fuera or nueva in [Fase.DOLOR, Fase.METIENDOSE]:
		add_to_group("daniables")
	else:
		remove_from_group("daniables")


func _en_fase_2() -> bool:
	return vida <= R.MZIZI_VIDA / 2


func _process(delta: float) -> void:
	_tiempo += delta
	_tiempo_fase += delta
	_encuadrar(delta)
	_blanco = maxf(0.0, _blanco - delta)
	_hoja_brilla = maxf(0.0, _hoja_brilla - delta)
	_boca_abierta = maxf(0.0, _boca_abierta - delta)
	match fase:
		Fase.PRESENTACION:
			_altura = minf(1.0, _tiempo_fase / 0.6)
			if _tiempo_fase > 0.4 and _tiempo_fase < 1.8:
				_boca_abierta = 0.1                               # ruge
			if _tiempo_fase > 2.4:
				_cambiar(Fase.METIENDOSE)
		Fase.ESCONDIDO:
			_altura = 0.0
			if _tiempo_fase >= R.MZIZI_ESCONDIDO * (0.75 if _en_fase_2() else 1.0):
				_elegir_agujero()
				_cambiar(Fase.AVISO)
				Sonido.efecto("mzizi_aviso", 0.0, global_position)
		Fase.AVISO:
			var aviso: float = R.MZIZI_AVISO_FASE2 if _en_fase_2() else R.MZIZI_AVISO
			_agujeros[_agujero].frame = 1
			_agujeros[_agujero].position.x = Vector2(AGUJEROS[_agujero]).x * zona.radios_umbral.x + (1.0 if int(_tiempo * 30.0) % 2 else -1.0) * 0.6
			if int(_tiempo_fase * 10.0) % 3 == 0:
				_polvo(_pos_agujero(_agujero), 2, 30.0)
			if _tiempo_fase >= aviso:
				_agujeros[_agujero].position.x = Vector2(AGUJEROS[_agujero]).x * zona.radios_umbral.x
				_agujeros[_agujero].frame = 2
				_polvo(_pos_agujero(_agujero), 10, 80.0)
				_temblar(2.5, 0.25)
				_cambiar(Fase.SALIENDO)
				Sonido.efecto("mzizi_sale", 0.0, global_position)
		Fase.SALIENDO:
			_altura = minf(1.0, _tiempo_fase / 0.3)
			_morder_si_encima()
			if _altura >= 1.0:
				_escupidas = 0
				_cambiar(Fase.FUERA)
		Fase.FUERA:
			_altura = 1.0
			_morder_si_encima()
			# escupe dos veces; abre la boca un momento antes (es el aviso para apartarse)
			for momento in ESCUPE_EN:
				if _tiempo_fase > momento - 0.35 and _tiempo_fase < momento + 0.15:
					_boca_abierta = 0.05
			if _escupidas < ESCUPE_EN.size() and _tiempo_fase >= ESCUPE_EN[_escupidas]:
				_escupir()
				_escupidas += 1
			if _tiempo_fase >= R.MZIZI_FUERA:
				_cambiar(Fase.METIENDOSE)
		Fase.METIENDOSE:
			_altura = maxf(0.0, 1.0 - _tiempo_fase / 0.45)
			if _altura <= 0.0:
				_agujeros[_agujero].frame = 0
				if _en_fase_2():
					_llamar_petrinos()
				_cambiar(Fase.ESCONDIDO)
		Fase.DOLOR:
			_altura = 1.0 if _tiempo_fase < 0.7 else maxf(0.0, 1.0 - (_tiempo_fase - 0.7) / 0.35)
			if _tiempo_fase > 1.05:
				_agujeros[_agujero].frame = 0
				_cambiar(Fase.ESCONDIDO)
		Fase.VENCIDO:
			_proceso_vencido()
	_colocar_cuerpo()


func _elegir_agujero() -> void:
	# un agujero distinto, mejor si no está justo debajo de Maisha (que le dé tiempo a reaccionar)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var opciones: Array[int] = []
	for i in _agujeros.size():
		if i == _agujero:
			continue
		if maisha and _pos_agujero(i).distance_to(maisha.global_position) < 18.0:
			continue
		opciones.append(i)
	if opciones.is_empty():
		opciones = [(_agujero + 1) % _agujeros.size()]
	_agujero = opciones[randi() % opciones.size()]
	global_position = _pos_agujero(_agujero)


func _morder_si_encima() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < 15.0:
		maisha.call("recibir_danio", R.MZIZI_SALIDA_DANIO, global_position, "contacto")


func _escupir() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var boca := global_position + Vector2(0, -_alto_total() + 14)
	Sonido.efecto("mzizi_escupe", 0.0, global_position)
	var hacia := (maisha.global_position - global_position).normalized()
	var angulos := [0.0] if not _en_fase_2() else [-0.35, 0.0, 0.35]
	for a in angulos:
		var piedra: Node2D = PIEDRA.new()
		piedra.direccion = hacia.rotated(a)
		piedra.position = global_position + hacia * 6.0
		piedra.altura = global_position.y - boca.y
		get_parent().add_child(piedra)


func _llamar_petrinos() -> void:
	var cuantos := R.MZIZI_PETRINOS_FASE2 - get_tree().get_nodes_in_group("enemigos").size()
	var otros: Array[int] = []
	for i in _agujeros.size():
		if i != _agujero:
			otros.append(i)
	otros.shuffle()
	for k in clampi(cuantos, 0, otros.size()):
		var p := _pos_agujero(otros[k]) + Vector2(0, 4)
		_polvo(p, 6, 60.0)
		zona.call("invocar_petrino_en", p)


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	_blanco = 0.04            # «clinc»: el cetro rebota en la piedra
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo != "explosion" or vida <= 0:
		return
	# mientras asome de su agujero, le alcanza CADA semilla que estalle: también las que se
	# soltaron seguidas y estallan una detrás de otra (antes, las que llegaban tarde se perdían)
	var en_dolor := fase == Fase.DOLOR
	var asoma := _altura >= R.MZIZI_ASOMA_GOLPEABLE
	if fase not in [Fase.SALIENDO, Fase.FUERA, Fase.PRESENTACION, Fase.DOLOR, Fase.METIENDOSE] or not asoma:
		return
	vida -= 1
	vida_cambiada.emit(vida)
	Impacto.pausa(0.08)
	_blanco = 0.35
	_hoja_brilla = 1.0
	_boca_abierta = 0.8                       # grita
	_temblar(3.0, 0.3)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 14
	astillas.chispas = 6
	astillas.fuerza = 100.0
	astillas.position = global_position + Vector2(0, -_alto_total() * 0.6)
	get_parent().add_child(astillas)
	if vida <= 0:
		_vencer()
	elif not en_dolor:
		_cambiar(Fase.DOLOR)
		Sonido.efecto("mzizi_dolor")
	else:
		Sonido.efecto("mzizi_dolor", -4.0)       # otro estallido mientras aún se retuerce
		# cada estallido la deja un poco más fuera, retorciéndose (para que las semillas que vienen
		# detrás también le lleguen)
		_tiempo_fase = minf(_tiempo_fase, R.MZIZI_DOLOR_GOLPEABLE)


func _vencer() -> void:
	Sonido.efecto("mzizi_vencido")
	Sonido.musica("", 1.5)
	_cambiar(Fase.VENCIDO)
	for p in get_tree().get_nodes_in_group("piedras_mzizi"):
		p.call("romper")
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	_temblar(5.0, 1.0)


## Vencida: tiembla, se le cae la piedra a trozos y debajo hay madera viva; luego se hunde
func _proceso_vencido() -> void:
	var t := _tiempo_fase
	_altura = 1.0
	if t < 1.2:
		_blanco = 0.05 if int(t * 8.0) % 2 == 0 else 0.0
		_boca_abierta = 0.1
	elif t < 2.4:
		_madera = (t - 1.2) / 1.2
		if int(t * 20.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 5
			astillas.chispas = 3
			astillas.fuerza = 60.0
			astillas.position = global_position + Vector2(randf_range(-10, 10), -randf_range(10, _alto_total()))
			get_parent().add_child(astillas)
	else:
		_madera = 1.0
		_hoja_brilla = 0.5
		_altura = maxf(0.0, 1.0 - (t - 3.2) / 2.0) if t > 3.2 else 1.0
		if t > 3.2 and int(t * 6.0) % 2 == 0:
			_polvo(global_position, 1, 30.0, true)
	if t > 5.4 and is_in_group("jefes"):
		remove_from_group("jefes")
		for a in _agujeros:
			a.frame = 3
		if _barra:
			_barra.call("cerrar")
		destruido.emit()
		visible = false


# --- Dibujo -----------------------------------------------------------------------

func _alto_total() -> float:
	return SEGMENTOS * PASO * _altura + 30.0 * _altura


func _colocar_cuerpo() -> void:
	_cuerpo.visible = _altura > 0.01
	_sombra.visible = _altura > 0.01
	var de_madera := _madera >= 0.5
	var balanceo := 1.0 if fase in [Fase.FUERA, Fase.PRESENTACION, Fase.AVISO] else 0.4
	var cabeza_y := 0.0
	for i in SEGMENTOS:
		var s := _segmentos[i]
		var t := float(i) / SEGMENTOS
		var y := -2.0 - i * PASO * _altura
		var x := sin(_tiempo * 2.2 - i * 0.55) * 3.0 * t * balanceo
		s.position = Vector2(x, y).round()
		s.visible = y < -1.0 or i == 0
		var tam := 0 if i < 3 else (1 if i < 5 else 2)
		s.frame = (6 + tam) if de_madera else tam * 2 + (i % 2)
		s.modulate = _color_actual()
		cabeza_y = y
	var cx := sin(_tiempo * 2.2 - SEGMENTOS * 0.55) * 3.0 * balanceo
	_cabeza.position = Vector2(cx, cabeza_y - 20.0 * _altura - 4.0).round()
	var grietas := clampi(int((R.MZIZI_VIDA - vida) * 4 / R.MZIZI_VIDA), 0, 3)
	if de_madera:
		_cabeza.frame = 10
	elif _blanco > 0.0:
		_cabeza.frame = 9 if _boca_abierta > 0.0 else 8
	else:
		_cabeza.frame = (4 if _boca_abierta > 0.0 else 0) + grietas
	_cabeza.modulate = _color_actual()
	queue_redraw()
	_brillo.queue_redraw()


func _color_actual() -> Color:
	# late con la luz violeta de Giza (no cuando ya es de madera)
	if _madera >= 0.5:
		return Color.WHITE
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	return Color(1.0 + 0.1 * pulso, 1.0, 1.0 + 0.18 * pulso)


func _draw() -> void:
	if fase == Fase.DORMIDO or _altura <= 0.01:
		return
	# un halo violeta (o dorado, cuando revive) en la boca del agujero
	var color := Color(0.66, 0.33, 0.84, 0.3) if _madera < 0.5 else Color(1.0, 0.95, 0.77, 0.35)
	for y in range(-3, 4):
		var ancho := int(round(16.0 * sqrt(1.0 - (y / 4.0) * (y / 4.0))))
		draw_rect(Rect2(-ancho, y, ancho * 2, 1), color)



## La hojita de su cabeza brilla cuando le duele (la vida del Arco sigue ahí dentro)
func _dibujar_brillo() -> void:
	if _hoja_brilla <= 0.0 or not _cuerpo.visible:
		return
	var hoja := _cabeza.position + Vector2(16, -6)
	for k in 6:
		var a := _tiempo * 4.0 + k * TAU / 6.0
		var p := (hoja + Vector2(cos(a), sin(a)) * (3.0 + 3.0 * (1.0 - minf(1.0, _hoja_brilla)))).round()
		_brillo.draw_rect(Rect2(p, Vector2.ONE), Color(0.44, 0.81, 0.31, minf(1.0, _hoja_brilla)))


func _polvo(donde: Vector2, cuantos: int, fuerza: float, dorado := false) -> void:
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = cuantos
	astillas.chispas = 0 if not dorado else cuantos
	astillas.fuerza = fuerza
	astillas.dura = 0.5
	astillas.colores = TIERRA if not dorado else [Color("fff3c4"), Color("6fcf4f")]
	astillas.position = donde
	get_parent().add_child(astillas)


## Durante la pelea, la cámara se centra a medio camino entre Maisha y la arena (para ver a Mzizi entero)
func _encuadrar(delta: float) -> void:
	var camara := get_viewport().get_camera_2d()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if camara == null or maisha == null:
		return
	var peleando := fase != Fase.DORMIDO and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (zona.global_position + Vector2(0, -24) - maisha.global_position) * 0.8
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()


func _temblar(fuerza: float, segundos: float) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null:
		return
	var t := create_tween()
	var pasos := int(segundos / 0.04)
	for i in pasos:
		var f := fuerza * (1.0 - float(i) / pasos)
		t.tween_property(camara, "offset", Vector2(randf_range(-f, f), randf_range(-f, f)).round(), 0.04)
	t.tween_property(camara, "offset", Vector2.ZERO, 0.04)
