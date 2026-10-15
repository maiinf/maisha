extends "res://scripts/mundo/escena_mundo.gd"
## EL KITOVU: donde empieza el juego. El centro del mundo, gris y roto.
##   1. Maisha despierta en un cráter, sin nada y entumecida (anda despacio), y se pregunta dónde está.
##   2. Una chispa de vida la guía por el valle: el pozo, la torre y el monumento. En cada sitio,
##      un recuerdo (una imagen fija y sus pensamientos). Al final, la chispa entra en su brote.
##   3. Se oye cloquear: Kuku, la gallina de Mzee Shamba, se ha escapado. Huye, se cansa y se coge.
##   4. Con la gallina en brazos, en la puerta de la granja: el castor sale desconfiado y se ablanda.
##      Dentro: la cena, una noche junto al fuego y, a la mañana siguiente, las tareas
##      (zanahorias, un pez y la cerca). Al terminarlas, el cetro de su familia y el mapa partido.
##   4. Giza ha dejado manchas por el valle: 3 zonas de práctica (cada partida en sitios y con formas distintas).
##      El narrador enseña algo en cada una: golpe y semillas, Latido y Aliento, y la última «a solas».
##   5. Limpias las tres, despierta Mzizi, la raíz del Arco (miniboss). Al vencerla, el Arco se abre.
## Sin cetro, las manchas están dormidas y Maisha no se atreve a acercarse.

const CHARLA := preload("res://scripts/mundo/charla.gd")
const CHISPA := preload("res://scripts/mundo/kitovu/chispa_vida.gd")
const GALLINA_PERDIDA := preload("res://scripts/mundo/kitovu/gallina_perdida.gd")
const GALLINA := preload("res://scripts/mundo/kitovu/gallina.gd")
const ALDEANO := preload("res://scripts/mundo/aldea/aldeano.gd")
const TEXTURA_GALLINA := preload("res://arte/mundos/kitovu/gallina.png")
## Los sitios a los que guía la chispa de vida (casillas): el pozo, la torre y el monumento
const SITIOS_CHISPA := [Vector2i(11, 15), Vector2i(25, 10), Vector2i(36, 12)]
## el camino de la chispa hasta cada sitio: por el camino de tierra, rodeando la granja por el este
## (el estanque, la acequia y la rueda del molino cierran el paso por el oeste) y lejos de las manchas
const RUTAS_CHISPA := [
	[Vector2i(12, 37), Vector2i(17, 34), Vector2i(23, 30), Vector2i(30, 28), Vector2i(37, 26), Vector2i(38, 21), Vector2i(36, 17), Vector2i(30, 14), Vector2i(22, 13), Vector2i(17, 14)],
	[Vector2i(18, 13)],
	[],
]
const SITIO_KUKU := Vector2i(21, 19)          # donde anda Kuku perdida: en la hierba, lejos de las manchas
const KUKU_EN_GRANJA := Vector2(536, 412)
const GRANJA := Vector2(520, 380)          # centro de la granja (el oasis de color)
const GRANJA_RADIOS := Vector2(300, 170)

var _practicas: Array[Node2D] = []   # las zonas de práctica de esta partida
var _arena: Node2D                     # la arena de Mzizi
var _pelea: Node2D                     # la zona en la que se está peleando ahora
var _enemigos_antes := -1
var _empujada := 0.0
var _chispa: Node2D
var _kuku: Node2D
var _llevada: Sprite2D                 # Kuku en brazos de Maisha
var _puerta_casa: Area2D
var _encuentro_hecho := false
var _brillo_brote: Node2D
var _destello_brote := 0.0
var _avisos_kuku := 0


func _ready() -> void:
	super()
	$Corrupcion.registrar_oasis(GRANJA, GRANJA_RADIOS, 40.0)
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.jefe != "":
			_arena = z
		else:
			_practicas.append(z)
		z.mensajes = false          # aquí explica las cosas el narrador
		for conexion in z.mensaje.get_connections():
			z.mensaje.disconnect(conexion["callable"])
		z.estado_cambiado.connect(_al_cambiar_zona.bind(z))
	_activar_zonas()
	_preparar_comienzo()
	for e in get_tree().get_nodes_in_group("espantapajaros"):
		e.golpeado.connect(_al_golpear_espantapajaros)
	if not Estado.tiene("kitovu_despierta"):
		_despertar.call_deferred()
	elif Estado.tiene("cetro_recibido") and not Estado.tiene("narr/cetro"):
		_narrar.call_deferred("narrador_cetro", "narr/cetro", 0.8)


## Con el cetro, las manchas despiertan; la arena de Mzizi, solo cuando no queda ninguna
func _activar_zonas() -> void:
	var cetro := Estado.tiene("cetro_recibido")
	for z in _practicas:
		z.activa = cetro
	if _arena:
		_arena.activa = cetro and practicas_limpias() >= _practicas.size()


## Cuántas zonas de práctica se han purgado ya
func practicas_limpias() -> int:
	var n := 0
	for z in _practicas:
		if z.estado == 4:
			n += 1
	return n


func _poner_sonido() -> void:
	if not Estado.tiene("kitovu_despierta"):
		# partida nueva: sigue la música del despertar (o empieza, si no venía sonando) y luego la del Kitovu
		Sonido.musica("despertar", 2.0, "kitovu")
		Sonido.ambiente(_ambiente_de_escena())
	else:
		super()


func _despertar() -> void:
	_maisha.set("puede_actuar", false)
	_maisha.set("lentitud", 0.4)                     # entumecida: le cuesta andar
	_maisha.call("expresar", "despertar")            # sentada en el cráter, abre los ojos y se levanta
	await get_tree().create_timer(2.2).timeout
	await CHARLA.hablar(self, "maisha_despierta")
	_maisha.call("recuperar_lentitud", 15.0)          # (lo lleva Maisha: así no se queda entumecida si algo se corta)
	await get_tree().create_timer(1.5).timeout
	_aparecer_chispa(true)


# --- El comienzo pausado: la chispa de vida, Kuku y la puerta -------------------------

func _preparar_comienzo() -> void:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "casa_shamba":
			_puerta_casa = p
	if _puerta_casa:
		# hasta devolver a Kuku no abre nadie (a quien ya conoce a Shamba de antes, le abre siempre)
		_puerta_casa.cerrada_hasta = "" if Estado.tiene("shamba_conocido") else "kuku_devuelta"
		_puerta_casa.cerrada.connect(_puerta_cerrada)
	_crear_brillo_brote()
	if Estado.tiene("kitovu_despierta") and not Estado.tiene("recuerdo_3") and not Estado.tiene("shamba_conocido"):
		_aparecer_chispa.call_deferred(false)
	if Estado.tiene("kuku_perdida") and not Estado.tiene("kuku_cogida"):
		_soltar_kuku()
	if Estado.tiene("kuku_cogida") and not Estado.tiene("kuku_devuelta"):
		_llevar_kuku()
	if Estado.tiene("kuku_devuelta"):
		var kuku: Node2D = GALLINA.new()
		kuku.position = KUKU_EN_GRANJA
		$Entidades.add_child(kuku)
	if Estado.tiene("amanecer_granja") and not Estado.tiene("amanecer_visto"):
		_amanecer()


func _recuerdos() -> int:
	var n := 0
	for i in 3:
		if Estado.tiene("recuerdo_%d" % (i + 1)):
			n += 1
	return n


func _aparecer_chispa(primera: bool) -> void:
	_chispa = CHISPA.new()
	for c in SITIOS_CHISPA:
		_chispa.sitios.append(Vector2(c) * 16.0 + Vector2(8, 14))
	for ruta in RUTAS_CHISPA:
		var puntos: Array = []
		for c in ruta:
			puntos.append(Vector2(c) * 16.0 + Vector2(8, 14))
		_chispa.rutas.append(puntos)
	_chispa.indice = _recuerdos()
	_chispa.position = _maisha.global_position + Vector2(34, -34)
	add_child(_chispa)
	if primera:
		_maisha.call("expresar", "sorpresa")
	_chispa.llegada.connect(_al_llegar_chispa)
	_chispa.terminada.connect(_al_terminar_chispa)
	Sonido.efecto("chispa")
	if primera:
		await CHARLA.hablar(self, "kitovu_chispa")


func _al_llegar_chispa(indice: int) -> void:
	_maisha.set("puede_actuar", false)
	Sonido.fanfarria("recuerdo")
	_destello_brote = 1.0
	await CHARLA.hablar(self, "recuerdo_%d" % (indice + 1))
	if is_instance_valid(_chispa):
		_chispa.seguir()


func _al_terminar_chispa() -> void:
	_destello_brote = 2.0
	await get_tree().create_timer(2.5).timeout
	Estado.marcar("kuku_perdida")
	_soltar_kuku()
	Sonido.efecto("gallina_cacareo")
	await CHARLA.hablar(self, "kitovu_cacareo")


func _soltar_kuku() -> void:
	_kuku = GALLINA_PERDIDA.new()
	_kuku.position = Vector2(SITIO_KUKU) * 16.0 + Vector2(8, 14)
	$Entidades.add_child(_kuku)
	_kuku.cogida.connect(_al_coger_kuku)


func _al_coger_kuku() -> void:
	Estado.marcar("kuku_cogida")
	_llevar_kuku()
	await CHARLA.hablar(self, "kitovu_kuku_cogida")


func _llevar_kuku() -> void:
	_llevada = Sprite2D.new()
	_llevada.texture = TEXTURA_GALLINA
	_llevada.hframes = 2
	_llevada.position = Vector2(0, -36)
	_llevada.z_index = 1
	_maisha.add_child(_llevada)


func _puerta_cerrada() -> void:
	Sonido.efecto("llamar_puerta")
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if dialogo and not dialogo.hablando and _llevada == null:
		CHARLA.hablar(self, "kitovu_puerta_cerrada")


## Con Kuku en brazos, en la puerta: el castor sale desconfiado... y se ablanda
func _encuentro() -> void:
	_encuentro_hecho = true
	_maisha.set("puede_actuar", false)
	Sonido.efecto("puerta")
	_maisha.call("expresar", "sorpresa")
	var shamba: Node2D = ALDEANO.new()
	shamba.id = "shamba"
	shamba.position = _puerta_casa.global_position + Vector2(0, 12)
	shamba.modulate.a = 0.0
	$Entidades.add_child(shamba)
	create_tween().tween_property(shamba, "modulate:a", 1.0, 0.4)
	_maisha.call("mirar", Vector2.UP)
	await get_tree().create_timer(0.7).timeout
	await CHARLA.hablar(shamba, "shamba")
	# Kuku salta al suelo y se queda en su granja
	if is_instance_valid(_llevada):
		_llevada.queue_free()
		_llevada = null
	var kuku: Node2D = GALLINA.new()
	kuku.position = _maisha.global_position + Vector2(14, 6)
	$Entidades.add_child(kuku)
	Sonido.efecto("gallina_cacareo", -4.0)
	await CHARLA.hablar(self, "kitovu_tras_puerta")
	# el castor entra en casa y deja la puerta abierta
	Sonido.efecto("puerta")
	var t := create_tween()
	t.tween_property(shamba, "modulate:a", 0.0, 0.4)
	t.tween_callback(shamba.queue_free)
	_maisha.set("puede_actuar", true)


## El brote de Maisha brilla un poco más con cada recuerdo
func _crear_brillo_brote() -> void:
	_brillo_brote = Node2D.new()
	_brillo_brote.position = Vector2(0, -30)
	_brillo_brote.z_index = 2
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_brillo_brote.material = mat
	_maisha.add_child(_brillo_brote)
	_brillo_brote.draw.connect(_dibujar_brillo_brote)


func _dibujar_brillo_brote() -> void:
	if Estado.tiene("cetro_recibido"):
		return
	var nivel := _recuerdos() / 3.0 * 0.6 + minf(1.0, _destello_brote)
	if nivel <= 0.01:
		return
	var pulso := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 400.0)
	for i in 3:
		_brillo_brote.draw_circle(Vector2.ZERO, 3.0 + i * 4.0 + pulso * 1.5, Color(0.25, 0.55, 0.2, 0.12 * nivel))


## A la mañana siguiente, al salir de la casa: la luz del amanecer, que se va aclarando
func _amanecer() -> void:
	Estado.marcar("amanecer_visto")
	var luz := CanvasModulate.new()
	luz.color = Color(1.0, 0.76, 0.62)
	add_child(luz)
	var t := create_tween()
	t.tween_property(luz, "color", Color.WHITE, 28.0).set_trans(Tween.TRANS_SINE)
	t.tween_callback(luz.queue_free)


## El narrador habla una sola vez por cada cosa (la marca lo recuerda)
func _narrar(id: String, marca: String, espera := 0.0) -> void:
	if Estado.tiene(marca):
		return
	Estado.marcar(marca)
	if espera > 0.0:
		await get_tree().create_timer(espera).timeout
	await CHARLA.hablar(self, id)


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "cetro_recibido":
		_activar_zonas()


func _al_golpear_espantapajaros(veces: int) -> void:
	if veces == 3:
		_narrar("narrador_espantapajaros", "narr/espantapajaros", 0.3)


func _al_cambiar_zona(estado: int, zona: Node2D) -> void:
	if zona == _arena:
		match estado:
			1:   # AVISO
				_narrar("narrador_arena", "narr/arena")
			2:   # CERRADA: Mzizi sale y ruge; luego habla el narrador
				_pelea = zona
				_narrar("narrador_mzizi", "narr/mzizi", 1.6)
			4:   # PURGADA
				await _narrar("narrador_purgada", "narr/purgada", 0.6)
				Estado.marcar("portal_raiz")
		return
	# las manchas: el narrador enseña una cosa en cada una, según cuántas se han limpiado ya
	var limpias := practicas_limpias()
	match estado:
		1:
			match limpias:
				0: _narrar("narrador_zona", "narr/zona")
				1: _narrar("narrador_zona2", "narr/zona2")
				2: _narrar("narrador_zona3", "narr/zona3")
		2:
			_pelea = zona
			_enemigos_antes = -1
			if limpias == 0:
				_narrar("narrador_cerrada", "narr/cerrada", 0.5)
			# si su aviso saltó antes de tiempo (dos manchas muy juntas: Maisha pisó el borde de la otra
			# mientras peleaba en la primera), la lección de esta mancha se da ahora, al cerrarse
			elif limpias == 1:
				_narrar("narrador_zona2", "narr/zona2")
			elif limpias == 2:
				_narrar("narrador_zona3", "narr/zona3")
		4:
			_pelea = null
			if limpias >= _practicas.size():
				await _narrar("narrador_despierta", "narr/despierta", 0.8)
				Sonido.efecto("temblor")
				_temblar_suelo()
				_activar_zonas()
			elif limpias == 1:
				_narrar("narrador_purgada1", "narr/purgada1", 0.8)
			elif limpias == 2:
				_narrar("narrador_purgada2", "narr/purgada2", 0.8)


func _temblar_suelo() -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null:
		return
	var t := create_tween()
	for i in 20:
		var f := 3.0 * (1.0 - i / 20.0)
		t.tween_property(camara, "offset", Vector2(randf_range(-f, f), randf_range(-f, f)).round(), 0.05)
	t.tween_property(camara, "offset", Vector2.ZERO, 0.05)


func _process(delta: float) -> void:
	_empujada = maxf(0.0, _empujada - delta)
	_destello_brote = maxf(0.0, _destello_brote - delta * 0.6)
	if _brillo_brote:
		_brillo_brote.queue_redraw()
	# Kuku en brazos: se mueve un poco; y en la puerta, el encuentro con el castor
	if _llevada:
		_llevada.frame = int(Time.get_ticks_msec() / 300) % 2 if int(Time.get_ticks_msec() / 1500) % 3 == 0 else 0
		_llevada.position.y = -36.0 - (1.0 if int(Time.get_ticks_msec() / 250) % 2 == 0 else 0.0)
		if not _encuentro_hecho and _puerta_casa and _maisha.global_position.distance_to(_puerta_casa.global_position) < 44.0:
			_encuentro()
	# una pista si Kuku se escapa una y otra vez
	if is_instance_valid(_kuku) and _kuku.get("_huidas") >= 2 and _avisos_kuku == 0:
		_avisos_kuku = 1
		var dialogo := get_tree().get_first_node_in_group("dialogo")
		if dialogo and not dialogo.hablando:
			CHARLA.hablar(self, "kitovu_kuku_huye")
	# cerca de la granja (lo único vivo del valle) se oye la brisa en la hierba; lejos, el viento entre árboles secos
	var cerca := clampf(1.0 - (_maisha.global_position - GRANJA).length() / 700.0, 0.0, 1.0)
	Sonido.volumen_ambiente("brisa", 0.15 + 0.5 * cerca)
	Sonido.volumen_ambiente("viento", 0.6 - 0.35 * cerca)
	# sin cetro (o con manchas sin limpiar, en la arena) Maisha no se atreve a entrar
	for z in _practicas + ([_arena] if _arena else []):
		if not z.activa and z.estado != 4 and z.en_borde(_maisha.global_position):
			var fuera: Vector2 = (_maisha.global_position - z.global_position).normalized()
			_maisha.global_position += fuera * 90.0 * delta + fuera
			if _empujada <= 0.0:
				_empujada = 6.0
				var dialogo := get_tree().get_first_node_in_group("dialogo")
				if dialogo and not dialogo.hablando:
					CHARLA.hablar(self, "kitovu_arena_dormida" if z == _arena else "kitovu_mancha_sin_cetro")
	_comprobar_leccion_golpe()
	_comprobar_leccion_latido()
	# durante la pelea, el narrador explica el Corazón y el Aliento cuando hace falta
	if _pelea and _pelea != _arena and _pelea.estado == 2:
		var enemigos := get_tree().get_nodes_in_group("enemigos").size()
		if _enemigos_antes >= 0 and enemigos < _enemigos_antes and not Estado.tiene("narr/nucleo"):
			_leccion_semilla()
		_enemigos_antes = enemigos
		if _maisha.aliento < 60.0 and Estado.tiene("narr/zona2"):
			_narrar("narrador_aliento", "narr/aliento", 0.2)


# --- Lecciones (el mundo se para hasta que se pulsa la tecla) ------------------------------------------

const LECCION := preload("res://scripts/interfaz/leccion.gd")
var _leccion: CanvasLayer
var _ensenando := false


func _leccion_lista() -> CanvasLayer:
	if _leccion == null:
		_leccion = LECCION.new()
		add_child(_leccion)
	return _leccion


## El cetro: la primera vez que Maisha llega junto al espantapájaros con el cetro
func _comprobar_leccion_golpe() -> void:
	if _ensenando or not Estado.tiene("cetro_recibido") or Estado.tiene("leccion/golpe"):
		return
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if dialogo and dialogo.hablando:
		return
	for e in get_tree().get_nodes_in_group("espantapajaros"):
		if (e as Node2D).global_position.distance_to(_maisha.global_position) < 34.0:
			_ensenando = true
			Estado.marcar("leccion/golpe")
			await _leccion_lista().ensenar("golpe", "J", "Pulsa J para golpear con el cetro", [_maisha, e])
			_maisha.call("mirar", (e as Node2D).global_position - _maisha.global_position)
			_maisha.call("golpear")
			_ensenando = false
			return


## Las semillas: en la primera mancha, cuando cae el primer Petrino, el narrador presenta el Corazón de Giza
func _leccion_semilla() -> void:
	if _ensenando:
		return
	_ensenando = true
	await _narrar("narrador_nucleo", "narr/nucleo", 0.4)
	var nucleo: Node2D = _pelea.get("_nucleo") if _pelea else null
	Estado.marcar("leccion/semilla")
	await _leccion_lista().ensenar("explosivo", "K", "Pulsa K para plantar una semilla junto al Corazón", [_maisha, nucleo])
	if _maisha.call("lanzar_semilla"):
		var semilla := get_tree().get_nodes_in_group("semillas").back() as Node2D
		var casilla := Vector2i((semilla.global_position / 16.0).floor()) if semilla else Vector2i.ZERO
		# a cámara lenta hasta que Maisha sale de la cruz (o estalla)
		await _leccion_lista().camara_lenta("¡Sal de la cruz!", func() -> bool:
			if not is_instance_valid(semilla) or not semilla.is_inside_tree():
				return false
			var c := Vector2i((_maisha.global_position / 16.0).floor())
			return (c.x == casilla.x and absi(c.y - casilla.y) <= 2) or (c.y == casilla.y and absi(c.x - casilla.x) <= 2))
	_ensenando = false


## El Latido: en la segunda mancha, la primera vez que un Petrino se le echa encima a Maisha
func _comprobar_leccion_latido() -> void:
	if _ensenando or Estado.tiene("leccion/latido") or not Estado.tiene("narr/zona2") or _pelea == null or _pelea == _arena:
		return
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if dialogo and dialogo.hablando:
		return
	for e in get_tree().get_nodes_in_group("enemigos"):
		if (e as Node2D).global_position.distance_to(_maisha.global_position) < 30.0:
			_ensenando = true
			Estado.marcar("leccion/latido")
			_maisha.set("aliento", maxf(float(_maisha.get("aliento")), 60.0))
			await _leccion_lista().ensenar("latido", "L", "Pulsa L: el Latido aparta a los Petrinos", [_maisha, e])
			_maisha.call("latido")
			_ensenando = false
			return

