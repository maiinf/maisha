extends Node
## SONIDO (autoload «Sonido»): la música, los ambientes y los efectos de todo el juego.
## Todo lo que suena lo crean herramientas/componer_musica.py y herramientas/crear_sonidos.py:
## es nuestro, no hay derechos de terceros.
##
##   Sonido.musica("kitovu")                       cambia la música con un fundido (si ya suena, no hace nada)
##   Sonido.musica("despertar", 2.0, "kitovu")     una pieza que no se repite y, al acabar, la siguiente
##   Sonido.fanfarria("purga")                     una pieza corta por encima (la música baja un momento)
##   Sonido.ambiente({"brisa": 1.0, "viento": 0.4})   ambientes en bucle (los que no se nombran se apagan)
##   Sonido.efecto("dialogo_pasar")                un efecto; con «donde» suena más flojo si está lejos
##
## Buses: Musica, Ambiente y Efectos (sus niveles se cambian en el menú de pausa y se guardan).

const MUSICA := "res://audio/musica/%s.ogg"
const EFECTOS := "res://audio/sonidos/%s.ogg"
const AMBIENTES := "res://audio/ambiente/%s.ogg"
const NO_SE_REPITEN := ["raiz_libre", "despertar", "purga", "victoria", "objeto", "tarea", "recuerdo", "noche", "amanece", "kitovu", "interior"]
## El título de cada pieza (los mismos que en herramientas/componer_musica.py)
const TITULOS := {
	"despertar": "Un largo letargo", "kitovu": "Raíces dormidas", "inicio": "El tema de Maisha",
	"prados": "Camino de los Prados", "aldea": "Cuna de Musgo", "interior": "Nana de la chimenea",
	"combate": "Manchas de Giza", "jefe": "Mzizi, la raíz del Arco", "purga": "Vuelve el color",
	"victoria": "El Arco despierta", "objeto": "¡Lo tengo!", "tarea": "Tarea cumplida",
	"recuerdo": "Un eco de antes", "noche": "Noche en la granja", "amanece": "Amanece",
	"bosque": "Hojas de cobre", "jefe_pembe": "Pembe, el ciervo de hierro",
	"cienaga": "Agua quieta", "jefe_konokono": "Konokono, la caracola de óxido",
	"campo": "Surcos de hierro", "jefe_cosechadora": "La Cosechadora Oxidada",
	"tienda": "El puesto de Tawi", "raiz_libre": "Raíz respira", "sendero": "El puente viejo", "pasarelas": "Entre juncos",
}
## Piezas tranquilas que no suenan sin parar: al acabar, un rato de silencio (solo ambiente) y vuelven
const CON_SILENCIO := {"kitovu": Vector2(25, 55), "interior": Vector2(15, 35)}
const AJUSTES := "user://ajustes.cfg"
const SILENCIO := -60.0
## Volumen de cada efecto (dB): para que ninguno tape a los demás
const VOLUMEN := {
	"dialogo_pasar": -6.0, "dialogo_cerrar": -8.0, "menu_mover": -10.0, "menu_aceptar": -6.0, "menu_atras": -7.0,
	"mochila_abrir": -5.0, "mochila_cerrar": -6.0, "pausa": -6.0,
	"cetro_golpe": -6.5, "golpe_acierto": -4.0, "clinc": -6.0, "semilla_plantar": -5.0, "semilla_mecha": -9.5,
	"explosion": -2.5, "brotes": -9.0, "latido": -3.0, "maisha_herida": -3.0, "maisha_cae": -3.0,
	"recoger": -5.0, "esencia": -4.0, "puerta": -6.0,
	"petrino_aparece": -4.0, "petrino_golpeado": -5.0, "petrino_muere": -4.0, "petrino_embiste": -7.0,
	"zona_aviso": -6.0, "espinas_suben": -3.0, "corazon_golpeado": -3.0, "corazon_roto": -2.5, "ola_purga": -6.0,
	"mzizi_rugido": -2.0, "mzizi_dolor": -2.0, "mzizi_aviso": -3.0, "mzizi_sale": -2.0, "mzizi_escupe": -4.0,
	"piedra_rompe": -6.0, "mzizi_vencido": -2.0, "temblor": -3.0, "portal_abre": -3.0,
	"pesca_lanzar": -5.0, "pesca_espera": -14.0, "pesca_pica": -3.0, "pesca_saca": -3.0, "pesca_escapa": -5.0,
	"zanahoria_arrancar": -4.0, "tablas_coger": -4.0, "cerca_martillo": -3.0, "cerca_arreglada": -6.0,
	"espantapajaros_golpe": -5.0, "seta_recoger": -5.0, "mineral_romper": -4.0, "entregar": -5.0,
	"construir": -3.0, "estatua_despierta": -3.0,
	"chispa": -9.0, "chispa_entra": -4.0, "gallina_cacareo": -5.0, "gallina_asustada": -5.0,
	"llamar_puerta": -3.0, "sopa": -8.0,
	"mision_nueva": -5.0, "mision_cumplida": -4.0, "mision_paso": -7.0, "rueda_abrir": -8.0, "meditar": -4.0, "arte_sube": -3.0,
	"pembe_bramido": -2.0, "pembe_escarba": -4.0, "pembe_galope": -3.0, "pembe_choque": -2.0, "pembe_dolor": -2.0,
	"pembe_vencido": -2.0, "jabali_grunido": -5.0,
	"konokono_despierta": -2.0, "konokono_rueda": -3.0, "konokono_escondida": -4.0, "konokono_traga": -3.0,
	"konokono_escupe": -5.0, "konokono_dolor": -3.0, "konokono_vencida": -2.0, "babosa_chof": -9.0, "sorber": -4.0,
	"cosechadora_arranca": -2.0, "cosechadora_tolva": -5.0, "cosechadora_tuerca": -5.0, "cosechadora_atascada": -2.0,
	"cosechadora_ira": -3.0, "cosechadora_embiste": -3.0, "cosechadora_choque": -2.0, "cosechadora_dolor": -2.0,
	"cosechadora_vencida": -2.0, "cosechadora_fuego": -3.0, "fuego_quema": -5.0, "comprar": -3.0, "cristal": -5.0, "eco_voz": -2.0, "pagina": -4.0, "libro_abrir": -3.0, "libro_cerrar": -3.0, "pluma": -8.0, "topo_excava": -4.0, "topo_sale": -2.0, "campanilla": -5.0, "cuervo_graznido": -4.0, "cuervo_picado": -3.0, "agua_baja": -3.0,
	"rana_croa": -6.0, "rana_salta": -7.0, "rana_cae": -4.0,
	"murcielago_chillido": -6.0, "murcielago_grito": -3.0, "onda_rebota": -5.0, "murcielago_mareo": -5.0,
	"murcielago_aleteo": -8.0, "bundi_ulula": -4.0, "bundi_conjura": -5.0, "bundi_lanza": -5.0, "bundi_esfuma": -6.0,
	"orbe_rebota": -3.0, "buibui_invoca": -4.0, "mende_corre": -10.0, "mende_muere": -6.0, "rango_nuevo": -3.0, "cencerro": -5.0, "escala_tramo": -5.0,
	"kambare_ruge": -2.0, "kambare_salta": -3.0, "kambare_cae": -2.0, "kambare_escupe": -4.0, "kambare_dolor": -2.0,
	"kambare_vencido": -2.0, "cangrejo_chasca": -6.0, "cangrejo_vuelca": -4.0,
	"guardian_brama": -2.0, "guardian_carga": -2.0, "mascara_cruje": -3.0, "mascara_rompe": -2.0,
	"raiz_ronca": -9.0, "raiz_despierta": -3.0, "raiz_azota": -2.0,
	"mamba_ruge": -2.0, "mamba_salta": -3.0, "mamba_muerde": -2.0, "mamba_dolor": -2.0, "mamba_coletazo": -3.0, "mamba_vencido": -2.0,
}
## Nivel de cada bus (0 a 10) y su volumen en dB con el nivel al máximo (la música, sutil)
const BUSES := {"Musica": -9.0, "Ambiente": -10.0, "Efectos": -3.0}
## Ajuste fino (dB) de las piezas musicales cuyo nivel medio se aparta de la referencia (-15,5 dBFS)
const VOLUMEN_MUSICA := {
	"raiz_libre": -3.0, "ruinas": -1.5, "pasarelas_viva": -1.5, "pasarelas": -1.0,
	"embarcadero_viva": -1.0, "gruta": -1.0, "jefe_pembe": -1.5, "jefe_konokono": -1.0, "jefe_kambare": -1.5,
	"bosque": 1.5, "bosque_gris": 2.0, "bosque_viva": 2.5,
	"cueva": 2.0, "surcos_gris": 2.0, "pasarelas_gris": 1.5,
	"lago": 2.0, "lago_gris": 1.5, "lago_viva": 2.0,
	"setas": 2.0, "jefe_kuvu": 1.5, "despertar": 1.5, "orilla_gris": 1.5, "orilla": 1.5,
	"canada": 1.5, "canada_gris": 1.5, "canada_viva": 1.5,
}

var musica_actual := ""
var niveles := {"Musica": 7, "Ambiente": 8, "Efectos": 8}
var conteo := {}                 # cuántas veces ha sonado cada cosa (lo usan las pruebas)

var _musica: Array[AudioStreamPlayer] = []
var _activa := 0
var _siguiente := ""
var _fanfarria: AudioStreamPlayer
var _ambientes := {}             # nombre -> AudioStreamPlayer
var _objetivo_ambiente := {}     # nombre -> volumen lineal deseado (0..1)
var _efectos: Array[AudioStreamPlayer] = []
var _cache := {}
var _ultimo := {}                # nombre -> fotograma en que sonó (no repetir el mismo efecto en el mismo fotograma)
var _tween_musica: Tween


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for bus in BUSES:
		if AudioServer.get_bus_index(bus) == -1:
			AudioServer.add_bus()
			var i := AudioServer.bus_count - 1
			AudioServer.set_bus_name(i, bus)
			AudioServer.set_bus_send(i, "Master")
	_cargar_ajustes()
	for i in 2:
		var m := AudioStreamPlayer.new()
		m.bus = "Musica"
		m.volume_db = SILENCIO
		m.finished.connect(_al_acabar_musica.bind(m))
		add_child(m)
		_musica.append(m)
	_fanfarria = AudioStreamPlayer.new()
	_fanfarria.bus = "Musica"
	_fanfarria.finished.connect(_al_acabar_fanfarria)
	add_child(_fanfarria)
	for i in 16:
		var e := AudioStreamPlayer.new()
		e.bus = "Efectos"
		add_child(e)
		_efectos.append(e)


# --- Música ---------------------------------------------------------------------

func _db_musica(nombre: String) -> float:
	return float(VOLUMEN_MUSICA.get(nombre, 0.0))


func musica(nombre: String, fundido := 1.5, siguiente := "") -> void:
	if nombre == musica_actual:
		if siguiente != "":
			_siguiente = siguiente
		return
	_contar("musica:" + nombre)
	musica_actual = nombre
	_siguiente = siguiente
	var vieja := _musica[_activa]
	_activa = 1 - _activa
	var nueva := _musica[_activa]
	if _tween_musica:
		_tween_musica.kill()
	_tween_musica = create_tween().set_parallel(true)
	if nombre == "":
		_tween_musica.tween_property(vieja, "volume_db", SILENCIO, fundido)
		_tween_musica.chain().tween_callback(vieja.stop)
		return
	var stream := _cargar(MUSICA % nombre)
	if stream == null:
		return
	if stream is AudioStreamOggVorbis:
		(stream as AudioStreamOggVorbis).loop = not nombre in NO_SE_REPITEN
	nueva.stream = stream
	nueva.volume_db = SILENCIO
	nueva.play()
	_tween_musica.tween_property(nueva, "volume_db", _db_musica(nombre), fundido).set_trans(Tween.TRANS_SINE)
	_tween_musica.tween_property(vieja, "volume_db", SILENCIO, fundido)
	_tween_musica.chain().tween_callback(vieja.stop)


func _al_acabar_musica(jugador: AudioStreamPlayer) -> void:
	if jugador != _musica[_activa]:
		return
	if _siguiente != "":
		var s := _siguiente
		_siguiente = ""
		musica_actual = ""
		musica(s, 2.0)
	elif CON_SILENCIO.has(musica_actual):
		# un rato de silencio (se oye el ambiente) y vuelve a sonar, si seguimos en el mismo sitio
		var cual := musica_actual
		var espera: Vector2 = CON_SILENCIO[cual]
		_contar("silencio:" + cual)
		await get_tree().create_timer(randf_range(espera.x, espera.y), true).timeout
		if musica_actual == cual and not jugador.playing:
			jugador.volume_db = SILENCIO
			jugador.play()
			create_tween().tween_property(jugador, "volume_db", _db_musica(cual), 3.0)


## Una pieza corta por encima de la música (purgar una zona, conseguir algo...): la música baja mientras suena
func fanfarria(nombre: String) -> void:
	var stream := _cargar(MUSICA % nombre)
	if stream == null:
		return
	_contar("fanfarria:" + nombre)
	# Maisha lo celebra (con los brazos en alto) cuando consigue algo importante
	if nombre in ["purga", "victoria", "objeto", "tarea"]:
		var maisha := get_tree().get_first_node_in_group("maisha")
		if maisha and maisha.has_method("celebrar"):
			maisha.celebrar()
	if stream is AudioStreamOggVorbis:
		(stream as AudioStreamOggVorbis).loop = false
	_fanfarria.stream = stream
	_fanfarria.play()
	var t := create_tween()
	t.tween_property(_musica[_activa], "volume_db", _db_musica(musica_actual) - 18.0, 0.3)


func _al_acabar_fanfarria() -> void:
	if musica_actual != "":
		create_tween().tween_property(_musica[_activa], "volume_db", _db_musica(musica_actual), 1.5)


# --- Ambiente -------------------------------------------------------------------

## Los ambientes que deben sonar y a qué volumen (0..1); los demás se apagan poco a poco
func ambiente(volumenes: Dictionary) -> void:
	_objetivo_ambiente = volumenes.duplicate()
	for nombre in volumenes:
		if not _ambientes.has(nombre):
			var stream := _cargar(AMBIENTES % nombre)
			if stream == null:
				continue
			if stream is AudioStreamOggVorbis:
				(stream as AudioStreamOggVorbis).loop = true
			var a := AudioStreamPlayer.new()
			a.bus = "Ambiente"
			a.stream = stream
			a.volume_db = SILENCIO
			add_child(a)
			a.play(randf() * 8.0)
			_ambientes[nombre] = a


## Cambia el volumen de un ambiente que ya suena (p. ej. más pájaros cerca de la granja)
func volumen_ambiente(nombre: String, lineal: float) -> void:
	if _objetivo_ambiente.has(nombre):
		_objetivo_ambiente[nombre] = lineal


func _process(delta: float) -> void:
	for nombre in _ambientes.keys():
		var a: AudioStreamPlayer = _ambientes[nombre]
		var objetivo: float = linear_to_db(maxf(0.001, float(_objetivo_ambiente.get(nombre, 0.0))))
		a.volume_db = move_toward(a.volume_db, maxf(SILENCIO, objetivo), delta * 20.0)
		if not _objetivo_ambiente.has(nombre) and a.volume_db <= SILENCIO + 0.1:
			a.queue_free()
			_ambientes.erase(nombre)


# --- Efectos --------------------------------------------------------------------

## Un efecto de sonido. «donde»: posición en el mundo (si está lejos de la cámara, suena más flojo o no suena)
func efecto(nombre: String, volumen_db := 0.0, donde: Variant = null, variar := 0.05) -> void:
	if _ultimo.get(nombre, -1) == Engine.get_process_frames():
		return
	var vol: float = float(VOLUMEN.get(nombre, -4.0)) + volumen_db
	if donde is Vector2:
		var camara := get_viewport().get_camera_2d()
		if camara:
			var lejos: float = (donde as Vector2).distance_to(camara.get_screen_center_position())
			if lejos > 520.0:
				return
			vol -= maxf(0.0, lejos - 160.0) / 30.0
	var stream := _cargar(EFECTOS % nombre)
	if stream == null:
		return
	_ultimo[nombre] = Engine.get_process_frames()
	_contar(nombre)
	var jugador: AudioStreamPlayer = null
	for e in _efectos:
		if not e.playing:
			jugador = e
			break
	if jugador == null:
		jugador = _efectos[0]
		_efectos.push_back(_efectos.pop_front())
	jugador.stream = stream
	jugador.volume_db = vol
	jugador.pitch_scale = 1.0 + randf_range(-variar, variar)
	jugador.play()


# --- Niveles (menú de pausa) -----------------------------------------------------

func poner_nivel(bus: String, nivel: int) -> void:
	niveles[bus] = clampi(nivel, 0, 10)
	_aplicar_nivel(bus)
	_guardar_ajustes()


func _aplicar_nivel(bus: String) -> void:
	var i := AudioServer.get_bus_index(bus)
	if i == -1:
		return
	var nivel: int = niveles[bus]
	AudioServer.set_bus_mute(i, nivel == 0)
	# de 10 a 1: del volumen base a 27 dB menos (el oído lo nota más o menos parejo)
	AudioServer.set_bus_volume_db(i, BUSES[bus] - (10 - nivel) * 3.0)


func _cargar_ajustes() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(AJUSTES) == OK:
		for bus in niveles:
			niveles[bus] = clampi(int(cfg.get_value("sonido", bus, niveles[bus])), 0, 10)
	for bus in niveles:
		_aplicar_nivel(bus)


func _guardar_ajustes() -> void:
	var cfg := ConfigFile.new()
	cfg.load(AJUSTES)              # para no borrar los demás ajustes (los temblores, por ejemplo)
	for bus in niveles:
		cfg.set_value("sonido", bus, niveles[bus])
	cfg.save(AJUSTES)


## Calla todo (antes de cerrar el juego, para que el audio suelte lo que está sonando)
func callar() -> void:
	for j in _musica + _efectos + [_fanfarria]:
		j.stop()
		j.stream = null
	for a in _ambientes.values():
		a.queue_free()
	_ambientes.clear()
	musica_actual = ""
	await get_tree().create_timer(0.15, true, false, true).timeout


func _exit_tree() -> void:
	# al cerrar el juego: soltar los sonidos cargados
	for j in _musica + _efectos + [_fanfarria]:
		j.stop()
		j.stream = null
	for a in _ambientes.values():
		a.stop()
		a.stream = null
	_cache.clear()


func _cargar(ruta: String) -> AudioStream:
	if _cache.has(ruta):
		return _cache[ruta]
	if not ResourceLoader.exists(ruta):
		push_warning("Sonido: no existe %s" % ruta)
		return null
	var s: AudioStream = load(ruta)
	_cache[ruta] = s
	return s


func _contar(clave: String) -> void:
	conteo[clave] = int(conteo.get(clave, 0)) + 1
