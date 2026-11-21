extends "res://scripts/mundo/escena_mundo.gd"
## JIONI, LA CIUDAD DE LOS FAROLES (el Valle del Ocaso, la ciudad del centro). Desde que se paró el sol nadie duerme:
## los fénec (mbweha) están DESVELADOS, con ojeras, repitiendo su faena sin parar.
##   - LA PLAZA DE LOS DOCE FAROLES: doce postes en corro (ocaso/poste_farol.gd). Cada Farol de la Hora colgado
##     devuelve una hora a la ciudad: un vecino, por fin, descansa (`ORDEN`: el primero que falte), abre las
##     cortinas o su puesto y habla de otra manera. En el centro, KIBATARI, el aprendiz de Mwanga.
##   - LA TORRE DEL RELOJ DE ARENA (norte): ata el sol con tres cadenas (se lee).
##   - EL BARRIO DE LAS CORTINAS (oeste) y EL MERCADO DEL CREPÚSCULO (este): las casas y los puestos de los vecinos.
##   - Las salidas: las Dunas de Penumbra (oeste), el Jardín de los Faroles (este), la Calzada de los Obeliscos
##     (sureste) y la PUERTA DEL HORIZONTE (sur), sellada hasta tener los tres pesos del reloj (`tres_pesos`).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const POSTE := preload("res://scripts/mundo/ocaso/poste_farol.gd")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const ARTE := "res://arte/mundos/ocaso/jioni/"
## (todo en casillas)
const PLAZA := Vector2(32.0, 22.0)
const KIBATARI := Vector2i(32, 22)
const TORRE := Vector2i(40, 13)
## en qué orden descansan los vecinos, uno por farol colgado
const ORDEN := ["kikombe", "kesho", "mto", "pazia", "ufagio", "ndoto"]
## vecino: [dónde está, su casa o su puesto ("casa"/"puesto"), dónde está ella]
const VECINOS := {
	"kesho": [Vector2i(11, 17), "casa", Vector2i(9, 15)],
	"mto": [Vector2i(19, 17), "casa", Vector2i(17, 15)],
	"ndoto": [Vector2i(11, 34), "casa", Vector2i(9, 32)],
	"pazia": [Vector2i(19, 34), "casa", Vector2i(17, 32)],
	"kikombe": [Vector2i(46, 19), "puesto", Vector2i(46, 17)],
	"ufagio": [Vector2i(24, 26), "", Vector2i.ZERO],
}
## los puestos del Mercado que aún no tienen dueño (la tienda, más adelante)
const PUESTOS_CERRADOS := [Vector2i(52, 17), Vector2i(56, 22)]
## salida: [id, destino, casilla, hacia dónde sale Maisha al volver, tamaño, marca que la abre]
const SALIDAS := [["dunas", "dunas_penumbra", Vector2i(1, 21), Vector2.RIGHT, Vector2(12, 48), ""],
	["jardin", "jardin_faroles", Vector2i(62, 27), Vector2.LEFT, Vector2(12, 48), ""],
	["calzada", "calzada_obeliscos", Vector2i(54, 42), Vector2.UP, Vector2(64, 12), ""],
	["horizonte", "horizonte_inmovil", Vector2i(31, 42), Vector2.UP, Vector2(48, 12), "tres_pesos"]]
const HORIZONTE := Vector2i(31, 40)

var _vecinos := {}                       # nombre → su nodo
var _casas := {}                         # nombre → el sprite de su casa o su puesto


func _ready() -> void:
	# las tres pesas del reloj abren la Puerta del Horizonte
	if Estado.tiene("peso_oeste") and Estado.tiene("peso_este") and Estado.tiene("peso_sur"):
		Estado.marcar("tres_pesos")
	# (antes de super(): al volver por una de ellas, la puerta tiene que estar ya)
	for s in SALIDAS:
		var puerta: Area2D = PUERTA.new()
		puerta.id = s[0]
		puerta.destino = s[1]
		puerta.destino_puerta = "jioni"
		puerta.salida = s[3]
		puerta.tam = s[4]
		puerta.cerrada_hasta = s[5]
		puerta.position = _sitio(s[2]) + (Vector2(8, -6) if s[0] == "horizonte" else Vector2(0, -6))
		add_child(puerta)
		puerta.cerrada.connect(func() -> void: CHARLA_SCRIPT.hablar(self, "jioni_salida_" + String(s[0])))
	super()
	Estado.marcar("jioni")
	_poner_cosas()
	if Estado.tiene("ocaso_libre"):
		_anochecer()
	if not Estado.tiene("jioni_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


static func descansa(nombre: String) -> bool:
	return Estado.tiene("jioni/descansa_" + nombre)


func _poner_cosas() -> void:
	var torre := _poner_adorno("torre", TORRE, 72, 18)
	torre.add_to_group("torres")
	_leer("jioni_torre", _sitio(TORRE) + Vector2(0, 6))
	var horizonte := _poner_adorno("horizonte", HORIZONTE, 0, 0)
	horizonte.position.x += 8
	for x in [-34.0, 34.0]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(12, 8)
		forma.shape = caja
		forma.position = Vector2(x, -4)
		horizonte.add_child(forma)
	for k in 12:
		var a := -PI / 2.0 + k * PI / 6.0
		var poste: StaticBody2D = POSTE.new()
		poste.marca = POSTE.PREFIJO + "%02d" % k
		poste.position = PLAZA * 16.0 + Vector2(8, 8) + Vector2(cos(a) * 120.0, sin(a) * 80.0)
		$Entidades.add_child(poste)
		poste.colgado.connect(_al_colgar_farol)
	var kibatari: StaticBody2D = VECINO.new()
	kibatari.id = "kibatari"
	kibatari.charla = "kibatari"
	kibatari.position = _sitio(KIBATARI)
	$Entidades.add_child(kibatari)
	for p in PUESTOS_CERRADOS:
		var puesto := _poner_adorno("puesto", p, 52, 12)
		(puesto.get_child(0) as Sprite2D).hframes = 2
	for nombre: String in VECINOS:
		var v: Array = VECINOS[nombre]
		if v[1] != "":
			var cosa := _poner_adorno(v[1], v[2], 56 if v[1] == "casa" else 52, 14)
			var sprite := cosa.get_child(0) as Sprite2D
			sprite.hframes = 2
			sprite.frame = 1 if descansa(nombre) else 0
			_casas[nombre] = sprite
		_poner_vecino(nombre)


func _poner_vecino(nombre: String) -> void:
	var vecino: StaticBody2D = VECINO.new()
	vecino.id = nombre if descansa(nombre) else nombre + "_desvelado"
	vecino.charla = "jioni_" + nombre
	vecino.position = _sitio(VECINOS[nombre][0])
	vecino.add_to_group("vecinos_jioni")
	$Entidades.add_child(vecino)
	_vecinos[nombre] = vecino


## Un farol más en la plaza: descansa el siguiente vecino (con un fundido: se va el desvelado y llega descansado)
func _al_colgar_farol() -> void:
	var n := POSTE.colgados()
	if n >= 12:
		Estado.marcar("jioni/doce_faroles")             # (Kibatari da la Bendición del Crepúsculo)
	_hud.mostrar_mensaje("Faroles de la Hora: %d de 12" % n)
	for nombre: String in ORDEN:
		if descansa(nombre):
			continue
		Estado.marcar("jioni/descansa_" + nombre)
		var viejo: Node2D = _vecinos[nombre]
		Sonido.efecto("vecino_descansa", -1.5, viejo.global_position)
		var t := create_tween()
		t.tween_property(viejo, "modulate:a", 0.0, 0.5)
		t.tween_callback(func() -> void:
			viejo.queue_free()
			_poner_vecino(nombre)
			if _casas.has(nombre):
				(_casas[nombre] as Sprite2D).frame = 1)
		break


func _leer(charla: String, donde: Vector2) -> Node2D:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)
	return lectura


## Un adorno que no se atraviesa: su dibujo de pie y una caja en la base (sin caja si ancho es 0)
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fondo: float) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = _sitio(casilla)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cuerpo.add_child(sprite)
	if ancho > 0.0:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(ancho, fondo)
		forma.shape = caja
		forma.position = Vector2(0, -fondo / 2.0)
		cuerpo.add_child(forma)
	$Entidades.add_child(cuerpo)
	return cuerpo


## Después del final, en Jioni es de noche: azul oscuro, los faroles de la plaza y las ventanas encendidas, y la
## ciudad duerme (lo que dicen los vecinos lo cambian sus conversaciones, con «ocaso_libre»). Una penumbra propia
## (CanvasModulate «Noche»): el relieve aparta su ciclo de día mientras está.
func _anochecer() -> void:
	var noche := CanvasModulate.new()
	noche.name = "Noche"
	noche.color = Color(0.36, 0.38, 0.62)
	add_child(noche)
	var luz := PointLight2D.new()
	luz.texture = preload("res://scripts/mundo/relieve.gd").textura_luz(128)
	luz.color = Color(0.85, 0.88, 1.0)
	luz.energy = 0.55
	luz.position = Vector2(0, -10)
	_maisha.add_child(luz)
	for nombre: String in _casas:
		var ventana := PointLight2D.new()
		ventana.texture = luz.texture
		ventana.color = Color(1.0, 0.72, 0.4)
		ventana.energy = 0.45
		ventana.texture_scale = 0.6
		ventana.position = Vector2(0, -18)
		(_casas[nombre] as Node2D).add_child(ventana)


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("jioni_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "jioni_llegada")
	Estado.marcar("jioni_llegada")
