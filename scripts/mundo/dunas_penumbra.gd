extends "res://scripts/mundo/escena_mundo.gd"
## LAS DUNAS DE PENUMBRA (el Valle del Ocaso, el camino del oeste de Jioni). Mesetas de roca entre ARENAS MOVEDIZAS
## (asterhaul/vacio.gd con `hundir`: quien las pisa se hunde, pierde 1 hoja y vuelve). Se cruzan por las sombras
## largas de las VELAS DE SOMBRA (ocaso/vela_sombra.gd): un golpe las gira, y solo echan sombra si el sol les da en
## la tela (ocaso/sol.gd). El sol se gira con los Relojes de Sol, como en el Mirador.
##   - DESDE JIONI (este): un Reloj y la primera Vela; con el sol al este, su sombra cruza a la Meseta.
##   - LA MESETA DE LAS VELAS (centro): otro Reloj, dos Kivuli excavadores y la Vela del norte (de cara: hay que
##     ponerla de canto y el sol al sur para subir al OASIS SECRETO, con un Farol de la Hora).
##   - EL CAÑÓN DE LOS ESPEJOS (sur): su Vela (de canto) sube a la Meseta con el sol al sur. Dos ESPEJOS
##     SEMIENTERRADOS (ocaso/espejo_enterrado.gd): la Carga los saca; el primero mira al sol, el segundo al primero.
##     Con los dos encendidos, el rayo funde la arena entre la Meseta y el Cráter en un PUENTE DE CRISTAL. Un farol.
##   - EL CRÁTER DEL ALACRÁN (oeste): KIVULI (enemigos/kivuli_jefe.gd), tres obeliscos y tres Relojes de Sol.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const SOL := preload("res://scripts/mundo/ocaso/sol.gd")
const RELOJ := preload("res://scripts/mundo/ocaso/reloj_sol.gd")
const VELA := preload("res://scripts/mundo/ocaso/vela_sombra.gd")
const ESPEJO := preload("res://scripts/mundo/ocaso/espejo_enterrado.gd")
const PUENTE := preload("res://scripts/mundo/ocaso/puente_vidrio.gd")
const KIVULI := preload("res://scripts/enemigos/kivuli.gd")
const JEFE := preload("res://scripts/enemigos/kivuli_jefe.gd")
const ARTE_MIRADOR := "res://arte/mundos/ocaso/mirador/"
## (todo en casillas) vela: [su pie, el largo de su sombra, ¿empieza de canto?, marca]
const VELAS := [[Vector2i(60, 27), 13, false, "dunas_1"], [Vector2i(38, 18), 8, false, "dunas_2"], [Vector2i(39, 43), 7, true, "dunas_3"]]
const OBELISCOS := [[Vector2i(8, 23), 5], [Vector2i(19, 23), 5], [Vector2i(13, 33), 5]]
const RELOJES := [Vector2i(66, 24), Vector2i(42, 22), Vector2i(13, 20), Vector2i(5, 29), Vector2i(22, 29)]
## espejo: [casilla, hacia dónde mira al principio, marca]
const ESPEJOS := [[Vector2i(32, 47), 0, "dunas_a"], [Vector2i(46, 47), 2, "dunas_b"]]
const PUENTE_CASILLAS := Rect2i(26, 26, 4, 3)
const FAROLES := [[Vector2i(38, 5), "farol/dunas_1"], [Vector2i(39, 49), "farol/dunas_2"]]
const EXCAVADORES := [Vector2i(34, 24), Vector2i(43, 31)]
const MESETA := Rect2i(30, 18, 17, 19)
const CRATER := Vector2(13.5, 27.5)
const CRATER_RADIOS := Vector2(11.5, 9.5)
## dónde da el sol de lleno con cada hora (en casillas): al oeste, el Cráter y media Meseta; al sur, el Cañón; al
## este, la otra media Meseta y la entrada
const LUZ := {0: Rect2i(0, 0, 38, 54), 1: Rect2i(0, 37, 74, 17), 2: Rect2i(38, 0, 36, 54)}

var sol: Node2D
var puente: Node2D
var kivuli: Node2D = null
var _espejos: Array = []
var _despertando := false


func _ready() -> void:
	var velas: Array = []
	for v in VELAS:
		var vela: StaticBody2D = VELA.new()
		vela.de_canto = v[2]
		vela.marca = v[3]
		if v[3] != "" and Estado.extra.get("velas", {}).has(v[3]):
			vela.de_canto = bool(Estado.extra["velas"][v[3]])
		velas.append(vela)
	sol = SOL.new()
	sol.name = "Sol"
	for i in VELAS.size():
		sol.obeliscos.append([VELAS[i][0], VELAS[i][1], velas[i]])
	for o in OBELISCOS:
		sol.obeliscos.append(o)
	for h in LUZ:
		var r: Rect2i = LUZ[h]
		sol.luz[h] = Rect2(Vector2(r.position) * 16.0, Vector2(r.size) * 16.0)
	add_child(sol)
	puente = PUENTE.new()
	puente.name = "Puente"
	puente.casillas = PUENTE_CASILLAS
	puente.marca = "dunas/puente_cristal"
	add_child(puente)
	super()
	Estado.marcar("dunas_penumbra")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	vacio.hundir = true
	add_child(vacio)
	for i in VELAS.size():
		velas[i].position = _sitio(VELAS[i][0])
		$Entidades.add_child(velas[i])
	_poner_cosas()
	if not Estado.tiene("dunas_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	for o in OBELISCOS:
		var ob := StaticBody2D.new()
		ob.position = _sitio(o[0])
		var sprite := Sprite2D.new()
		sprite.texture = load(ARTE_MIRADOR + "obelisco.png")
		sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
		ob.add_child(sprite)
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(12, 6)
		forma.shape = caja
		forma.position = Vector2(0, -3)
		ob.add_child(forma)
		ob.add_to_group("obeliscos")
		$Entidades.add_child(ob)
	for r in RELOJES:
		var reloj: StaticBody2D = RELOJ.new()
		reloj.position = _sitio(r)
		$Entidades.add_child(reloj)
	for e in ESPEJOS:
		var espejo: StaticBody2D = ESPEJO.new()
		espejo.lado = e[1]
		espejo.marca = e[2]
		espejo.marca_fuera = "dunas/fuera_" + String(e[2])
		espejo.position = _sitio(e[0])
		if _espejos.is_empty():
			espejo.mira_al_sol = true
		else:
			espejo.fuente = _espejos[0]
		_espejos.append(espejo)
		$Entidades.add_child(espejo)
		espejo.girado.connect(_al_girar_espejo)
	for f in FAROLES:
		var farol: Node2D = RECOGIBLE.new()
		farol.objeto = "farol_hora"
		farol.marca = f[1]
		farol.dibujo = ARTE_MIRADOR + "farol.png"
		farol.color_halo = Color(1.0, 0.75, 0.35)
		farol.position = _sitio(f[0])
		$Entidades.add_child(farol)
	for k in EXCAVADORES:
		var bicho: Node2D = KIVULI.new()
		bicho.zona = Rect2(Vector2(MESETA.position) * 16.0 + Vector2(6, 10), Vector2(MESETA.size) * 16.0 - Vector2(12, 14))
		bicho.position = _sitio(k)
		$Entidades.add_child(bicho)
	_leer("dunas_cartel", _sitio(Vector2i(62, 29)))
	if not Estado.tiene("kivuli_vencido"):
		kivuli = JEFE.new()
		kivuli.centro = CRATER * 16.0
		kivuli.radios = CRATER_RADIOS * 16.0
		kivuli.position = CRATER * 16.0
		$Entidades.add_child(kivuli)
		kivuli.destruido.connect(_al_vencer_kivuli)


func _leer(charla: String, donde: Vector2) -> Node2D:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)
	return lectura


func espejos_encendidos() -> int:
	var n := 0
	for e in _espejos:
		if e.encendido:
			n += 1
	return n


func _al_girar_espejo() -> void:
	if puente.hecho():
		return
	var n := espejos_encendidos()
	if n < _espejos.size():
		if n > 0:
			_hud.mostrar_mensaje("Espejos encendidos: %d de %d" % [n, _espejos.size()])
		return
	puente.fundir()
	Sonido.efecto("arco_ocaso", 0.0, Vector2(PUENTE_CASILLAS.get_center()) * 16.0)
	Impacto.temblar(3.0, 0.5)
	_hud.mostrar_mensaje("El rayo funde la arena en cristal")


func en_crater(p: Vector2) -> bool:
	return ((p - CRATER * 16.0) / (CRATER_RADIOS * 16.0)).length() < 0.8


## Al entrar en el Cráter, despierta Kivuli; mientras pelean, la cámara se va hacia la mitad entre los dos
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(kivuli) and not Estado.tiene("kivuli_vencido"):
		hacia = ((kivuli.global_position + Vector2(0, -20) - maisha.global_position) * 0.5).clamp(Vector2(-140, -80), Vector2(140, 80))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(kivuli) or Estado.tiene("kivuli_vencido"):
		return
	if en_crater(maisha.global_position):
		_despertando = true
		if not Estado.tiene("kivuli_visto"):
			Estado.marcar("kivuli_visto")
			await CHARLA_SCRIPT.hablar(self, "kivuli_encuentro")
		if is_instance_valid(kivuli):
			kivuli.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO


func _al_vencer_kivuli() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica(MUSICA_DE.get("dunas_penumbra", "mirador_ocaso"))
	await CHARLA_SCRIPT.hablar(self, "kivuli_vencido")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("dunas_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "dunas_llegada")
	Estado.marcar("dunas_llegada")
