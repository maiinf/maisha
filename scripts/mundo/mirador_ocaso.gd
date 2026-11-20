extends "res://scripts/mundo/escena_mundo.gd"
## EL MIRADOR DEL OCASO (el Valle del Ocaso, la primera zona: al sur del Kitovu). Mesetas de arenisca colgadas
## sobre el abismo de un atardecer que no se acaba. Entre meseta y meseta solo hay vacío (asterhaul/vacio.gd): se
## cruza por las SOMBRAS LARGAS de los obeliscos, que son sólidas y caen hacia el lado contrario del sol
## (ocaso/sol.gd). El sol se gira con los RELOJES DE SOL (ocaso/reloj_sol.gd): oeste → sur → este.
##   - LA ENTRADA (arriba): con el sol al oeste, la sombra del primer obelisco cruza al BALCÓN ESTE (el 1.er Farol
##     de la Hora y un Kivuli). Una rampa baja del balcón a la plaza.
##   - LA PLAZA DEL RELOJ: MWANGA, el viejo farolillero, y el 1.er Reloj (no gira hasta que Mwanga enseña cómo).
##     Sol al este: la sombra del obelisco del oeste cruza a las Terrazas. Sol al sur: la del Arco sube a la plaza.
##   - LAS TERRAZAS DE PENUMBRA (oeste): dos Kivuli y el 2.º Reloj; con el sol al sur, una sombra sube al SECRETO
##     (el 2.º Farol).
##   - EL ARCO DEL ATARDECER (sur): un Kivuli y dos ESPEJOS DE BRONCE (ocaso/espejo.gd): el primero tiene que mirar
##     al sol; el segundo, al primero. Con los dos encendidos, el arco se abre (la bajada a Jioni).
## Los KIVULI (enemigos/kivuli.gd) solo se pueden golpear cuando el sol les da de lleno: el sol ilumina el lado del
## valle donde está.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const SOL := preload("res://scripts/mundo/ocaso/sol.gd")
const RELOJ := preload("res://scripts/mundo/ocaso/reloj_sol.gd")
const ESPEJO := preload("res://scripts/mundo/ocaso/espejo.gd")
const KIVULI := preload("res://scripts/enemigos/kivuli.gd")
const ARTE := "res://arte/mundos/ocaso/mirador/"
## (todo en casillas) obelisco: [su pie, el largo de su sombra]
const OBELISCOS := [[Vector2i(42, 6), 11], [Vector2i(29, 27), 10], [Vector2i(39, 37), 7], [Vector2i(11, 16), 7]]
const RELOJES := [Vector2i(43, 23), Vector2i(12, 28)]
const MWANGA := Vector2i(37, 21)
## farol: [casilla, marca]
const FAROLES := [[Vector2i(65, 6), "farol/mirador_1"], [Vector2i(11, 5), "farol/mirador_2"]]
## kivuli: [casilla, su meseta (en casillas)]
const KIVULIS := [[Vector2i(61, 9), Rect2i(54, 3, 15, 11)], [Vector2i(8, 22), Rect2i(4, 16, 17, 19)],
	[Vector2i(16, 31), Rect2i(4, 16, 17, 19)], [Vector2i(44, 44), Rect2i(26, 37, 31, 10)]]
## espejo: [casilla, hacia dónde mira al principio (0 norte · 1 este · 2 sur · 3 oeste), marca]
const ESPEJOS := [[Vector2i(34, 42), 0, "mirador_a"], [Vector2i(48, 42), 2, "mirador_b"]]
const ARCO := Vector2i(54, 40)
## dónde da el sol de lleno con cada hora (en casillas): al oeste, las Terrazas; al sur, el Arco; al este, el Balcón
const LUZ := {0: Rect2i(0, 0, 23, 50), 1: Rect2i(0, 36, 72, 14), 2: Rect2i(52, 0, 20, 23)}

var sol: Node2D
var _arco: StaticBody2D
var _espejos: Array = []


func _ready() -> void:
	# (antes de super(): por si algún día se vuelve de Jioni)
	var paso: Area2D = preload("res://scripts/mundo/puerta.gd").new()
	paso.id = "jioni"
	paso.destino = "jioni"
	paso.destino_puerta = "mirador"
	paso.salida = Vector2.LEFT
	paso.tam = Vector2(22, 12)
	paso.cerrada_hasta = "arco_atardecer_abierto"
	paso.position = _sitio(ARCO) + Vector2(0, -6)
	add_child(paso)
	paso.cerrada.connect(_al_tocar_arco)
	sol = SOL.new()
	sol.name = "Sol"
	for o in OBELISCOS:
		sol.obeliscos.append(o)
	for h in LUZ:
		var r: Rect2i = LUZ[h]
		sol.luz[h] = Rect2(Vector2(r.position) * 16.0, Vector2(r.size) * 16.0)
	add_child(sol)
	super()
	Estado.marcar("mirador_ocaso")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	add_child(vacio)
	_poner_cosas()
	sol.cambiada.connect(_al_girar_sol)
	if not Estado.tiene("mirador_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	for o in OBELISCOS:
		var ob := _poner_adorno("obelisco", o[0], 12, 6)
		ob.add_to_group("obeliscos")
	_leer("mirador_obelisco", _sitio(OBELISCOS[0][0]) + Vector2(0, 6))
	for i in RELOJES.size():
		var reloj: StaticBody2D = RELOJ.new()
		reloj.requiere = "mwanga_reloj"
		reloj.position = _sitio(RELOJES[i])
		$Entidades.add_child(reloj)
		reloj.atascado.connect(_al_reloj_atascado)
	var mwanga: StaticBody2D = VECINO.new()
	mwanga.id = "mwanga"
	mwanga.charla = "mwanga"
	mwanga.position = _sitio(MWANGA)
	$Entidades.add_child(mwanga)
	for f in FAROLES:
		var farol: Node2D = RECOGIBLE.new()
		farol.objeto = "farol_hora"
		farol.marca = f[1]
		farol.dibujo = ARTE + "farol.png"
		farol.color_halo = Color(1.0, 0.75, 0.35)
		farol.position = _sitio(f[0])
		$Entidades.add_child(farol)
	for k in KIVULIS:
		var kivuli: Node2D = KIVULI.new()
		var r: Rect2i = k[1]
		kivuli.zona = Rect2(Vector2(r.position) * 16.0 + Vector2(6, 10), Vector2(r.size) * 16.0 - Vector2(12, 14))
		kivuli.position = _sitio(k[0])
		$Entidades.add_child(kivuli)
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
		espejo.girado.connect(_al_girar_espejo)
	_poner_arco()


func _leer(charla: String, donde: Vector2) -> Node2D:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)
	return lectura


## Un adorno que no se atraviesa: su dibujo de pie y una caja en la base
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fondo: float) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = _sitio(casilla)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cuerpo.add_child(sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(ancho, fondo)
	forma.shape = caja
	forma.position = Vector2(0, -fondo / 2.0)
	cuerpo.add_child(forma)
	$Entidades.add_child(cuerpo)
	return cuerpo


## El Arco del Atardecer: dos columnas que no se atraviesan; el hueco, cerrado por el velo hasta los dos espejos
func _poner_arco() -> void:
	_arco = StaticBody2D.new()
	_arco.position = _sitio(ARCO)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + "arco.png")
	sprite.hframes = 2
	sprite.offset = Vector2(0, -32)
	_arco.add_child(sprite)
	for x in [-24.0, 24.0]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(14, 8)
		forma.shape = caja
		forma.position = Vector2(x, -4)
		_arco.add_child(forma)
	$Entidades.add_child(_arco)
	if Estado.tiene("arco_atardecer_abierto"):
		sprite.frame = 1


func espejos_encendidos() -> int:
	var n := 0
	for e in _espejos:
		if e.encendido:
			n += 1
	return n


func _al_girar_espejo() -> void:
	if Estado.tiene("arco_atardecer_abierto"):
		return
	var n := espejos_encendidos()
	if n < _espejos.size():
		if n > 0:
			_hud.mostrar_mensaje("Espejos encendidos: %d de %d" % [n, _espejos.size()])
		return
	Estado.marcar("arco_atardecer_abierto")
	(_arco.get_child(0) as Sprite2D).frame = 1
	Sonido.efecto("arco_ocaso", 0.0, _arco.global_position)
	Impacto.temblar(3.0, 0.5)
	_hud.mostrar_mensaje("El Arco del Atardecer se abre")


func _al_girar_sol(hora: int) -> void:
	if hora == SOL.SUR:
		Estado.marcar("mirador/sol_sur")


func _al_reloj_atascado() -> void:
	CHARLA_SCRIPT.hablar(self, "mirador_reloj_atascado")


func _al_tocar_arco() -> void:
	CHARLA_SCRIPT.hablar(self, "mirador_arco_abierto" if Estado.tiene("arco_atardecer_abierto") else "mirador_arco")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("mirador_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "mirador_llegada")
	Estado.marcar("mirador_llegada")
