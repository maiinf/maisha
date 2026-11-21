extends "res://scripts/mundo/escena_mundo.gd"
## EL HORIZONTE INMÓVIL (el Valle del Ocaso, el final del juego). Se entra por la Puerta del Horizonte de Jioni.
##   - LA LLEGADA: Mauti espera. En el PEDESTAL (ocaso/pedestal_pesas.gd) se encajan las tres pesas y un puente de
##     cristal (ocaso/puente_vidrio.gd) baja a la pasarela.
##   - LA PASARELA DE LOS TRES PESOS: un repaso de todo el valle. Tres PILARES DORADOS (ocaso/pilar_dorado.gd):
##       oeste: la sombra de una Vela de Sombra tiene que cubrir su pie (vela de cara y sol al oeste);
##       centro: dos espejos de bronce encendidos (el primero mirando al sol, el segundo al primero);
##       este: la sombra de un obelisco (sol al este).
##     Con los tres, otro puente de cristal baja al altar.
##   - EL ALTAR DEL SOL ENCADENADO: JUA-GIZA (enemigos/jua_giza.gd), dos obeliscos, el contrapeso del oeste, dos
##     espejos altos, el candado del sur y un Reloj. Al soltar las tres cadenas llega Mauti, calman juntos al sol con
##     el Cetro del Nexo y llega la PRIMERA NOCHE («ocaso_libre»): el final.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const SOL := preload("res://scripts/mundo/ocaso/sol.gd")
const RELOJ := preload("res://scripts/mundo/ocaso/reloj_sol.gd")
const VELA := preload("res://scripts/mundo/ocaso/vela_sombra.gd")
const ESPEJO := preload("res://scripts/mundo/ocaso/espejo.gd")
const ESPEJO_ALTO := preload("res://scripts/mundo/ocaso/espejo_alto.gd")
const PUENTE := preload("res://scripts/mundo/ocaso/puente_vidrio.gd")
const PEDESTAL := preload("res://scripts/mundo/ocaso/pedestal_pesas.gd")
const PILAR := preload("res://scripts/mundo/ocaso/pilar_dorado.gd")
const CONTRAPESO := preload("res://scripts/mundo/ocaso/contrapeso.gd")
const CANDADO := preload("res://scripts/mundo/ocaso/candado_sur.gd")
const JEFE := preload("res://scripts/enemigos/jua_giza.gd")
const FIN := preload("res://scripts/interfaz/fin_mundo.gd")
const ARTE_MIRADOR := "res://arte/mundos/ocaso/mirador/"
## (todo en casillas)
const PEDESTAL_EN := Vector2i(32, 7)
const MAUTI := Vector2i(36, 5)
const PUENTE_PESAS := Rect2i(31, 10, 4, 4)
const PUENTE_ALTAR := Rect2i(31, 23, 4, 5)
const VELA_EN := [Vector2i(14, 17), 6]
const OBELISCOS := [[Vector2i(51, 17), 6], [Vector2i(24, 40), 4], [Vector2i(41, 40), 4]]
const ESPEJOS := [[Vector2i(27, 19), 0, "horizonte_a"], [Vector2i(38, 19), 0, "horizonte_b"]]
## pilar: [casilla, marca]
const PILARES := [[Vector2i(18, 17), "horizonte/pilar_oeste"], [Vector2i(33, 16), "horizonte/pilar_centro"], [Vector2i(47, 17), "horizonte/pilar_este"]]
const RELOJES := [Vector2i(12, 20), Vector2i(53, 20), Vector2i(36, 52)]
const CONTRAPESO_EN := Vector2i(19, 40)
const ESPEJOS_ALTOS := [Vector2i(23, 49), Vector2i(42, 49)]
const CANDADO_EN := Vector2i(30, 52)
const ALTAR := Vector2(32.5, 41.5)
const ALTAR_RADIOS := Vector2(15.5, 12.5)
const SOL_EN := Vector2(32.5 * 16, 40 * 16 + 8)

var sol: Node2D
var jua: Node2D = null
var _puente_pesas: Node2D
var _puente_altar: Node2D
var _espejos: Array = []
var _vela: StaticBody2D
var _despertando := false


func _ready() -> void:
	_vela = VELA.new()
	_vela.de_canto = true
	_vela.marca = "horizonte_vela"
	if Estado.extra.get("velas", {}).has("horizonte_vela"):
		_vela.de_canto = bool(Estado.extra["velas"]["horizonte_vela"])
	sol = SOL.new()
	sol.name = "Sol"
	sol.obeliscos.append([VELA_EN[0], VELA_EN[1], _vela])
	for o in OBELISCOS:
		sol.obeliscos.append(o)
	add_child(sol)
	_puente_pesas = _puente(PUENTE_PESAS, "horizonte/puente_pesas")
	_puente_altar = _puente(PUENTE_ALTAR, "horizonte/puente_altar")
	super()
	Estado.marcar("horizonte_inmovil")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	add_child(vacio)
	_vela.position = _sitio(VELA_EN[0])
	$Entidades.add_child(_vela)
	_poner_cosas()
	if not Estado.tiene("horizonte_llegada"):
		_pensar_al_llegar.call_deferred()


func _puente(casillas: Rect2i, marca: String) -> Node2D:
	var p: Node2D = PUENTE.new()
	p.casillas = casillas
	p.marca = marca
	add_child(p)
	return p


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _adorno(dibujo: String, c: Vector2i, caja: Vector2) -> StaticBody2D:
	var cosa := StaticBody2D.new()
	cosa.position = _sitio(c)
	var sprite := Sprite2D.new()
	sprite.texture = load(dibujo)
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cosa.add_child(sprite)
	var forma := CollisionShape2D.new()
	var r := RectangleShape2D.new()
	r.size = caja
	forma.shape = r
	forma.position = Vector2(0, -caja.y / 2.0)
	cosa.add_child(forma)
	$Entidades.add_child(cosa)
	return cosa


func _poner_cosas() -> void:
	for o in OBELISCOS:
		_adorno(ARTE_MIRADOR + "obelisco.png", o[0], Vector2(12, 6)).add_to_group("obeliscos")
	for c in RELOJES:
		var reloj: StaticBody2D = RELOJ.new()
		reloj.position = _sitio(c)
		$Entidades.add_child(reloj)
	var pedestal: StaticBody2D = PEDESTAL.new()
	pedestal.marca = "horizonte/pesas"
	pedestal.position = _sitio(PEDESTAL_EN)
	$Entidades.add_child(pedestal)
	pedestal.puestas.connect(_al_poner_pesas)
	for e in ESPEJOS:
		var espejo: StaticBody2D = ESPEJO.new()
		espejo.lado = e[1]
		espejo.marca = e[2]
		espejo.position = _sitio(e[0])
		if _espejos.is_empty():
			espejo.mira_al_sol = true
		else:
			espejo.fuente = _espejos[0]
		_espejos.append(espejo)
		$Entidades.add_child(espejo)
	var pruebas := [
		func() -> bool: return sol.en_sombra(_sitio(PILARES[0][0])),
		func() -> bool: return _espejos.all(func(e: Node) -> bool: return e.encendido),
		func() -> bool: return sol.en_sombra(_sitio(PILARES[2][0])),
	]
	for i in PILARES.size():
		var pilar: StaticBody2D = PILAR.new()
		pilar.marca = PILARES[i][1]
		pilar.prueba = pruebas[i]
		pilar.position = _sitio(PILARES[i][0])
		$Entidades.add_child(pilar)
		pilar.encendido.connect(_al_encender_pilar)
	_leer("horizonte_pasarela", _sitio(Vector2i(33, 21)))
	if not Estado.tiene("ocaso_libre"):
		var mauti: StaticBody2D = VECINO.new()
		mauti.id = "mauti"
		mauti.charla = "mauti_horizonte"
		mauti.position = _sitio(MAUTI)
		$Entidades.add_child(mauti)
	var contrapeso: StaticBody2D = CONTRAPESO.new()
	contrapeso.position = _sitio(CONTRAPESO_EN)
	$Entidades.add_child(contrapeso)
	var candado: StaticBody2D = CANDADO.new()
	candado.position = _sitio(CANDADO_EN)
	$Entidades.add_child(candado)
	var altos: Array = []
	for c in ESPEJOS_ALTOS:
		var alto: StaticBody2D = ESPEJO_ALTO.new()
		alto.position = _sitio(c)
		alto.apunta = SOL_EN
		alto.dura = 6.0
		$Entidades.add_child(alto)
		altos.append(alto)
	if Estado.tiene("ocaso_libre"):
		contrapeso.romper()
		var calmo := Sprite2D.new()                       # (el sol, ya en calma)
		calmo.texture = JEFE.DIBUJO
		calmo.hframes = 6
		calmo.frame = 5
		calmo.offset = Vector2(0, -62)
		calmo.position = SOL_EN
		$Entidades.add_child(calmo)
		return
	jua = JEFE.new()
	jua.espejos = altos
	jua.contrapeso = contrapeso
	jua.candado = candado
	jua.position = SOL_EN
	$Entidades.add_child(jua)
	jua.calmado.connect(_al_calmar)


func _leer(charla: String, donde: Vector2) -> Node2D:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)
	return lectura


func _al_poner_pesas() -> void:
	_puente_pesas.fundir()
	Sonido.efecto("puente_funde", 0.0, Vector2(PUENTE_PESAS.get_center()) * 16.0)
	await CHARLA_SCRIPT.hablar(self, "horizonte_pesas")


func pilares() -> int:
	return PILARES.filter(func(p: Array) -> bool: return Estado.tiene(p[1])).size()


func _al_encender_pilar() -> void:
	_hud.mostrar_mensaje("Pilares dorados: %d de 3" % pilares())
	if pilares() == PILARES.size() and not _puente_altar.hecho():
		_puente_altar.fundir()
		Sonido.efecto("puente_funde", 0.0, Vector2(PUENTE_ALTAR.get_center()) * 16.0)
		Impacto.temblar(3.0, 0.5)
		await get_tree().create_timer(0.6).timeout
		if is_inside_tree():
			await CHARLA_SCRIPT.hablar(self, "horizonte_puente")


func en_altar(p: Vector2) -> bool:
	return ((p - ALTAR * 16.0) / (ALTAR_RADIOS * 16.0)).length() < 0.75


## Al entrar en el Altar, despierta Jua-Giza; mientras dura la pelea, la cámara enseña al sol y a Maisha a la vez
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var hacia := Vector2.ZERO
	if maisha and _despertando and is_instance_valid(jua) and jua.fase != jua.Fase.CALMA:
		hacia = ((SOL_EN + Vector2(0, -50) - maisha.global_position) * 0.5).clamp(Vector2(-140, -90), Vector2(140, 90))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(jua):
		return
	if maisha and en_altar(maisha.global_position):
		_despertando = true
		if not Estado.tiene("jua_visto"):
			Estado.marcar("jua_visto")
			await CHARLA_SCRIPT.hablar(self, "jua_encuentro")
		if is_instance_valid(jua):
			jua.despertar()


## Las tres cadenas sueltas: Mauti llega, calman al sol con el Cetro del Nexo y llega la Primera Noche
func _al_calmar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica("ocaso_libre" if ResourceLoader.exists("res://audio/musica/ocaso_libre.ogg") else "jioni", 1.5)
	var mauti: StaticBody2D = VECINO.new()
	mauti.id = "mauti"
	mauti.charla = "mauti_horizonte"
	mauti.position = SOL_EN + Vector2(40, 70)
	$Entidades.add_child(mauti)
	if _maisha.global_position.distance_to(SOL_EN) > 150.0:
		_maisha.global_position = SOL_EN + Vector2(-30, 70)
	for charla in ["horizonte_calma", "horizonte_mauti"]:
		await CHARLA_SCRIPT.hablar(self, charla)
	if not Estado.tiene("ocaso_libre"):
		Estado.marcar("ocaso_libre")
		Sonido.efecto("cetro_nexo", 2.0, _maisha.global_position)
		Impacto.fogonazo(Color(1.0, 0.85, 0.6), 0.8, 1.2)
	await CHARLA_SCRIPT.hablar(self, "horizonte_final")
	Estado.guardar_pronto()
	_mostrar_fin()


func _mostrar_fin() -> void:
	if Estado.tiene("fin_ocaso_visto"):
		return
	Estado.marcar("fin_ocaso_visto")
	var fin: CanvasLayer = FIN.new()
	fin.ilustracion = load("res://arte/historia/26_primera_noche.png")
	fin.titulo = "La Primera Noche"
	fin.subtitulo = "Fin del Valle del Ocaso · Fin de Maisha"
	fin.pie = "Gracias por jugar"
	fin.musica = "ocaso_libre" if ResourceLoader.exists("res://audio/musica/ocaso_libre.ogg") else "jioni"
	var misiones := Misiones.hechas().size()
	var faroles := preload("res://scripts/mundo/ocaso/poste_farol.gd").colgados()
	fin.lineas_propias = [
		["Tiempo de juego", -1, -1, Estado.texto_tiempo(Estado.tiempo_jugado)],
		["Faroles colgados", faroles, 12, ""],
		["Cadenas del sol sueltas", 3, 3, ""],
		["Misiones cumplidas", misiones, misiones + Misiones.activas().size(), ""],
		["Esencia", Artes.esencia_ganada_total(), -1, ""],
		["Cristales del Nexo", Tienda.cristales_ganados_total(), -1, ""],
	]
	add_child(fin)
	fin.abrir()


func volver_a_su_musica() -> void:
	if Estado.tiene("ocaso_libre") and ResourceLoader.exists("res://audio/musica/ocaso_libre.ogg"):
		Sonido.musica("ocaso_libre", 2.0)
	else:
		super()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("horizonte_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "horizonte_llegada")
	Estado.marcar("horizonte_llegada")
