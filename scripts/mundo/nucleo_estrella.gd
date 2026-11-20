extends "res://scripts/mundo/escena_mundo.gd"
## EL NÚCLEO DE LA ESTRELLA (Asterhaul, el final): el pozo bajo la Losa de Mji-Jiwe, que se abre con las tres
## Cadenas rotas y los doce Yunques de Memoria despiertos. Tres cámaras, una por poder, y en orden:
##   - EL ATRIO DE LA ESTRELLA: Mauti espera aquí.
##   - 1. LA CÁMARA SÍSMICA (oeste): un muro agrietado, los Kaa-Jiwe y una vagoneta que hay que lanzar contra un
##     derrumbe; detrás, el PILAR del primer sello (Carga).
##   - 2. LA CÁMARA MAGNÉTICA (en medio; su compuerta la abre el primer sello): un río de escoria con una barcaza
##     (Pulso), los Kovu y, al otro lado, un bloque-imán que hay que llevar a la PLACA del segundo sello.
##   - 3. LA CÁMARA DE LA RESONANCIA (este; la abre el segundo sello): un puente de cristal sobre el abismo que
##     sostienen dos monolitos en cadena, los Popo y, en la isla del fondo, el MONOLITO del tercer sello, que solo
##     despierta con la nota de verdad (la Resonancia de Maisha, no un eco ni un campanazo).
##   - LA PUERTA TRIPLE (arriba de la Cámara Magnética): un ojo por sello; con los tres, se abre.
##   - EL SANTUARIO: EL CORAZÓN DEL METEORITO (enemigos/corazon_meteorito.gd). Al calmarlo, Mauti llega, se ve lo
##     que guardaba dentro y el Cetro del Nexo despierta del todo («asterhaul_libre»): el final de Asterhaul.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const MURO := preload("res://scripts/mundo/asterhaul/muro_agrietado.gd")
const VAGONETA := preload("res://scripts/mundo/asterhaul/vagoneta.gd")
const PILAR := preload("res://scripts/mundo/asterhaul/pilar_diapason.gd")
const BARCAZA := preload("res://scripts/mundo/asterhaul/barcaza.gd")
const BLOQUE := preload("res://scripts/mundo/asterhaul/bloque_iman.gd")
const COMPUERTA := preload("res://scripts/mundo/asterhaul/compuerta.gd")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const PUENTE := preload("res://scripts/mundo/asterhaul/puente_cristal.gd")
const PUERTA_TRIPLE := preload("res://scripts/mundo/asterhaul/puerta_triple.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const KAA := preload("res://scripts/enemigos/kaa_jiwe.gd")
const KOVU := preload("res://scripts/enemigos/kovu.gd")
const POPO := preload("res://scripts/enemigos/popo.gd")
const CORAZON := preload("res://scripts/enemigos/corazon_meteorito.gd")
const PLACA := preload("res://arte/mundos/asterhaul/fundicion/placa.png")
const FIN := preload("res://scripts/interfaz/fin_mundo.gd")
const YUNQUES := preload("res://scripts/mundo/asterhaul/yunques.gd")
const SELLOS: Array[String] = ["nucleo/sello_sismico", "nucleo/sello_magnetico", "nucleo/sello_resonante"]
## (todo en casillas)
const MAUTI := Vector2i(37, 57)
const ESTELA := Vector2i(46, 55)
const MURO_SISMICO := Vector2i(6, 44)
const DERRUMBE := Vector2i(18, 38)
const VAGONETA_C := Vector2i(6, 38)
const PILAR_SELLO := Vector2i(22, 37)
const KAAS := [Vector2i(11, 50), Vector2i(19, 53)]
const COMPUERTAS := [[Vector2i(28, 40), "nucleo/sello_sismico"], [Vector2i(57, 40), "nucleo/sello_magnetico"]]
const MUELLES := [Vector2i(36, 37), Vector2i(46, 37)]
const BLOQUE_C := Vector2i(51, 41)
const PLACA_C := Vector2i(51, 36)
const KOVUS := [[Vector2i(41, 34), Vector2i(45, 34)], [Vector2i(43, 44), Vector2i(38, 44)]]
const PUERTA_C := Vector2i(51, 31)
## la Cámara de la Resonancia: los dos monolitos del puente, el del sello y el puente
const MONOLITO_CORNISA := Vector2i(62, 42)
const MONOLITO_PENA := Vector2i(66, 37)
const MONOLITO_SELLO := Vector2i(77, 41)
const PUENTE_C := Rect2i(64, 39, 8, 2)
const POPOS := [Vector2i(70, 44), Vector2i(75, 37)]
## el Santuario: su centro y sus semiejes (px), y sus cuatro monolitos
const SANTUARIO := Vector2(680, 232)
const RADIOS := Vector2(272, 176)
const MONOLITOS_SANTUARIO := [Vector2i(30, 12), Vector2i(55, 12), Vector2i(32, 20), Vector2i(52, 20)]

var _corazon: Node2D = null
var _despertando := false


func _ready() -> void:
	super()
	Estado.marcar("nucleo_estrella")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	vacio.zona = Rect2(59 * 16, 34 * 16, 23 * 16, 15 * 16)
	add_child(vacio)
	_poner_escoria()
	_poner_cosas()
	if not Estado.tiene("nucleo_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


## La escoria («≈») no se pisa: un choque por cada tira de casillas seguidas
func _poner_escoria() -> void:
	var filas: PackedStringArray = $Region._filas
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Escoria"
	add_child(cuerpo)
	for y in filas.size():
		var x := 0
		while x < filas[y].length():
			if filas[y][x] != "≈":
				x += 1
				continue
			var x0 := x
			while x < filas[y].length() and filas[y][x] == "≈":
				x += 1
			var forma := CollisionShape2D.new()
			var caja := RectangleShape2D.new()
			caja.size = Vector2((x - x0) * 16.0 - 4.0, 16.0)
			forma.shape = caja
			forma.position = Vector2((x0 + x) * 8.0, y * 16.0 + 8.0)
			cuerpo.add_child(forma)


func _poner_cosas() -> void:
	if not Estado.tiene("asterhaul_libre"):
		var mauti: StaticBody2D = VECINO.new()
		mauti.id = "mauti"
		mauti.charla = "mauti_nucleo"
		mauti.position = _sitio(MAUTI)
		$Entidades.add_child(mauti)
	_leer("nucleo_atrio", _sitio(ESTELA))
	# 1. la Cámara Sísmica
	_poner_muro(MURO_SISMICO, "nucleo/muro", true)
	_poner_muro(DERRUMBE, "nucleo/derrumbe", false)
	var vagoneta: StaticBody2D = VAGONETA.new()
	vagoneta.position = _sitio(Vector2i(17, 38) if Estado.tiene("nucleo/derrumbe") else VAGONETA_C)
	$Entidades.add_child(vagoneta)
	var pilar: StaticBody2D = PILAR.new()
	pilar.marca = SELLOS[0]
	pilar.position = _sitio(PILAR_SELLO)
	$Entidades.add_child(pilar)
	for k in KAAS:
		var kaa: Node2D = KAA.new()
		kaa.position = _sitio(k)
		$Entidades.add_child(kaa)
	for c in COMPUERTAS:
		var compuerta: StaticBody2D = COMPUERTA.new()
		compuerta.marca = c[1]
		compuerta.position = _sitio(c[0])
		$Entidades.add_child(compuerta)
	# 2. la Cámara Magnética
	var barcaza: Node2D = BARCAZA.new()
	barcaza.name = "Barcaza"
	barcaza.muelle_a = MUELLES[0]
	barcaza.muelle_b = MUELLES[1]
	add_child(barcaza)
	var placa := Sprite2D.new()
	placa.texture = PLACA
	placa.hframes = 2
	placa.z_index = -3
	placa.frame = 1 if Estado.tiene(SELLOS[1]) else 0
	placa.position = _sitio(PLACA_C) + Vector2(0, -5)
	add_child(placa)
	var bloque: StaticBody2D = BLOQUE.new()
	bloque.placas.assign([PLACA_C])
	bloque.position = _sitio(PLACA_C if Estado.tiene(SELLOS[1]) else BLOQUE_C)
	$Entidades.add_child(bloque)
	bloque.parado.connect(func(c: Vector2i) -> void:
		if c == PLACA_C:
			placa.frame = 1
			Estado.marcar(SELLOS[1]))
	for k in KOVUS:
		var kovu: Node2D = KOVU.new()
		for c: Vector2i in k:
			kovu.nado.append(_sitio(c))
		kovu.position = _sitio(k[0])
		$Entidades.add_child(kovu)
	var puerta: StaticBody2D = PUERTA_TRIPLE.new()
	puerta.sellos = SELLOS
	puerta.marca = "nucleo/puerta_triple"
	puerta.position = _sitio(PUERTA_C) + Vector2(8, 0)
	$Entidades.add_child(puerta)
	puerta.abierta.connect(func() -> void: _hud.mostrar_mensaje("La Puerta Triple se abre"))
	# 3. la Cámara de la Resonancia
	for c in [MONOLITO_CORNISA, MONOLITO_PENA]:
		var m: StaticBody2D = MONOLITO.new()
		m.position = _sitio(c)
		$Entidades.add_child(m)
	var sello: StaticBody2D = MONOLITO.new()
	sello.position = _sitio(MONOLITO_SELLO)
	$Entidades.add_child(sello)
	sello.add_to_group("monolito_sello")
	sello.canta.connect(func(f: int) -> void:
		if f >= 3 and not Estado.tiene(SELLOS[2]):
			Estado.marcar(SELLOS[2]))
	var puente: Node2D = PUENTE.new()
	puente.casillas = PUENTE_C
	add_child(puente)
	for c in POPOS:
		var popo: Node2D = POPO.new()
		popo.position = _sitio(c)
		$Entidades.add_child(popo)
	# el Santuario
	for c in MONOLITOS_SANTUARIO:
		var m: StaticBody2D = MONOLITO.new()
		m.position = _sitio(c)
		$Entidades.add_child(m)
	_corazon = CORAZON.new()
	_corazon.centro = SANTUARIO
	_corazon.radios = RADIOS
	_corazon.position = SANTUARIO
	$Entidades.add_child(_corazon)
	if Estado.tiene("asterhaul_libre"):
		_corazon.vida = 0
		_corazon.calmar()
	else:
		_corazon.calmado.connect(_al_calmar)


func _poner_muro(casilla: Vector2i, marca: String, con_carga: bool) -> void:
	var muro: StaticBody2D = MURO.new()
	muro.marca = marca
	muro.con_carga = con_carga
	muro.dibujo = "desfiladero/muro" if con_carga else "desfiladero/derrumbe"
	muro.position = _sitio(casilla)
	$Entidades.add_child(muro)


func _leer(charla: String, donde: Vector2) -> void:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)


## Al entrar en el Santuario, despierta el Corazón; mientras pelean, la cámara se va hacia la mitad entre los dos
func _process(delta: float) -> void:
	var maisha := _maisha
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_corazon) and not Estado.tiene("corazon_calmado"):
		hacia = ((_corazon.global_position + Vector2(0, -30) - maisha.global_position) * 0.5).clamp(Vector2(-150, -86), Vector2(150, 86))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_corazon) or Estado.tiene("corazon_calmado"):
		return
	if ((maisha.global_position - SANTUARIO) / RADIOS).length() < 0.8:
		_despertando = true
		if not Estado.tiene("corazon_visto"):
			Estado.marcar("corazon_visto")
			await CHARLA_SCRIPT.hablar(self, "corazon_encuentro")
		if is_instance_valid(_corazon):
			_corazon.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


## El Corazón se calma: Mauti llega, se ve lo que guardaba y el Cetro del Nexo despierta del todo
func _al_calmar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica("asterhaul_libre", 1.5, "nucleo_estrella")
	var mauti: StaticBody2D = VECINO.new()
	mauti.id = "mauti"
	mauti.charla = "mauti_nucleo"
	mauti.position = SANTUARIO + Vector2(40, 60)
	$Entidades.add_child(mauti)
	if _maisha.global_position.distance_to(SANTUARIO) > 140.0:
		_maisha.global_position = SANTUARIO + Vector2(-30, 60)
	for charla in ["nucleo_final_semilla", "nucleo_final_mauti"]:
		await CHARLA_SCRIPT.hablar(self, charla)
	if not Estado.tiene("asterhaul_libre"):
		Estado.marcar("nexo_despierto")
		Estado.marcar("asterhaul_libre")
		Sonido.efecto("cetro_nexo", 2.0, _maisha.global_position)
		Impacto.fogonazo(Color(1.0, 0.92, 0.6), 0.8, 1.0)
	await CHARLA_SCRIPT.hablar(self, "nucleo_final_cetro")
	Estado.guardar_pronto()
	_mostrar_fin()


func _mostrar_fin() -> void:
	if Estado.tiene("fin_asterhaul_visto"):
		return
	Estado.marcar("fin_asterhaul_visto")
	var fin: CanvasLayer = FIN.new()
	fin.ilustracion = load("res://arte/historia/25_asterhaul_libre.png")
	fin.titulo = "Asterhaul late"
	fin.subtitulo = "Fin del tercer mundo"
	fin.pie = "Hacia el Valle del Ocaso..."
	fin.musica = "asterhaul_libre"
	var misiones := Misiones.hechas().size()
	var poderes := ["carga_sismica", "pulso_magnetico", "resonancia_ambar"].filter(func(s: String) -> bool: return Estado.tiene(s)).size()
	var cadenas := ["cadena_oeste_rota", "cadena_este_rota", "cadena_norte_rota"].filter(func(s: String) -> bool: return Estado.tiene(s)).size()
	fin.lineas_propias = [
		["Tiempo de juego", -1, -1, Estado.texto_tiempo(Estado.tiempo_jugado)],
		["Yunques de Memoria", YUNQUES.cuantos(), YUNQUES.ARTESANOS.size(), ""],
		["Cadenas del Cráter rotas", cadenas, 3, ""],
		["Poderes de la Tierra", poderes, 3, ""],
		["Misiones cumplidas", misiones, misiones + Misiones.activas().size(), ""],
		["Esencia", Artes.esencia_ganada_total(), -1, ""],
		["Cristales del Nexo", Tienda.cristales_ganados_total(), -1, ""],
	]
	add_child(fin)
	fin.abrir()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("nucleo_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "nucleo_llegada")
	Estado.marcar("nucleo_llegada")
