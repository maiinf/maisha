extends Node2D
## MAMBA, EL COCODRILO DE HERRUMBRE: el jefe de la dársena del Embarcadero Junco.
## Un cocodrilo viejo al que Giza cubrió de placas de hierro oxidado; tiene la plataforma de la dársena para él solo.
##
##   - ACECHA: flota como un tronco en el agua, dando vueltas alrededor de la plataforma (solo asoman los ojos y el
##     lomo). En el agua no se le puede dar.
##   - AVISA: se para en el borde, le brillan los ojos y una RAYA marca por dónde va a embestir (apunta a Maisha).
##   - EMBISTE: sale del agua y cruza la plataforma en línea recta con la boca abierta. Si pilla a Maisha, le hace
##     daño. Si llega al otro lado, se tira al agua y vuelve a acechar.
##   - Si en su camino hay un POSTE de amarre, SE LE CLAVAN LOS DIENTES en la madera y queda ATASCADO, tirando para
##     soltarse: el cetro le quita 1; una semilla que le estalle al lado, 2. (La gracia: ponerse detrás de un poste.)
##   - Fase 2 (con la mitad de vida): avisa más deprisa, a veces embiste dos veces seguidas y, al soltarse del
##     poste, da un COLETAZO en círculo que hace daño cerca.
## Al vencerlo se le cae la herrumbre: queda un cocodrilo verde y bronce, limpio, que se va nadando
## (marca «mamba_vencido»). Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "mamba").
## Los postes son las «ł» del mapa (grupo «postes»).

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, ACECHA, AVISA, EMBISTE, ATASCADO, COLETAZO, AL_AGUA, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "Mamba, el cocodrilo de herrumbre"
# fotogramas de arte/zonas/raiz/mamba.png
const FLOTA := 0
const EMBISTE_F := 1
const ATASCADO_F := [2, 3]
const COLETAZO_F := 4
const ATURDIDO := 5
const LIBRE := 6
const RADIO_POSTE := 13.0                # lo cerca que tiene que pasar el morro de un poste para clavarse

var zona: Node2D
var variante := "raiz"
var vida: int = R.MAMBA_VIDA
var fase: int = Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _mira := 1.0
var _blanco := 0.0
var _angulo := 0.0                       # dónde está en la ronda de agua (ángulo alrededor de la plataforma)
var _espera := 1.5
var _desde := Vector2.ZERO               # de dónde embiste
var _hacia := Vector2.RIGHT              # en qué dirección
var _hasta := Vector2.ZERO               # dónde acabaría si no se clava en nada
var _pillo := false                      # (en cada embestida, solo hace daño una vez)
var _poste: Node2D = null                # el poste en el que se ha clavado
var _seguidas := 0                       # embestidas seguidas que le quedan (fase 2: dos)
var _avisado := false                    # el consejo de los postes, solo la primera vez
var _coletazo := -1.0                    # radio del coletazo (-1: no hay)
var _coletazo_pillo := false
var _sprite: Sprite2D
var _sombra: Node2D
var _capa: Node2D                        # la raya del aviso, las ondas y el coletazo (bajo todo)
var _barra: CanvasLayer


func _ready() -> void:
	add_to_group("jefes")
	_capa = Node2D.new()
	_capa.top_level = true
	_capa.z_index = -1                   # (por encima del suelo de la zona y sus raíces)
	_capa.draw.connect(_dibujar_capa)
	add_child(_capa)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 34.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/mamba.png" % variante)
	_sprite.hframes = 7
	_sprite.offset = Vector2(-10, -22)
	add_child(_sprite)
	visible = false


func _centro() -> Vector2:
	return zona.global_position if zona else global_position


func _en_ronda(angulo: float) -> Vector2:
	return _centro() + Vector2(cos(angulo) * R.MAMBA_RONDA.x, sin(angulo) * R.MAMBA_RONDA.y)


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.MAMBA_VIDA
	visible = true
	modulate.a = 1.0
	_angulo = PI * 0.5
	global_position = _en_ronda(_angulo)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("mamba_ruge")
	Impacto.temblar(3.0, 0.6)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.MAMBA_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	vida = R.MAMBA_VIDA
	_coletazo = -1.0
	_poste = null
	if _barra:
		_barra.queue_free()
		_barra = null
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
	return vida <= R.MAMBA_VIDA / 2


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta, maisha)
	_capa.queue_redraw()
	if fase == Fase.DORMIDO:
		return
	match fase:
		Fase.PRESENTACION:
			if _t > 1.8:
				_espera = 1.0
				_cambiar(Fase.ACECHA)
		Fase.ACECHA:
			_acechar(delta, maisha)
			_espera -= delta
			if _espera <= 0.0 and maisha:
				_seguidas = 2 if _en_fase_2() and randf() < 0.5 else 1
				_apuntar(maisha)
		Fase.AVISA:
			var aviso := R.MAMBA_AVISO * (0.75 if _en_fase_2() else 1.0)
			if maisha and _t < aviso * 0.35:
				_fijar_raya(maisha.global_position)             # sigue a Maisha un poco, luego se fija
			if _t >= aviso:
				_pillo = false
				_cambiar(Fase.EMBISTE)
				Sonido.efecto("mamba_salta", 0.0, global_position)
		Fase.EMBISTE:
			_embestir(delta, maisha)
		Fase.ATASCADO:
			# tira del poste para soltarse (el poste tiembla)
			if is_instance_valid(_poste):
				_poste.position.x = _poste.get_meta("x0", _poste.position.x) + sin(_tiempo * 40.0) * 0.8
			if _t >= R.MAMBA_ATASCADO:
				_soltarse()
		Fase.COLETAZO:
			if _t >= 0.5:
				_al_agua()
		Fase.AL_AGUA:
			# vuelve a la ronda de agua más cercana, nadando
			var objetivo := _en_ronda(_angulo)
			global_position = global_position.move_toward(objetivo, 160.0 * delta)
			if global_position.distance_to(objetivo) < 2.0:
				_seguidas -= 1
				if _seguidas > 0 and maisha:
					_angulo += PI * 0.6 * (1.0 if randf() < 0.5 else -1.0)
					global_position = _en_ronda(_angulo)
					_apuntar(maisha)
				else:
					_espera = R.MAMBA_ACECHA * (0.7 if _en_fase_2() else 1.0)
					_cambiar(Fase.ACECHA)
		Fase.VENCIDO:
			_proceso_vencido()
	_mover_coletazo(delta, maisha)
	_animar()


## Flota alrededor de la plataforma, buscando el lado de Maisha
func _acechar(delta: float, maisha: Node2D) -> void:
	if maisha:
		var d := maisha.global_position - _centro()
		var deseado := atan2(d.y / R.MAMBA_RONDA.y, d.x / R.MAMBA_RONDA.x) + PI    # el lado contrario: para cruzar
		var dif := wrapf(deseado - _angulo, -PI, PI)
		_angulo += clampf(dif, -1.0, 1.0) * delta * 0.9
	var antes := global_position
	global_position = _en_ronda(_angulo)
	if absf(global_position.x - antes.x) > 0.05:
		_mira = signf(global_position.x - antes.x)


func _apuntar(maisha: Node2D) -> void:
	_fijar_raya(maisha.global_position)
	_cambiar(Fase.AVISA)
	Sonido.efecto("mamba_ruge", -8.0, global_position)
	if not _avisado and zona:
		_avisado = true
		zona.mensaje.emit("¡Ponte detrás de un poste!")


## La raya: desde donde está, pasando por Maisha, hasta el otro lado de la plataforma
func _fijar_raya(objetivo: Vector2) -> void:
	_desde = global_position
	_hacia = (objetivo - _desde).normalized()
	if _hacia == Vector2.ZERO:
		_hacia = (_centro() - _desde).normalized()
	var largo := 2.2 * R.MAMBA_RONDA.y
	var p := _desde
	for i in 80:
		p = _desde + _hacia * (largo * (i + 1) / 80.0)
		var d := p - _centro()
		if i > 20 and (d.x / R.MAMBA_RONDA.x) ** 2 + (d.y / R.MAMBA_RONDA.y) ** 2 > 1.0:
			break
	_hasta = p
	if absf(_hacia.x) > 0.1:
		_mira = signf(_hacia.x)


func _embestir(delta: float, maisha: Node2D) -> void:
	global_position += _hacia * R.MAMBA_VELOCIDAD * delta
	var morro := global_position + _hacia * 18.0
	# ¿un poste en el camino?
	for poste in get_tree().get_nodes_in_group("postes"):
		if (poste as Node2D).global_position.distance_to(morro) < RADIO_POSTE:
			_clavarse(poste)
			return
	if maisha and not _pillo and maisha.global_position.distance_to(global_position + _hacia * 8.0) < 20.0:
		_pillo = true
		maisha.call("recibir_danio", 1, global_position, "contacto")
	if global_position.distance_to(_desde) >= _desde.distance_to(_hasta):
		# ha cruzado sin clavarse: se tira al agua por el otro lado
		_angulo = atan2((global_position - _centro()).y / R.MAMBA_RONDA.y, (global_position - _centro()).x / R.MAMBA_RONDA.x)
		_al_agua()


func _clavarse(poste: Node2D) -> void:
	_poste = poste
	if not poste.has_meta("x0"):
		poste.set_meta("x0", poste.position.x)
	global_position = poste.global_position - _hacia * 20.0
	_cambiar(Fase.ATASCADO)
	Sonido.efecto("mamba_muerde", 0.0, global_position)
	Impacto.temblar(3.0, 0.3)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.fuerza = 80.0
	astillas.position = poste.global_position + Vector2(0, -10)
	get_parent().add_child(astillas)
	# el poste queda mordido
	for h in poste.get_children():
		if h is Sprite2D and (h as Sprite2D).hframes > 1:
			(h as Sprite2D).frame = 1


func _soltarse() -> void:
	if is_instance_valid(_poste):
		_poste.position.x = _poste.get_meta("x0", _poste.position.x)
	_poste = null
	Sonido.efecto("mamba_ruge", -4.0, global_position)
	if _en_fase_2():
		_cambiar(Fase.COLETAZO)
		_coletazo = 6.0
		_coletazo_pillo = false
		Sonido.efecto("mamba_coletazo", 0.0, global_position)
	else:
		_al_agua()


func _al_agua() -> void:
	var d := global_position - _centro()
	_angulo = atan2(d.y / R.MAMBA_RONDA.y, d.x / R.MAMBA_RONDA.x)
	_cambiar(Fase.AL_AGUA)
	Sonido.efecto("mamba_salta", -6.0, global_position)


## El coletazo: un anillo que se abre desde donde estaba atascado; hace daño a quien pille en el borde
func _mover_coletazo(delta: float, maisha: Node2D) -> void:
	if _coletazo < 0.0:
		return
	_coletazo += delta * 120.0
	if maisha and not _coletazo_pillo:
		var d := maisha.global_position.distance_to(global_position)
		if absf(d - _coletazo) < 7.0:
			_coletazo_pillo = true
			maisha.call("recibir_danio", 1, global_position, "contacto")
	if _coletazo > R.MAMBA_COLETAZO:
		_coletazo = -1.0


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.ATASCADO:
		_herir(danio)
		return true
	_blanco = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	# las semillas solo le hacen daño con los dientes clavados
	if tipo == "explosion" and fase == Fase.ATASCADO:
		_herir(R.MAMBA_DANIO_SEMILLA)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	Impacto.pausa(0.07)
	Sonido.efecto("mamba_dolor", 0.0, global_position)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.chispas = 3
	astillas.fuerza = 70.0
	astillas.position = global_position + Vector2(0, -12)
	get_parent().add_child(astillas)
	if vida <= 0:
		_vencer()


func _vencer() -> void:
	if is_instance_valid(_poste):
		_poste.position.x = _poste.get_meta("x0", _poste.position.x)
	_cambiar(Fase.VENCIDO)
	_coletazo = -1.0
	Sonido.efecto("mamba_vencido")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	Impacto.temblar(4.5, 0.9)
	Estado.marcar("mamba_vencido")


func _proceso_vencido() -> void:
	if _t < 1.4:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_sprite.frame = ATURDIDO
		if int(_t * 18.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 4
			astillas.fuerza = 60.0
			astillas.position = global_position + Vector2(randf_range(-34, 34), -randf_range(4, 20))
			get_parent().add_child(astillas)
	elif _t < 3.4:
		_sprite.frame = LIBRE
	else:
		# se va nadando hacia el canal del río y se hunde
		_sprite.frame = LIBRE
		_mira = 1.0
		_sprite.flip_h = false
		global_position += Vector2(40.0, 6.0) * get_process_delta_time()
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
	match fase:
		Fase.PRESENTACION:
			_sprite.frame = FLOTA if _t < 1.0 else EMBISTE_F
		Fase.ACECHA, Fase.AVISA, Fase.AL_AGUA:
			_sprite.frame = FLOTA
		Fase.EMBISTE:
			_sprite.frame = EMBISTE_F
		Fase.ATASCADO:
			_sprite.frame = ATASCADO_F[int(_tiempo * 7.0) % 2]
		Fase.COLETAZO:
			_sprite.frame = COLETAZO_F
	# en el agua, medio hundido: solo asoman los ojos y el lomo (y se mece)
	var en_agua := fase in [Fase.ACECHA, Fase.AVISA, Fase.AL_AGUA] or (fase == Fase.PRESENTACION and _t < 1.0)
	_sprite.position.y = (5.0 + sin(_tiempo * 2.0) * 1.0) if en_agua else 0.0
	_sombra.visible = not en_agua
	var ojos := 0.5 + 0.5 * sin(_tiempo * (12.0 if fase == Fase.AVISA else 3.0))
	if _blanco > 0.0:
		_sprite.modulate = Color(3, 3, 3)
	elif fase == Fase.AVISA:
		_sprite.modulate = Color(1.0 + 0.3 * ojos, 1.0, 1.0 + 0.4 * ojos)
	else:
		_sprite.modulate = Color(1, 1, 1)
	queue_redraw()


func _draw() -> void:
	if fase == Fase.ATASCADO:
		# tira y se marea: estrellitas sobre la cabeza
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(_mira * 16.0 + cos(a) * 7.0, -30.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))


func _dibujar_capa() -> void:
	if fase == Fase.DORMIDO:
		return
	# las ondas que deja en el agua al acechar
	if fase in [Fase.ACECHA, Fase.AVISA, Fase.AL_AGUA]:
		for k in 3:
			var f := fmod(_tiempo * 0.9 + k * 0.33, 1.0)
			_capa.draw_arc(global_position + Vector2(0, 2), 10.0 + f * 22.0, 0, TAU, 24, Color(0.62, 0.82, 0.82, (1.0 - f) * 0.45), 1.0)
	# la raya del aviso: por dónde va a embestir (parpadea más deprisa justo antes)
	if fase == Fase.AVISA:
		var aviso := R.MAMBA_AVISO * (0.75 if _en_fase_2() else 1.0)
		var f := clampf(_t / aviso, 0.0, 1.0)
		var a := 0.35 + 0.35 * sin(_tiempo * (10.0 + f * 24.0))
		var largo := _desde.distance_to(_hasta)
		var tramos := int(largo / 10.0)
		for i in tramos:
			if i % 2 == 0:
				var p0 := _desde + _hacia * (i * 10.0)
				_capa.draw_line(p0, p0 + _hacia * 7.0, Color(0.05, 0.02, 0.08, a * 0.6), 5.0)
				_capa.draw_line(p0, p0 + _hacia * 7.0, Color(0.85, 0.6, 1.0, a + 0.2), 2.5)
		_capa.draw_circle(_hasta, 5.0, Color(0.85, 0.6, 1.0, a + 0.2))
	# el coletazo
	if _coletazo >= 0.0:
		var alfa := 1.0 - _coletazo / R.MAMBA_COLETAZO
		_capa.draw_arc(global_position, _coletazo, 0, TAU, 36, Color(0.62, 0.82, 0.82, alfa), 3.0)
		_capa.draw_arc(global_position, _coletazo - 3.0, 0, TAU, 36, Color(0.66, 0.33, 0.84, alfa * 0.6), 1.5)


## Durante la pelea, la cámara enseña la dársena entera
func _encuadrar(delta: float, maisha: Node2D) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase != Fase.DORMIDO and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (_centro() + Vector2(0, -6) - maisha.global_position) * 0.85
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()
