extends "res://scripts/mundo/escena_mundo.gd"
## LA CALZADA DE LOS OBELISCOS (el Valle del Ocaso, el camino del sureste de Jioni). Islas de arenisca sobre el
## abismo, unidas solo por las SOMBRAS de los obeliscos (ocaso/sol.gd): cada tramo pide una hora del sol, y al girar
## un Reloj de Sol se abre un tramo y se cierra otro.
##   - DESDE JIONI (noroeste): sol al OESTE → la sombra cruza al Pilar I.
##   - EL PILAR I: sol al ESTE → la sombra del Balcón del Mediodía llega (secreto, un farol); sol al SUR → la del
##     Viaducto sube hasta aquí.
##   - EL VIADUCTO DE LOS CENTINELAS: dos Centinelas de Reloj (enemigos/centinela.gd): en penumbra andan y pegan;
##     al sol se quedan de piedra y la Carga los vuelca. Un farol. Sol al SUR → la sombra de la Rotonda sube.
##   - LA ROTONDA: SAA-MCHANGA (enemigos/saa_mchanga.gd), cuatro obeliscos para esconderse del rayo y un Reloj.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const SOL := preload("res://scripts/mundo/ocaso/sol.gd")
const RELOJ := preload("res://scripts/mundo/ocaso/reloj_sol.gd")
const CENTINELA := preload("res://scripts/enemigos/centinela.gd")
const JEFE := preload("res://scripts/enemigos/saa_mchanga.gd")
const ARTE_MIRADOR := "res://arte/mundos/ocaso/mirador/"
const ARTE := "res://arte/mundos/ocaso/calzada/"
## (todo en casillas) obelisco: [su pie, el largo de su sombra]
const OBELISCOS := [[Vector2i(17, 8), 9], [Vector2i(48, 7), 10], [Vector2i(32, 22), 8], [Vector2i(34, 37), 5],
	[Vector2i(27, 41), 4], [Vector2i(42, 41), 4], [Vector2i(27, 48), 4], [Vector2i(42, 48), 4]]
const RELOJES := [Vector2i(8, 8), Vector2i(30, 11), Vector2i(55, 10), Vector2i(26, 24), Vector2i(34, 52)]
const PILARES := [Vector2i(28, 4), Vector2i(36, 4), Vector2i(25, 31), Vector2i(43, 31)]
const CENTINELAS := [Vector2i(29, 28), Vector2i(40, 28)]
const VIADUCTO := Rect2i(24, 22, 21, 11)
const FAROLES := [[Vector2i(59, 5), "farol/calzada_1"], [Vector2i(42, 24), "farol/calzada_2"]]
const ROTONDA := Vector2(34.5, 44.5)
const ROTONDA_RADIOS := Vector2(13.5, 9.5)
## dónde da el sol de lleno (en casillas): al oeste y al este, media Viaducto cada uno; al sur, la Rotonda
const LUZ := {0: Rect2i(0, 14, 34, 20), 1: Rect2i(0, 34, 72, 22), 2: Rect2i(34, 14, 38, 20)}

var sol: Node2D
var saa: Node2D = null
var _despertando := false


func _ready() -> void:
	sol = SOL.new()
	sol.name = "Sol"
	for o in OBELISCOS:
		sol.obeliscos.append(o)
	for h in LUZ:
		var r: Rect2i = LUZ[h]
		sol.luz[h] = Rect2(Vector2(r.position) * 16.0, Vector2(r.size) * 16.0)
	add_child(sol)
	super()
	Estado.marcar("calzada_obeliscos")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	add_child(vacio)
	_poner_cosas()
	if not Estado.tiene("calzada_llegada"):
		_pensar_al_llegar.call_deferred()


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
	for c in PILARES:
		_adorno(ARTE + "pilar.png", c, Vector2(22, 8))
	for c in RELOJES:
		var reloj: StaticBody2D = RELOJ.new()
		reloj.position = _sitio(c)
		$Entidades.add_child(reloj)
	for f in FAROLES:
		var farol: Node2D = RECOGIBLE.new()
		farol.objeto = "farol_hora"
		farol.marca = f[1]
		farol.dibujo = ARTE_MIRADOR + "farol.png"
		farol.color_halo = Color(1.0, 0.75, 0.35)
		farol.position = _sitio(f[0])
		$Entidades.add_child(farol)
	for c in CENTINELAS:
		var centinela: Node2D = CENTINELA.new()
		centinela.zona = Rect2(Vector2(VIADUCTO.position) * 16.0 + Vector2(8, 12), Vector2(VIADUCTO.size) * 16.0 - Vector2(16, 16))
		centinela.position = _sitio(c)
		$Entidades.add_child(centinela)
	var lectura: Node2D = LECTURA.new()
	lectura.charla = "calzada_cartel"
	lectura.position = _sitio(Vector2i(14, 5))
	$Entidades.add_child(lectura)
	if not Estado.tiene("saa_vencido"):
		saa = JEFE.new()
		saa.position = ROTONDA * 16.0
		$Entidades.add_child(saa)
		saa.destruido.connect(_al_vencer_saa)


func en_rotonda(p: Vector2) -> bool:
	return ((p - ROTONDA * 16.0) / (ROTONDA_RADIOS * 16.0)).length() < 0.8


func _pensar(charla: String) -> void:
	if Estado.tiene(charla):
		return
	Estado.marcar(charla)
	await get_tree().create_timer(0.6).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, charla)


## Al llegar al Viaducto, Maisha ve a los Centinelas; al entrar en la Rotonda, despierta Saa-Mchanga
func _process(_delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	if not Estado.tiene("calzada_centinelas") and Rect2(Vector2(VIADUCTO.position) * 16.0, Vector2(VIADUCTO.size) * 16.0).has_point(maisha.global_position):
		_pensar("calzada_centinelas")
	if _despertando or not is_instance_valid(saa) or Estado.tiene("saa_vencido"):
		return
	if en_rotonda(maisha.global_position):
		_despertando = true
		if not Estado.tiene("saa_visto"):
			Estado.marcar("saa_visto")
			await CHARLA_SCRIPT.hablar(self, "saa_encuentro")
		if is_instance_valid(saa):
			saa.despertar()


func _al_vencer_saa() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica(MUSICA_DE.get("calzada_obeliscos", "mirador_ocaso"))
	await CHARLA_SCRIPT.hablar(self, "saa_vencido")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("calzada_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "calzada_llegada")
	Estado.marcar("calzada_llegada")
