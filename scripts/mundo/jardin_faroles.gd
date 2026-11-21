extends "res://scripts/mundo/escena_mundo.gd"
## EL JARDÍN DE LOS FAROLES (el Valle del Ocaso, el camino del este de Jioni). Patios entre setos altos, unidos por
## la LUZ (ocaso/luz_jardin.gd): el PRISMA SOLAR de la entrada echa un rayo dorado hacia el este, y hay que llevarlo
## con ESPEJOS DE ÁNGULO (ocaso/espejo_angulo.gd, un golpe los cambia de «/» a «\») y un PRISMA (ocaso/prisma.gd,
## saca un haz violeta por la cara que se le gire).
##   - LA PÉRGOLA (oeste): el Prisma Solar.
##   - EL CLAUSTRO DE LOS PRISMAS (centro): cuatro espejos y el prisma. Las POLILLAS DE PAPEL
##     (enemigos/polilla_papel.gd) tapan los espejos encendidos. La luz dorada abre la VERJA del Invernadero.
##   - EL PABELLÓN DEL TÉ (norte, secreto): tras una CELOSÍA ILUSORIA que deshace la luz violeta. Un farol.
##   - EL ESTANQUE DE LOS REFLEJOS (sur): dos pasarelas gemelas (ocaso/pasarela_espejo.gd); la luz violeta delata
##     la falsa. Un farol al final del muelle.
##   - EL INVERNADERO (este): MONDO (enemigos/mondo.gd) y cuatro espejos altos (ocaso/espejo_alto.gd).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const VACIO := preload("res://scripts/mundo/asterhaul/vacio.gd")
const LUZ := preload("res://scripts/mundo/ocaso/luz_jardin.gd")
const ESPEJO := preload("res://scripts/mundo/ocaso/espejo_angulo.gd")
const PRISMA := preload("res://scripts/mundo/ocaso/prisma.gd")
const BARRERA := preload("res://scripts/mundo/ocaso/barrera_luz.gd")
const PASARELA := preload("res://scripts/mundo/ocaso/pasarela_espejo.gd")
const ESPEJO_ALTO := preload("res://scripts/mundo/ocaso/espejo_alto.gd")
const POLILLA := preload("res://scripts/enemigos/polilla_papel.gd")
const JEFE := preload("res://scripts/enemigos/mondo.gd")
const ARTE := "res://arte/mundos/ocaso/jardin/"
## (todo en casillas)
const FUENTE := Vector2i(6, 27)
## espejo: [casilla, ¿empieza «/»?, marca] (la luz va: «/» · «/» · «\» · «\»)
const ESPEJOS := [[Vector2i(26, 27), false, "jardin_1"], [Vector2i(26, 19), false, "jardin_2"],
	[Vector2i(40, 19), true, "jardin_3"], [Vector2i(40, 27), true, "jardin_4"]]
const PRISMA_EN := Vector2i(33, 19)
const CELOSIA := Rect2i(31, 12, 4, 1)
const VERJA := Rect2i(46, 26, 1, 3)
## pasarela: [casillas, ¿falsa?]
const PASARELAS := [[Rect2i(25, 46, 20, 2), true], [Rect2i(25, 49, 20, 2), false]]
const FAROLES := [[Vector2i(38, 5), "farol/jardin_1"], [Vector2i(48, 50), "farol/jardin_2"]]
const POLILLAS := [Vector2i(24, 22), Vector2i(42, 23), Vector2i(33, 35)]
const LINTERNAS := [Vector2i(23, 17), Vector2i(43, 17), Vector2i(23, 37), Vector2i(43, 37), Vector2i(3, 23),
	Vector2i(13, 23), Vector2i(3, 31), Vector2i(13, 31), Vector2i(21, 43), Vector2i(35, 43), Vector2i(23, 3), Vector2i(43, 3)]
const ESPEJOS_ALTOS := [Vector2i(55, 20), Vector2i(68, 20), Vector2i(68, 35), Vector2i(55, 35)]
const INVERNADERO := Vector2(61.5, 27.5)
const INVERNADERO_RADIOS := Vector2(10.5, 11.5)

var luz: Node2D
var mondo: Node2D = null
var _despertando := false


func _ready() -> void:
	luz = LUZ.new()
	luz.name = "Luz"
	luz.fuentes = [[FUENTE, Vector2i.RIGHT]]
	super()
	add_child(luz)
	Estado.marcar("jardin_faroles")
	var vacio: Node = VACIO.new()
	vacio.name = "Vacio"
	vacio.hundir = true
	add_child(vacio)
	_poner_cosas()
	if not Estado.tiene("jardin_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _adorno(dibujo: String, donde: Vector2, caja := Vector2.ZERO) -> StaticBody2D:
	var cosa := StaticBody2D.new()
	cosa.position = donde
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cosa.add_child(sprite)
	if caja != Vector2.ZERO:
		var forma := CollisionShape2D.new()
		var r := RectangleShape2D.new()
		r.size = caja
		forma.shape = r
		forma.position = Vector2(0, -caja.y / 2.0)
		cosa.add_child(forma)
	$Entidades.add_child(cosa)
	return cosa


func _poner_cosas() -> void:
	_adorno("fuente", _sitio(FUENTE), Vector2(14, 6))
	_adorno("pergola", Vector2(18 * 16, 29 * 16))
	_adorno("pabellon", Vector2(27 * 16, 8 * 16), Vector2(84, 14))
	for c in LINTERNAS:
		_adorno("linterna", _sitio(c), Vector2(10, 5))
	for e in ESPEJOS:
		var espejo: StaticBody2D = ESPEJO.new()
		espejo.casilla = e[0]
		espejo.barra = e[1]
		espejo.marca = e[2]
		espejo.position = _sitio(e[0])
		$Entidades.add_child(espejo)
	var prisma: StaticBody2D = PRISMA.new()
	prisma.casilla = PRISMA_EN
	prisma.lado = 3
	prisma.marca = "jardin_prisma"
	prisma.position = _sitio(PRISMA_EN)
	$Entidades.add_child(prisma)
	var celosia: StaticBody2D = BARRERA.new()
	celosia.name = "Celosia"
	celosia.casillas = CELOSIA
	celosia.abre_con = 2
	celosia.marca = "jardin/celosia"
	celosia.dibujo = load(ARTE + "celosia.png")
	celosia.position = Vector2(33 * 16, 13 * 16)
	$Entidades.add_child(celosia)
	celosia.abierta.connect(func() -> void: _pensar("jardin_celosia"))
	var verja: StaticBody2D = BARRERA.new()
	verja.name = "Verja"
	verja.casillas = VERJA
	verja.abre_con = 1
	verja.marca = "jardin/verja"
	verja.dibujo = load(ARTE + "verja.png")
	verja.cuadros = 2
	verja.position = Vector2(46 * 16 + 8, 29 * 16)
	$Entidades.add_child(verja)
	verja.abierta.connect(func() -> void: _pensar("jardin_verja"))
	for p in PASARELAS:
		var pasarela: Node2D = PASARELA.new()
		pasarela.casillas = p[0]
		pasarela.falsa = p[1]
		pasarela.marca = "jardin/reflejo_delatado"
		add_child(pasarela)
	for f in FAROLES:
		var farol: Node2D = RECOGIBLE.new()
		farol.objeto = "farol_hora"
		farol.marca = f[1]
		farol.dibujo = "res://arte/mundos/ocaso/mirador/farol.png"
		farol.color_halo = Color(1.0, 0.75, 0.35)
		farol.position = _sitio(f[0])
		$Entidades.add_child(farol)
	for c in POLILLAS:
		var polilla: Node2D = POLILLA.new()
		polilla.position = _sitio(c)
		$Entidades.add_child(polilla)
	_leer("jardin_cartel", _sitio(Vector2i(11, 25)))
	var altos: Array = []
	for i in ESPEJOS_ALTOS.size():
		var alto: StaticBody2D = ESPEJO_ALTO.new()
		alto.position = _sitio(ESPEJOS_ALTOS[i])
		alto.apunta = _sitio(ESPEJOS_ALTOS[(i + 2) % 4]) + Vector2(0, 18)   # (hasta delante del de enfrente, en diagonal)
		$Entidades.add_child(alto)
		altos.append(alto)
	if not Estado.tiene("mondo_vencido"):
		mondo = JEFE.new()
		mondo.espejos = altos
		mondo.position = INVERNADERO * 16.0
		$Entidades.add_child(mondo)
		mondo.destruido.connect(_al_vencer_mondo)


func _leer(charla: String, donde: Vector2) -> Node2D:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)
	return lectura


func _pensar(charla: String) -> void:
	if Estado.tiene(charla):
		return
	Estado.marcar(charla)
	await get_tree().create_timer(0.8).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, charla)


func en_invernadero(p: Vector2) -> bool:
	return ((p - INVERNADERO * 16.0) / (INVERNADERO_RADIOS * 16.0)).length() < 0.75


## Al entrar en el Invernadero, despierta Mondo; al delatar la pasarela falsa, Maisha lo comenta
func _process(_delta: float) -> void:
	if not Estado.tiene("jardin_reflejo") and Estado.tiene("jardin/reflejo_delatado"):
		_pensar("jardin_reflejo")
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or _despertando or not is_instance_valid(mondo) or Estado.tiene("mondo_vencido"):
		return
	if en_invernadero(maisha.global_position):
		_despertando = true
		if not Estado.tiene("mondo_visto"):
			Estado.marcar("mondo_visto")
			await CHARLA_SCRIPT.hablar(self, "mondo_encuentro")
		if is_instance_valid(mondo):
			mondo.despertar()


func _al_vencer_mondo() -> void:
	await get_tree().create_timer(3.0).timeout
	if not is_inside_tree():
		return
	Sonido.musica(MUSICA_DE.get("jardin_faroles", "jioni"))
	await CHARLA_SCRIPT.hablar(self, "mondo_vencido")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("jardin_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "jardin_llegada")
	Estado.marcar("jardin_llegada")
