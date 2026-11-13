extends "res://scripts/mundo/escena_mundo.gd"
## LA SECCIÓN PROHIBIDA (Sigilia, el final): las salas de mármol morado bajo el Gran Archivo de Maandiko. Se baja
## cuando el Índice tiene sus doce nombres (sigilia/indice.gd).
##   - LA ESCALERA DE LOS 12 NOMBRES: los doce ATRILES encendidos; MAUTI y KALAMU bajan con Maisha y esperan aquí.
##   - EL CLAUSTRO DEL TRIPLE SELLO: tres PEDESTALES (sigilia/pedestal.gd: fuego, hielo y rayo), dormidos hasta que
##     se enciendan los dos SELLOS de las cámaras. Luego, cada uno con su sigilo: con los tres se abre el TRIPLE SELLO.
##   - LA CÁMARA DEL SELLO DE FUEGO Y HIELO (oeste): tras un FOSO de tinta que corre hacia el sur (placas de hielo);
##     su sello (un pedestal de fuego), en un rincón tapado por Tinta Quieta.
##   - LA CÁMARA DEL SELLO DE HIELO Y RAYO (este): tras una sima (un Puente de Constelación, con sus dos bobinas);
##     su sello (un pedestal de rayo), en la isleta de un estanque de tinta.
##   - LAS SOMBRAS DE RENGLÓN (enemigos/sombra_renglon.gd), por el Claustro y las cámaras.
##   - LA ROTONDA DEL PRIMER NOMBRE: EL GRIMORIO DE TINTA (enemigos/grimorio_tinta.gd) y sus tres pedestales.
##     Vencido: entran Mauti y Kalamu, el Grimorio vuelve a ser el Índice Vivo y entrega la PLUMA DEL PRIMER NOMBRE
##     («sigilia_libre»), y sale el final de Sigilia (arte/historia/24_sigilia_libre.png).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const INDICE := preload("res://scripts/mundo/sigilia/indice.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const BOBINA := preload("res://scripts/mundo/sigilia/bobina.gd")
const PUENTE := preload("res://scripts/mundo/sigilia/puente_constelacion.gd")
const PEDESTAL := preload("res://scripts/mundo/sigilia/pedestal.gd")
const SOMBRA := preload("res://scripts/enemigos/sombra_renglon.gd")
const GRIMORIO := preload("res://scripts/enemigos/grimorio_tinta.gd")
const FIN := preload("res://scripts/interfaz/fin_mundo.gd")
const ARTE := "res://arte/mundos/sigilia/seccion/"
## (todo en casillas)
const MAUTI := Vector2i(26, 62)
const KALAMU := Vector2i(37, 62)
const FOSO := Rect2i(15, 38, 3, 12)
const CHARCO_OESTE := Vector2i(7, 35)
const SELLO_OESTE := Vector2i(7, 31)
const SELLO_ESTE := Vector2i(56, 44)
const PUENTE_ESTE := Rect2i(44, 43, 6, 3)
const BOBINAS := [Vector2i(41, 40), Vector2i(41, 48)]
const PEDESTALES := {"fuego": Vector2i(24, 39), "hielo": Vector2i(29, 39), "rayo": Vector2i(34, 39)}
const TRIPLE_SELLO := Vector2i(30, 34)
const SOMBRAS := [Vector2i(24, 46), Vector2i(39, 46), Vector2i(8, 44), Vector2i(51, 38)]
## la Rotonda: su centro (px), sus semiejes (px) y sus pedestales
const ROTONDA := Vector2(512, 296)
const RADIOS := Vector2(248, 184)
const PEDESTALES_ROTONDA := {"fuego": Vector2i(21, 18), "hielo": Vector2i(42, 18), "rayo": Vector2i(31, 8)}
const ENTRADA_ROTONDA := Vector2i(31, 28)

var _grimorio: Node2D = null
var _despertando := false
var _sello: StaticBody2D
var _sello_sprite: Sprite2D
var _del_claustro: Array = []


func _ready() -> void:
	super()
	Estado.marcar("seccion_prohibida")
	_poner_cosas()
	_maisha.caida.connect(_al_caer)
	if Estado.tiene("grimorio_vencido") and not Estado.tiene("sigilia_libre"):
		_cierre.call_deferred()            # (se salió a medias del final: se retoma)
	elif not Estado.tiene("seccion_llegada"):
		_pensar_al_llegar.call_deferred()


## El foso del oeste corre hacia el sur; los estanques están quietos (lo preguntan las placas de hielo)
func corriente_en(p: Vector2) -> Vector2:
	return Vector2.DOWN if FOSO.has_point(Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))) else Vector2.ZERO


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	# los doce atriles, encendidos, a los dos lados de la Escalera
	for i in 12:
		var atril := Sprite2D.new()
		atril.texture = load(ARTE + "atril.png")
		atril.hframes = 2
		atril.frame = 1
		atril.offset = Vector2(0, -13)
		atril.position = Vector2((21.5 if i < 6 else 42.5) * 16.0, (60.0 + (i % 6) * 1.5) * 16.0)
		$Entidades.add_child(atril)
	for v in [["mauti", MAUTI], ["kalamu", KALAMU]]:
		$Entidades.add_child(_vecino(v[0], _sitio(v[1])))
	# la cámara del oeste: el tapón de Tinta Quieta y su sello
	var charco: StaticBody2D = CHARCO.new()
	charco.marca = "charco/seccion/%d,%d" % [CHARCO_OESTE.x, CHARCO_OESTE.y]
	charco.position = _sitio(CHARCO_OESTE)
	$Entidades.add_child(charco)
	_poner_pedestal("fuego", SELLO_OESTE, "seccion/sello_oeste", false).activado.connect(_al_encender_sello)
	# la cámara del este: el puente con sus bobinas y su sello
	var puente: Node2D = PUENTE.new()
	puente.casillas = PUENTE_ESTE
	puente.marca = "seccion/puente_este"
	for b in BOBINAS:
		var bobina: StaticBody2D = BOBINA.new()
		bobina.position = _sitio(b)
		$Entidades.add_child(bobina)
		puente.bobinas.append(bobina)
	add_child(puente)
	_poner_pedestal("rayo", SELLO_ESTE, "seccion/sello_este", false).activado.connect(_al_encender_sello)
	# el Claustro: los tres pedestales (dormidos hasta que estén los dos sellos) y el Triple Sello
	for tipo in PEDESTALES:
		var p := _poner_pedestal(tipo, PEDESTALES[tipo], "seccion/pedestal_" + tipo, not _sellos_encendidos())
		p.activado.connect(_al_activar_del_claustro)
		_del_claustro.append(p)
	_sello = StaticBody2D.new()
	_sello.position = Vector2(TRIPLE_SELLO) * 16.0 + Vector2(32, 30)
	_sello_sprite = Sprite2D.new()
	_sello_sprite.texture = load(ARTE + "sello.png")
	_sello_sprite.hframes = 2
	_sello_sprite.offset = Vector2(0, -22)
	_sello.add_child(_sello_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(64, 10)
	forma.shape = caja
	forma.position = Vector2(0, -5)
	_sello.add_child(forma)
	$Entidades.add_child(_sello)
	if Estado.tiene("seccion/triple_sello"):
		_abrir_sello(false)
	for s in SOMBRAS:
		var sombra: Node2D = SOMBRA.new()
		sombra.position = _sitio(s)
		$Entidades.add_child(sombra)
	# la Rotonda: sus pedestales (se apagan solos) y el Grimorio
	for tipo in PEDESTALES_ROTONDA:
		_poner_pedestal(tipo, PEDESTALES_ROTONDA[tipo], "", false).add_to_group("pedestales_rotonda")
	if not Estado.tiene("grimorio_vencido"):
		_grimorio = GRIMORIO.new()
		_grimorio.centro = ROTONDA
		_grimorio.radios = RADIOS
		_grimorio.position = ROTONDA + Vector2(0, -16)
		$Entidades.add_child(_grimorio)
		_grimorio.destruido.connect(_al_vencer_grimorio)


func _vecino(id: String, donde: Vector2) -> StaticBody2D:
	var n: StaticBody2D = VECINO.new()
	n.id = id
	n.charla = id + "_seccion"
	n.position = donde
	return n


func _poner_pedestal(tipo: String, casilla: Vector2i, marca: String, dormido: bool) -> StaticBody2D:
	var p: StaticBody2D = PEDESTAL.new()
	p.tipo = tipo
	p.marca = marca
	p.dormido = dormido
	p.position = _sitio(casilla)
	$Entidades.add_child(p)
	return p


func _sellos_encendidos() -> bool:
	return Estado.tiene("seccion/sello_oeste") and Estado.tiene("seccion/sello_este")


## Un sello de cámara se enciende: con los dos, despiertan los tres pedestales del Claustro
func _al_encender_sello(_tipo: String) -> void:
	if not _sellos_encendidos():
		_hud.mostrar_mensaje("Un sello se enciende. Queda el de la otra cámara")
		return
	for p in _del_claustro:
		p.despertar()
	_hud.mostrar_mensaje("Los pedestales del Claustro han despertado")


## Un pedestal del Claustro se enciende: con los tres, se abre el Triple Sello
func _al_activar_del_claustro(_tipo: String) -> void:
	for p in _del_claustro:
		if not p.encendido:
			return
	if not Estado.tiene("seccion/triple_sello"):
		Estado.marcar("seccion/triple_sello")
		_abrir_sello(true)


func _abrir_sello(ahora: bool) -> void:
	_sello_sprite.frame = 1
	_sello.get_child(1).set_deferred("disabled", true)
	if ahora:
		Sonido.efecto("rueda_abrir", 0.0, _sello.global_position)
		Sonido.efecto("arte_sube", -4.0, _sello.global_position)
		Impacto.temblar(2.5, 0.4)
		_hud.mostrar_mensaje("El Triple Sello se abre")


## Al entrar en la Rotonda, despierta el Grimorio. Mientras pelean, la cámara se va hacia la mitad entre los dos.
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_grimorio) and not Estado.tiene("grimorio_vencido"):
		hacia = ((_grimorio.global_position + Vector2(0, -30) - maisha.global_position) * 0.5).clamp(Vector2(-160, -90), Vector2(160, 90))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_grimorio) or Estado.tiene("grimorio_vencido"):
		return
	if ((maisha.global_position - ROTONDA) / RADIOS).length() < 0.85:
		_despertando = true
		if not Estado.tiene("grimorio_visto"):
			Estado.marcar("grimorio_visto")
			await CHARLA_SCRIPT.hablar(self, "grimorio_encuentro")
		if is_instance_valid(_grimorio):
			_grimorio.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO


## Si cae, vuelve a la entrada de la Rotonda (si ya pelea) o a la Escalera
func _al_caer() -> void:
	var punto := _sitio(ENTRADA_ROTONDA) if _despertando and not Estado.tiene("grimorio_vencido") else _entrada
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_vencer_grimorio() -> void:
	await get_tree().create_timer(1.6).timeout
	if is_inside_tree():
		_cierre()


## El final de Sigilia: Mauti y Kalamu entran, el Grimorio vuelve a ser el Índice Vivo y entrega la Pluma
func _cierre() -> void:
	Impacto.fogonazo(Color(1.0, 0.9, 0.6), 0.6, 0.8)
	Sonido.efecto("arte_sube", 0.0, ROTONDA)
	Sonido.musica("seccion_prohibida", 1.5)
	var base := ROTONDA + Vector2(0, 70)
	if _maisha.global_position.distance_to(base) > 120.0:
		_maisha.global_position = base
	$Entidades.add_child(_vecino("kalamu", base + Vector2(-34, 22)))
	$Entidades.add_child(_vecino("mauti", base + Vector2(34, 22)))
	await get_tree().create_timer(1.2).timeout
	if not is_inside_tree():
		return
	for charla in ["sigilia_final_kalamu", "sigilia_final_indice", "sigilia_final_mauti"]:
		await CHARLA_SCRIPT.hablar(self, charla)
	if not Estado.tiene("sigilia_libre"):
		Estado.dar("pluma_primer_nombre")
		Estado.marcar("sigilia_libre")
	Estado.guardar_pronto()
	_mostrar_fin()


func _mostrar_fin() -> void:
	if Estado.tiene("fin_sigilia_visto"):
		return
	Estado.marcar("fin_sigilia_visto")
	var fin: CanvasLayer = FIN.new()
	fin.ilustracion = load("res://arte/historia/24_sigilia_libre.png")
	fin.titulo = "Sigilia recuerda"
	fin.subtitulo = "Fin del segundo mundo"
	fin.pie = "Continuará en Asterhaul..."
	fin.musica = "maandiko"
	var misiones := Misiones.hechas().size()
	fin.lineas_propias = [
		["Tiempo de juego", -1, -1, Estado.texto_tiempo(Estado.tiempo_jugado)],
		["Nombres devueltos al Índice", INDICE.cuantos(), INDICE.NOMBRES.size(), ""],
		["Sigilos aprendidos", ["sigilo_fuego", "sigilo_hielo", "sigilo_rayo"].filter(func(s: String) -> bool: return Estado.tiene(s)).size(), 3, ""],
		["Misiones cumplidas", misiones, misiones + Misiones.activas().size(), ""],
		["Esencia", Artes.esencia_ganada_total(), -1, ""],
		["Cristales del Nexo", Tienda.cristales_ganados_total(), -1, ""],
	]
	add_child(fin)
	fin.abrir()


## (la pantalla del final pone otra música: al cerrarla vuelve la de aquí)
func volver_a_su_musica() -> void:
	Sonido.musica("seccion_prohibida")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("seccion_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "seccion_llegada")
	Estado.marcar("seccion_llegada")
