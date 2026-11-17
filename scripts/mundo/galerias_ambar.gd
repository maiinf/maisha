extends "res://scripts/mundo/escena_mundo.gd"
## LAS GALERÍAS DE ÁMBAR (Asterhaul, el camino del oeste de Mji-Jiwe): la mina de los canteros. Las VÍAS cruzan
## todas las salas; lo que rueda por ellas obedece a los CAMBIOS DE AGUJAS (asterhaul/aguja.gd: un golpe de cetro).
##   - EL TALLER DE KITO (este): KITO, la talladora de ámbar, en gris (sigilia/escriba.gd; su Esquirla está en la
##     Veta Norte). El primer cambio de agujas (oeste / norte) y una VAGONETA: desviada al norte, rompe la
##     BARRICADA de la Veta. Con su pulso, Kito abre la REJA del Cruce Mayor.
##   - LA VETA NORTE: la Esquirla de Kito y un MCHIMBAJI rodando por su vía.
##   - EL CRUCE MAYOR: el desvío triple (oeste: la Cámara del Ancla · norte: un ramal muerto con PARACHOQUES, para
##     estampar a los Mchimbaji · sur: la Bóveda), otra vagoneta y otro Mchimbaji.
##   - LA BÓVEDA DE LAS GEODAS (sur), a oscuras: las GEODAS RESONANTES (asterhaul/geoda.gd) se encienden a golpes
##     y alumbran. Al fondo, una Esquirla de Estrella.
##   - LA CÁMARA DEL ANCLA OESTE: EL KIFARU DE BASALTO (enemigos/kifaru.gd), cuatro pilares y una vagoneta.
##     Despierta al entrar. Al vencerlo se rompe la Cadena del Oeste («cadena_oeste_rota»).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const MURO := preload("res://scripts/mundo/asterhaul/muro_agrietado.gd")
const VAGONETA := preload("res://scripts/mundo/asterhaul/vagoneta.gd")
const AGUJA := preload("res://scripts/mundo/asterhaul/aguja.gd")
const REJA := preload("res://scripts/mundo/asterhaul/reja.gd")
const GEODA := preload("res://scripts/mundo/asterhaul/geoda.gd")
const PILAR := preload("res://scripts/mundo/asterhaul/pilar_basalto.gd")
const MCHIMBAJI := preload("res://scripts/enemigos/mchimbaji.gd")
const KIFARU := preload("res://scripts/enemigos/kifaru.gd")
const ARTE := "res://arte/mundos/asterhaul/"
const PENUMBRA := Color(0.16, 0.15, 0.22)
## (todo en casillas)
const KITO := Vector2i(70, 25)
const TALLER := Vector2i(74, 23)
const CARTEL := Vector2i(67, 25)
const REJA_KITO := Vector2i(49, 27)
const PARACHOQUES := Vector2i(32, 22)
## aguja: [casilla del desvío, ramales, marca]
const AGUJAS := [
	[Vector2i(64, 27), [Vector2i.LEFT, Vector2i.UP], "galerias/aguja_a"],
	[Vector2i(40, 27), [Vector2i.LEFT, Vector2i.UP, Vector2i.DOWN], "galerias/aguja_b"],
]
## barricada (solo la rompe una vagoneta): [casilla, marca]
const BARRICADAS := [[Vector2i(64, 17), "galerias/barricada_veta"], [Vector2i(40, 36), "galerias/barricada_boveda"],
	[Vector2i(29, 27), "galerias/barricada_camara"]]
const VAGONETAS := [Vector2i(76, 27), Vector2i(45, 27), Vector2i(23, 27)]
## Mchimbaji: [casilla, hacia dónde empieza a rodar]
const MCHIMBAJIS := [[Vector2i(58, 9), Vector2i.LEFT], [Vector2i(36, 27), Vector2i.RIGHT], [Vector2i(56, 44), Vector2i.RIGHT]]
const GEODAS := [Vector2i(43, 41), Vector2i(52, 49), Vector2i(60, 41), Vector2i(67, 49), Vector2i(45, 51)]
## esquirla: [objeto, casilla, marca]
const ESQUIRLAS := [["esquirla_kito", Vector2i(54, 7), "esquirla/kito"], ["esquirla_estrella", Vector2i(71, 51), "esquirla/boveda"]]
## la Cámara del Ancla: su centro (en casillas), sus semiejes (px) y sus pilares
const CAMARA := Vector2(14.5, 27.5)
const RADIOS := Vector2(208, 176)
const PILARES := [Vector2i(8, 22), Vector2i(20, 22), Vector2i(8, 32), Vector2i(20, 32)]

var _kifaru: Node2D = null
var _despertando := false
var _penumbra: CanvasModulate
var _luz_maisha: PointLight2D
var _oscuro := 0.0


func _ready() -> void:
	super()
	Estado.marcar("galerias_ambar")
	_poner_cosas()
	_poner_oscuridad()
	if not Estado.tiene("galerias_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	_poner_adorno("mji_jiwe/casa", TALLER, 58, 14, 0)
	_poner_adorno("desfiladero/estela", CARTEL, 12, 6, -1)
	_leer("galerias_aguja", _sitio(CARTEL) + Vector2(0, 6))
	_poner_adorno("galerias/parachoques", PARACHOQUES, 16, 8, -1).add_to_group("parachoques")
	var kito: StaticBody2D = ESCRIBA.new()
	kito.nombre = "kito"
	kito.dibujo = "kito"
	kito.sufijo_apagado = "_gris"
	kito.sufijo_marca = "_pulso"
	kito.position = _sitio(KITO)
	$Entidades.add_child(kito)
	var reja: StaticBody2D = REJA.new()
	reja.marca = "kito_hablado"
	reja.position = _sitio(REJA_KITO)
	$Entidades.add_child(reja)
	if not Estado.tiene("kito_hablado"):
		_leer("galerias_reja", _sitio(REJA_KITO) + Vector2(14, 4))
	for a in AGUJAS:
		var aguja: Node2D = AGUJA.new()
		aguja.casilla = a[0]
		aguja.ramales.assign(a[1])
		aguja.marca = a[2]
		aguja.position = _sitio(a[0]) + Vector2(12, -12)
		$Entidades.add_child(aguja)
	for b in BARRICADAS:
		var barricada: StaticBody2D = MURO.new()
		barricada.marca = b[1]
		barricada.con_carga = false
		barricada.dibujo = "galerias/barricada"
		barricada.position = _sitio(b[0])
		$Entidades.add_child(barricada)
	for v in VAGONETAS:
		var vagoneta: StaticBody2D = VAGONETA.new()
		vagoneta.position = _sitio(v)
		$Entidades.add_child(vagoneta)
	for m in MCHIMBAJIS:
		var bicho: Node2D = MCHIMBAJI.new()
		bicho.dir = m[1]
		bicho.position = _sitio(m[0])
		$Entidades.add_child(bicho)
	for i in GEODAS.size():
		var geoda: StaticBody2D = GEODA.new()
		geoda.marca = "galerias/geoda_%d" % (i + 1)
		geoda.position = _sitio(GEODAS[i])
		$Entidades.add_child(geoda)
	for e in ESQUIRLAS:
		var esquirla: Node2D = RECOGIBLE.new()
		esquirla.objeto = e[0]
		esquirla.marca = e[2]
		esquirla.dibujo = ARTE + "desfiladero/esquirla.png"
		esquirla.color_halo = Color(1.0, 0.75, 0.3)
		esquirla.position = _sitio(e[1])
		$Entidades.add_child(esquirla)
	for p in PILARES:
		var pilar: StaticBody2D = PILAR.new()
		pilar.position = _sitio(p)
		$Entidades.add_child(pilar)
	if not Estado.tiene("kifaru_vencido"):
		_kifaru = KIFARU.new()
		_kifaru.centro = CAMARA * 16.0
		_kifaru.radios = RADIOS
		_kifaru.position = _sitio(Vector2i(8, 27))
		$Entidades.add_child(_kifaru)
		_kifaru.destruido.connect(_al_vencer_kifaru)


## Un adorno que no se atraviesa: su dibujo de pie (o un fotograma de su tira de dos) y una caja en la base
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fondo: float, fotograma: int) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = _sitio(casilla)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	if fotograma >= 0:
		sprite.hframes = 2
		sprite.frame = fotograma
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


func _leer(charla: String, donde: Vector2) -> void:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)


## LA OSCURIDAD DE LA BÓVEDA: todo se apaga al bajar a ella (y Maisha alumbra un poco); arriba, luz normal
func _poner_oscuridad() -> void:
	_penumbra = CanvasModulate.new()
	_penumbra.color = Color.WHITE
	add_child(_penumbra)
	_luz_maisha = PointLight2D.new()
	_luz_maisha.texture = preload("res://scripts/mundo/relieve.gd").textura_luz(256)
	_luz_maisha.texture_scale = 1.6 if Estado.tiene("farol_geoda") else 1.0              # (el farol de geoda de Chuma)
	_luz_maisha.color = Color(1.0, 0.92, 0.75)
	_luz_maisha.energy = 0.0
	_luz_maisha.position = Vector2(0, -10)
	_maisha.add_child(_luz_maisha)


## ¿Está ese punto en la Bóveda de las Geodas (o en su paso)?
func en_boveda(p: Vector2) -> bool:
	return p.y > 36.0 * 16.0 and p.x > 33.0 * 16.0


## En la Bóveda, se hace de noche. Al entrar en la Cámara del Ancla, despierta el Kifaru; mientras pelean, la cámara
## se va hacia la mitad entre Maisha y él.
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	_oscuro = move_toward(_oscuro, 1.0 if en_boveda(maisha.global_position) else 0.0, delta * 1.6)
	_penumbra.color = Color.WHITE.lerp(PENUMBRA, _oscuro)
	_luz_maisha.energy = 1.1 * _oscuro
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_kifaru) and not Estado.tiene("kifaru_vencido"):
		hacia = ((_kifaru.global_position + Vector2(0, -20) - maisha.global_position) * 0.5).clamp(Vector2(-140, -80), Vector2(140, 80))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_kifaru) or Estado.tiene("kifaru_vencido"):
		return
	if ((maisha.global_position - CAMARA * 16.0) / RADIOS).length() < 0.85:
		_despertando = true
		if not Estado.tiene("kifaru_visto"):
			Estado.marcar("kifaru_visto")
			await CHARLA_SCRIPT.hablar(self, "kifaru_encuentro")
		if is_instance_valid(_kifaru):
			_kifaru.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


func _al_vencer_kifaru() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica("galerias_ambar")
	await CHARLA_SCRIPT.hablar(self, "kifaru_vencido")


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca.begins_with("galerias/barricada_"):
		_hud.mostrar_mensaje("La barricada se viene abajo")
	elif marca.begins_with("galerias/geoda_"):
		var n := 0
		for i in GEODAS.size():
			if Estado.tiene("galerias/geoda_%d" % (i + 1)):
				n += 1
		_hud.mostrar_mensaje("Geodas encendidas: %d de %d" % [n, GEODAS.size()])
		if n == GEODAS.size():
			Estado.marcar("secreto/galerias_ambar/geodas")
	elif marca == "kito_hablado":
		_hud.mostrar_mensaje("Kito abre la reja del Cruce Mayor")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("galerias_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "galerias_llegada")
	Estado.marcar("galerias_llegada")
