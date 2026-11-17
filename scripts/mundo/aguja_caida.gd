extends "res://scripts/mundo/escena_mundo.gd"
## LA AGUJA CAÍDA (Asterhaul, el camino del norte de Mji-Jiwe): terrazas de piedra de estrella colgadas sobre el
## viento astral. Lo que no es terraza es abismo. Aquí manda el sonido: los MONOLITOS-DIAPASÓN
## (asterhaul/monolito.gd) cantan con la Resonancia de Ámbar (o un momento, de un campanazo con la Carga), y su
## onda se contagia de uno a otro.
##   - LA BASE (sur): PIGO, la afinadora de campanas, en gris (sigilia/escriba.gd; su Esquirla está en la Cresta).
##     La ESTELA se lee. Dos monolitos junto al primer PUENTE DE CRISTAL (asterhaul/puente_cristal.gd): las losas
##     solo existen donde llega una onda. Con un campanazo basta para cruzarlo corriendo.
##   - LA CRESTA DE LOS DIAPASONES (en medio): la Esquirla de Pigo, los POPO (enemigos/popo.gd) y, a cada lado,
##     un PEÑASCO FLOTANTE (asterhaul/penasco.gd) que acude al monolito que canta y lleva a un ISLOTE: al oeste,
##     una Esquirla de Estrella; al este, un secreto. Con su pulso, Pigo enseña la RESONANCIA DE ÁMBAR (P).
##   - EL PUENTE ALTO: largo; hace falta que canten tres monolitos en cadena (el de la Cresta y los dos de las
##     peñas sueltas, que solo despiertan por simpatía).
##   - EL NIDO DE LA CIMA: KIPANGA ASTRAL (enemigos/kipanga.gd) y cuatro monolitos. Despierta al entrar. Al
##     vencerlo se rompe la tercera Cadena («cadena_norte_rota»).
##   - LAS CAÍDAS: las casillas «=» son vacío (asterhaul/vacio.gd: si nada la sostiene, Maisha cae).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const PUENTE := preload("res://scripts/mundo/asterhaul/puente_cristal.gd")
const PENASCO := preload("res://scripts/mundo/asterhaul/penasco.gd")
const POPO := preload("res://scripts/enemigos/popo.gd")
const KIPANGA := preload("res://scripts/enemigos/kipanga.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const ARTE := "res://arte/mundos/asterhaul/"
## (todo en casillas)
const PIGO := Vector2i(36, 68)
const ESTELA := Vector2i(33, 66)
## los monolitos: los dos de la Base, los tres de la Cresta, los de los islotes, los dos de las peñas sueltas del
## puente alto (cantan por simpatía) y los cuatro del Nido
const MONOLITOS := [Vector2i(31, 63), Vector2i(40, 63), Vector2i(18, 49), Vector2i(53, 49), Vector2i(38, 45),
	Vector2i(6, 51), Vector2i(65, 51), Vector2i(40, 40), Vector2i(40, 35),
	Vector2i(26, 17), Vector2i(45, 17), Vector2i(26, 27), Vector2i(45, 27)]
const PUENTES := [Rect2i(34, 58, 4, 4), Rect2i(34, 34, 4, 10)]
## peñasco: [muelle del lado de la Cresta, muelle del lado del islote]
const PENASCOS := [[Vector2i(14, 49), Vector2i(8, 49)], [Vector2i(56, 49), Vector2i(62, 49)]]
const POPOS := [Vector2i(22, 53), Vector2i(49, 53), Vector2i(31, 39)]
## esquirla: [objeto, casilla, marca]
const ESQUIRLAS := [["esquirla_pigo", Vector2i(36, 47), "esquirla/pigo"], ["esquirla_estrella", Vector2i(4, 50), "esquirla/islote"]]
const INSCRIPCION := Vector2i(67, 50)
## el Nido: su centro y sus semiejes (px)
const NIDO := Vector2(576, 360)
const RADIOS := Vector2(240, 176)

var _kipanga: Node2D = null
var _despertando := false
var _filas: PackedStringArray


func _ready() -> void:
	super()
	Estado.marcar("aguja_caida")
	_filas = $Region._filas
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	add_child(vacio)
	_poner_cosas()
	if not Estado.tiene("aguja_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	_poner_adorno("aguja/estela", ESTELA, 12, 6)
	_leer("estela_resonancia", _sitio(ESTELA) + Vector2(0, 6))
	_leer("aguja_islote_este", _sitio(INSCRIPCION))
	var pigo: StaticBody2D = ESCRIBA.new()
	pigo.nombre = "pigo"
	pigo.dibujo = "pigo"
	pigo.sufijo_apagado = "_gris"
	pigo.sufijo_marca = "_pulso"
	pigo.position = _sitio(PIGO)
	$Entidades.add_child(pigo)
	for c in MONOLITOS:
		var monolito: StaticBody2D = MONOLITO.new()
		monolito.position = _sitio(c)
		$Entidades.add_child(monolito)
	for r in PUENTES:
		var puente: Node2D = PUENTE.new()
		puente.casillas = r
		add_child(puente)
	for p in PENASCOS:
		var penasco: Node2D = PENASCO.new()
		penasco.muelle_a = p[0]
		penasco.muelle_b = p[1]
		add_child(penasco)
	for c in POPOS:
		var popo: Node2D = POPO.new()
		popo.position = _sitio(c)
		$Entidades.add_child(popo)
	for e in ESQUIRLAS:
		var esquirla: Node2D = RECOGIBLE.new()
		esquirla.objeto = e[0]
		esquirla.marca = e[2]
		esquirla.dibujo = ARTE + "desfiladero/esquirla.png"
		esquirla.color_halo = Color(1.0, 0.75, 0.3)
		esquirla.position = _sitio(e[1])
		$Entidades.add_child(esquirla)
	if not Estado.tiene("kipanga_vencido"):
		_kipanga = KIPANGA.new()
		_kipanga.centro = NIDO
		_kipanga.radios = RADIOS
		_kipanga.position = NIDO + Vector2(0, -24)
		$Entidades.add_child(_kipanga)
		_kipanga.destruido.connect(_al_vencer_kipanga)


## Un adorno que no se atraviesa: su dibujo de pie y una caja en la base
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fondo: float) -> void:
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


func _leer(charla: String, donde: Vector2) -> void:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)


## ¿Hay algo bajo ese punto de vacío? (lo sabe el vigía de las caídas)
func sostenida(p: Vector2) -> bool:
	return $Vacio.sostenida(p)


func _process(delta: float) -> void:
	var maisha := _maisha
	if maisha == null:
		return
	if maisha.global_position.x > 64.0 * 16.0 and _filas[floori(maisha.global_position.y / 16.0)][floori(maisha.global_position.x / 16.0)] == "%" \
			and not Estado.tiene("secreto/aguja_caida/islote_este"):
		Estado.marcar("secreto/aguja_caida/islote_este")
	# Kipanga: despierta al entrar en el Nido; mientras pelean, la cámara se va hacia la mitad entre Maisha y él
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_kipanga) and not Estado.tiene("kipanga_vencido"):
		hacia = ((_kipanga.global_position + Vector2(0, -30) - maisha.global_position) * 0.5).clamp(Vector2(-150, -86), Vector2(150, 86))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_kipanga) or Estado.tiene("kipanga_vencido"):
		return
	if ((maisha.global_position - NIDO) / RADIOS).length() < 0.8:
		_despertando = true
		if not Estado.tiene("kipanga_visto"):
			Estado.marcar("kipanga_visto")
			await CHARLA_SCRIPT.hablar(self, "kipanga_encuentro")
		if is_instance_valid(_kipanga):
			_kipanga.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


func _al_vencer_kipanga() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica("aguja_caida")
	await CHARLA_SCRIPT.hablar(self, "kipanga_vencido")


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "resonancia_ambar":
		_hud.mostrar_mensaje("Resonancia de Ámbar (P): haz cantar a los monolitos")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("aguja_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "aguja_llegada")
	Estado.marcar("aguja_llegada")
