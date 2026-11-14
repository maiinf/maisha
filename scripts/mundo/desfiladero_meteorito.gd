extends "res://scripts/mundo/escena_mundo.gd"
## EL DESFILADERO DEL METEORITO (Asterhaul, el primer camino: al este del Kitovu): un cañón de roca ocre y ámbar,
## con las vías de los canteros. Lo que no es suelo es pared.
##   - LA ENTRADA (suroeste): una VAGONETA en su vía; lanzada, aparta el montón de rocas del final (un secreto).
##     Al norte, tras un MURO AGRIETADO, un rincón con la 2.ª ESQUIRLA DE ESTRELLA.
##   - EL TALLER DE MWAMBA (centro): MWAMBA, el viejo cantero (sigilia/escriba.gd, en gris hasta que se le devuelve
##     su ESQUIRLA, que está en la cantera). Con el pulso de vuelta enseña la CARGA SÍSMICA (I). La ESTELA se lee.
##     La vía larga tiene un ramal al norte que acaba en el DERRUMBE: detrás está MAUTI. Solo lo aparta la vagoneta.
##   - LA CANTERA HUNDIDA (sureste): los KAA-JIWE (enemigos/kaa_jiwe.gd; sin la Carga no se les puede hacer nada) y
##     la Esquirla de Mwamba. Al norte, tras otro muro, la inscripción de los primeros canteros (un secreto).
##   - LA PUERTA DEL CRÁTER (noreste), tras un muro agrietado: tres PILARES-DIAPASÓN; con los tres sonando, se abre.
##     Detrás está Mji-Jiwe (aún no construida).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const MURO := preload("res://scripts/mundo/asterhaul/muro_agrietado.gd")
const VAGONETA := preload("res://scripts/mundo/asterhaul/vagoneta.gd")
const PILAR := preload("res://scripts/mundo/asterhaul/pilar_diapason.gd")
const KAA := preload("res://scripts/enemigos/kaa_jiwe.gd")
const ARTE := "res://arte/mundos/asterhaul/desfiladero/"
## (todo en casillas)
const MWAMBA := Vector2i(47, 21)
const TALLER := Vector2i(39, 20)
const ESTELA := Vector2i(52, 19)
const MAUTI := Vector2i(30, 7)
## muro: [casilla, marca]
const MUROS := [[Vector2i(20, 34), "desfiladero/muro_secreto"], [Vector2i(66, 17), "desfiladero/muro_puerta"],
	[Vector2i(72, 35), "secreto/desfiladero_meteorito/72,35"]]
## derrumbe (solo lo aparta una vagoneta): [casilla, marca]
const DERRUMBES := [[Vector2i(30, 12), "desfiladero/derrumbe_mauti"], [Vector2i(25, 41), "secreto/desfiladero_meteorito/25,41"]]
## vagoneta: [dónde empieza, dónde queda si su derrumbe ya está apartado, la marca de ese derrumbe]
const VAGONETAS := [[Vector2i(46, 24), Vector2i(30, 14), "desfiladero/derrumbe_mauti"],
	[Vector2i(8, 41), Vector2i(23, 41), "secreto/desfiladero_meteorito/25,41"]]
## esquirla: [objeto, casilla, marca]
const ESQUIRLAS := [["esquirla_mwamba", Vector2i(73, 47), "esquirla/mwamba"], ["esquirla_estrella", Vector2i(20, 30), "esquirla/desfiladero"]]
const KAAS := [Vector2i(20, 47), Vector2i(58, 42), Vector2i(66, 50), Vector2i(54, 50), Vector2i(58, 9)]
const PILARES := [Vector2i(63, 7), Vector2i(66, 7), Vector2i(69, 7)]
const PUERTA := Vector2i(73, 8)
const INSCRIPCION := Vector2i(72, 30)

var _puerta: StaticBody2D
var _voz: Node2D


func _ready() -> void:
	super()
	Estado.marcar("desfiladero_meteorito")
	_poner_cosas()
	if not Estado.tiene("desfiladero_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	_poner_adorno("taller", TALLER, 84, 16)
	_poner_adorno("estela", ESTELA, 12, 6)
	_leer("estela_carga", _sitio(ESTELA) + Vector2(0, 6))
	_leer("desfiladero_inscripcion", _sitio(INSCRIPCION))
	var mwamba: StaticBody2D = ESCRIBA.new()
	mwamba.nombre = "mwamba"
	mwamba.dibujo = "mwamba"
	mwamba.sufijo_apagado = "_gris"
	mwamba.sufijo_marca = "_pulso"
	mwamba.position = _sitio(MWAMBA)
	$Entidades.add_child(mwamba)
	var mauti: StaticBody2D = VECINO.new()
	mauti.id = "mauti"
	mauti.charla = "mauti_desfiladero"
	mauti.position = _sitio(MAUTI)
	$Entidades.add_child(mauti)
	for m in MUROS:
		_poner_muro(m[0], m[1], true)
	for d in DERRUMBES:
		var derrumbe := _poner_muro(d[0], d[1], false)
		if d[1] == "desfiladero/derrumbe_mauti" and not Estado.tiene(d[1]):
			# mientras está el derrumbe, a Mauti se le oye detrás
			_voz = _leer("derrumbe_mauti", _sitio(d[0]) + Vector2(0, 18))
			derrumbe.roto.connect(_al_apartar_derrumbe)
	for v in VAGONETAS:
		var vagoneta: StaticBody2D = VAGONETA.new()
		vagoneta.position = _sitio(v[1] if Estado.tiene(v[2]) else v[0])
		$Entidades.add_child(vagoneta)
	for e in ESQUIRLAS:
		var esquirla: Node2D = RECOGIBLE.new()
		esquirla.objeto = e[0]
		esquirla.marca = e[2]
		esquirla.dibujo = ARTE + "esquirla.png"
		esquirla.color_halo = Color(1.0, 0.75, 0.3)
		esquirla.position = _sitio(e[1])
		$Entidades.add_child(esquirla)
	for k in KAAS:
		var kaa: Node2D = KAA.new()
		kaa.position = _sitio(k)
		$Entidades.add_child(kaa)
	for i in PILARES.size():
		var pilar: StaticBody2D = PILAR.new()
		pilar.marca = "desfiladero/pilar_%d" % (i + 1)
		pilar.position = _sitio(PILARES[i])
		$Entidades.add_child(pilar)
		pilar.sonando.connect(_al_sonar_pilar)
	_poner_puerta()


func _poner_muro(casilla: Vector2i, marca: String, con_carga: bool) -> StaticBody2D:
	var muro: StaticBody2D = MURO.new()
	muro.marca = marca
	muro.con_carga = con_carga
	muro.dibujo = "muro" if con_carga else "derrumbe"
	muro.position = _sitio(casilla)
	$Entidades.add_child(muro)
	return muro


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


## La Puerta del Cráter: cerrada no se pasa; se abre con los tres pilares sonando
func _poner_puerta() -> void:
	_puerta = _poner_adorno("puerta", PUERTA, 60, 10)
	(_puerta.get_child(0) as Sprite2D).hframes = 2
	_leer("puerta_crater", _sitio(PUERTA) + Vector2(0, 6))
	if Estado.tiene("puerta_crater_abierta"):
		_abrir_puerta()


func _abrir_puerta() -> void:
	(_puerta.get_child(0) as Sprite2D).frame = 1
	(_puerta.get_child(1) as CollisionShape2D).set_deferred("disabled", true)


func _al_sonar_pilar() -> void:
	var sonando := 0
	for i in PILARES.size():
		if Estado.tiene("desfiladero/pilar_%d" % (i + 1)):
			sonando += 1
	if sonando < PILARES.size():
		_hud.mostrar_mensaje("Pilares despiertos: %d de %d" % [sonando, PILARES.size()])
		return
	Estado.marcar("puerta_crater_abierta")
	await get_tree().create_timer(0.8).timeout
	if not is_inside_tree():
		return
	_abrir_puerta()
	Sonido.efecto("roca_romper", -4.0, _sitio(PUERTA))
	Sonido.efecto("arte_sube", -2.0, _sitio(PUERTA))
	Impacto.temblar(4.0, 0.6)
	_hud.mostrar_mensaje("La Puerta del Cráter se abre")


func _al_apartar_derrumbe() -> void:
	if is_instance_valid(_voz):
		_voz.queue_free()
	_hud.mostrar_mensaje("El derrumbe se viene abajo")


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "carga_sismica":
		_hud.mostrar_mensaje("Carga Sísmica (I): embiste hacia delante")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("desfiladero_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "desfiladero_llegada")
	Estado.marcar("desfiladero_llegada")
