extends "res://scripts/mundo/escena_mundo.gd"
## EL OBSERVATORIO DE LA AURORA (Sigilia, el tercer camino desde Maandiko, por el noroeste): terrazas de piedra
## colgadas en la noche, bajo la aurora. Lo que no es terraza es cielo: no se pisa.
##   - LA CÚPULA DE NYOTA (abajo): su casa-cúpula y NYOTA, la astrónoma (sigilia/escriba.gd con su dibujo), en blanco.
##     Su FICHA está en el rincón del sur, tras un tapón de Tinta Quieta, y la ronda un Saa al que aún no se puede
##     parar. Con su nombre, enseña el SIGILO DE RAYO. La ESTELA («ȩ») se lee.
##   - LAS BOBINAS ASTRALES (sigilia/bobina.gd): el rayo las enciende un rato. LOS PUENTES DE CONSTELACIÓN
##     (sigilia/puente_constelacion.gd) se tienden cuando todas sus bobinas están encendidas a la vez: el primero
##     pide una; los del Claustro, dos antes de que se apaguen.
##   - LA GALERÍA DEL SOLSTICIO (oeste): la 2.ª FICHA (la de Darubini, una escriba de Maandiko) y una BOBINA MAYOR
##     en la isleta de un estanque de tinta (se llega con el Sigilo de Hielo; aquí la tinta no corre).
##   - LA GALERÍA DE LAS CAMPANAS (este): la otra BOBINA MAYOR, en un rincón tapado por Tinta Quieta (Sigilo de Fuego).
##     Con las dos mayores encendidas se tiende el puente del norte.
##   - SAA, el autómata de relojería (enemigos/saa.gd), de ronda por las terrazas.
##   - KENGELE, la Gran Campana Muda (enemigos/kengele.gd), en la GRAN CÚPULA, con sus cuatro DIAPASONES: despierta
##     al entrar. Suelta la 3.ª ficha (la de Mlinzi).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const BOBINA := preload("res://scripts/mundo/sigilia/bobina.gd")
const PUENTE := preload("res://scripts/mundo/sigilia/puente_constelacion.gd")
const SAA := preload("res://scripts/enemigos/saa.gd")
const KENGELE := preload("res://scripts/enemigos/kengele.gd")
const ARTE := "res://arte/mundos/sigilia/observatorio/"
## (todo en casillas)
const NYOTA := Vector2i(33, 68)
const CASA := Vector2i(27, 66)
const CHARCOS := [Vector2i(46, 74), Vector2i(63, 36)]
## ficha: [objeto, casilla]
const FICHAS := [["ficha_nyota", Vector2i(46, 77)], ["ficha_darubini", Vector2i(4, 40)]]
## puente: [nombre, casillas, bobinas ([casilla, marca])]
const PUENTES := [
	["sur", Rect2i(35, 55, 3, 5), [[Vector2i(38, 61), ""]]],
	["oeste", Rect2i(20, 45, 6, 3), [[Vector2i(28, 43), ""], [Vector2i(28, 49), ""]]],
	["este", Rect2i(47, 45, 6, 3), [[Vector2i(44, 43), ""], [Vector2i(44, 49), ""]]],
	["norte", Rect2i(35, 32, 3, 6), [[Vector2i(11, 46), "observatorio/mayor_oeste"], [Vector2i(63, 33), "observatorio/mayor_este"]]],
]
## Saa: [su puesto, su ronda]
const SAAS := [
	[Vector2i(46, 70), [Vector2i(41, 70), Vector2i(51, 70)]],
	[Vector2i(36, 46), [Vector2i(31, 46), Vector2i(41, 46)]],
	[Vector2i(4, 46), [Vector2i(4, 42), Vector2i(4, 52)]],
	[Vector2i(61, 46), [Vector2i(56, 44), Vector2i(66, 44), Vector2i(66, 50), Vector2i(56, 50)]],
]
## adorno: [dibujo, casilla, ancho de su caja]
const ADORNOS := [
	["telescopio", Vector2i(22, 61), 14], ["telescopio", Vector2i(50, 61), 14], ["telescopio", Vector2i(27, 39), 14],
	["telescopio", Vector2i(45, 39), 14], ["telescopio", Vector2i(18, 39), 14], ["telescopio", Vector2i(27, 53), 14],
	["campanas", Vector2i(56, 40), 40], ["campanas", Vector2i(66, 40), 40], ["campanas", Vector2i(56, 53), 40],
]
## la Gran Cúpula: su centro (en casillas), sus semiejes (px) y sus diapasones
const CUPULA := Vector2(36, 19)
const RADIOS := Vector2(248, 184)
const DIAPASONES := [Vector2i(26, 13), Vector2i(46, 13), Vector2i(26, 25), Vector2i(46, 25)]

var _kengele: Node2D = null
var _despertando := false


func _ready() -> void:
	super()
	Estado.marcar("observatorio_aurora")
	_poner_cosas()
	if not Estado.tiene("observatorio_llegada"):
		_pensar_al_llegar.call_deferred()


## En los estanques del Observatorio la tinta está quieta (lo preguntan las placas de hielo)
func corriente_en(_p: Vector2) -> Vector2:
	return Vector2.ZERO


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] == "ȩ":
				var estela: Node2D = LECTURA.new()
				estela.charla = "observatorio_estela"
				estela.position = _sitio(Vector2i(x, y)) + Vector2(0, 6)
				$Entidades.add_child(estela)
	_poner_adorno("cupula_nyota", CASA, 64, 20)
	for a in ADORNOS:
		_poner_adorno(a[0], a[1], a[2], 6)
	var nyota: StaticBody2D = ESCRIBA.new()
	nyota.nombre = "nyota"
	nyota.dibujo = "nyota"
	nyota.position = _sitio(NYOTA)
	$Entidades.add_child(nyota)
	for c in CHARCOS:
		var ch: StaticBody2D = CHARCO.new()
		ch.marca = "charco/observatorio/%d,%d" % [c.x, c.y]
		ch.position = _sitio(c)
		$Entidades.add_child(ch)
	for f in FICHAS:
		var ficha: Node2D = RECOGIBLE.new()
		ficha.objeto = f[0]
		ficha.marca = "ficha/" + String(f[0]).trim_prefix("ficha_")
		ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
		ficha.color_halo = Color(0.85, 0.7, 1.0)
		ficha.position = _sitio(f[1])
		$Entidades.add_child(ficha)
	for p in PUENTES:
		var puente: Node2D = PUENTE.new()
		puente.casillas = p[1]
		puente.marca = "observatorio/puente_" + p[0]
		for b in p[2]:
			var bobina: StaticBody2D = BOBINA.new()
			bobina.marca = b[1]
			bobina.position = _sitio(b[0])
			$Entidades.add_child(bobina)
			puente.bobinas.append(bobina)
		add_child(puente)
		puente.tendido.connect(_al_tender_puente.bind(p[0]))
	for s in SAAS:
		var saa: Node2D = SAA.new()
		saa.position = _sitio(s[0])
		for r: Vector2i in s[1]:
			saa.ronda.append(_sitio(r))
		$Entidades.add_child(saa)
	for d in DIAPASONES:
		var diapason: StaticBody2D = BOBINA.new()
		diapason.dibujo = "diapason"
		diapason.dura = 6.0
		diapason.position = _sitio(d)
		$Entidades.add_child(diapason)
		diapason.add_to_group("diapasones")
	if not Estado.tiene("kengele_vencida"):
		_kengele = KENGELE.new()
		_kengele.centro = CUPULA * 16.0 + Vector2(8, 8)
		_kengele.radios = RADIOS
		_kengele.position = _kengele.centro
		$Entidades.add_child(_kengele)
		_kengele.destruido.connect(_al_vencer_kengele)


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


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "sigilo_rayo":
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Sigilo de Rayo (R para cambiar)")


func _al_tender_puente(cual: String) -> void:
	_hud.mostrar_mensaje("El camino a la Gran Cúpula está tendido" if cual == "norte" else "Un Puente de Constelación se enciende")


## Al entrar en la Gran Cúpula, despierta Kengele. Mientras pelean, la cámara se va hacia la mitad entre Maisha y
## la campana, para que se vean las dos.
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_kengele) and not Estado.tiene("kengele_vencida"):
		hacia = ((_kengele.global_position + Vector2(0, -30) - maisha.global_position) * 0.5).clamp(Vector2(-160, -90), Vector2(160, 90))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_kengele) or Estado.tiene("kengele_vencida"):
		return
	var d := (maisha.global_position - (CUPULA * 16.0 + Vector2(8, 8))) / RADIOS
	if d.length() < 0.82:
		_despertando = true
		if not Estado.tiene("kengele_vista"):
			Estado.marcar("kengele_vista")
			await CHARLA_SCRIPT.hablar(self, "kengele_encuentro")
		if is_instance_valid(_kengele):
			_kengele.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


func _al_vencer_kengele() -> void:
	await get_tree().create_timer(3.0).timeout
	if is_inside_tree():
		Sonido.musica("observatorio_aurora")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("observatorio_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "observatorio_llegada")
	Estado.marcar("observatorio_llegada")
