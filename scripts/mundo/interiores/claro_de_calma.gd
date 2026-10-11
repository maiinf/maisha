extends "res://scripts/mundo/escena_mundo.gd"
## CLARO DE CALMA: el interior del Gran Árbol (como las casas de Pokémon en la Nintendo DS:
## al cruzar la puerta cambia la escena y se ve la habitación entera, rodeada de negro).
##   - el brote del Árbol de la Vida en el centro: aquí se medita (Árbol de la Vida, scripts/interfaz/arbol_vida.gd)
##   - la cama de hojas y los libros de Bibi
##   - al fondo, unas raíces cierran el paso a lo más hondo del árbol (el misterio del origen)

const FONDO := preload("res://arte/mundos/raiz/aldea/interior_claro.png")
const BROTE := preload("res://arte/mundos/raiz/aldea/brote_vida.png")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const COSA := preload("res://scripts/mundo/objetos/cosa.gd")
const BROTE_VIDA := preload("res://scripts/mundo/objetos/brote_vida.gd")
const LUZ := Color(1.0, 0.8, 0.45)

## Suelo de la habitación (elipse) y hueco de la salida, en píxeles del dibujo
const CENTRO := Vector2(176, 128)
const RADIOS := Vector2(152, 76)
const HUECO := 14.0

var _brote: Sprite2D
var _luces: Node2D
var _tiempo := 0.0


func _ready() -> void:
	var fondo := Sprite2D.new()
	fondo.texture = FONDO
	fondo.centered = false
	fondo.z_index = -10
	add_child(fondo)
	move_child(fondo, 0)
	_crear_paredes()
	_crear_muebles()
	_crear_luces()
	var salida: Area2D = PUERTA.new()
	salida.id = "salida"
	salida.destino = "cuna_de_musgo"
	salida.destino_puerta = "arbol"
	salida.salida = Vector2.UP
	salida.tam = Vector2(HUECO * 2, 10)
	salida.position = CENTRO + Vector2(0, RADIOS.y + 9)
	add_child(salida)
	super()


## La habitación se ve entera y quieta, centrada en la pantalla
func _crear_camara() -> void:
	var camara := Camera2D.new()
	camara.position = Vector2(FONDO.get_width(), FONDO.get_height()) / 2.0
	add_child(camara)
	camara.make_current()


func _crear_paredes() -> void:
	var paredes := StaticBody2D.new()
	paredes.name = "Paredes"
	add_child(paredes)
	var lados := 56
	for i in lados:
		var a := TAU * i / lados
		var b := TAU * (i + 1) / lados
		var p := CENTRO + Vector2(cos(a), sin(a)) * RADIOS
		var q := CENTRO + Vector2(cos(b), sin(b)) * RADIOS
		var medio := (p + q) / 2.0
		if medio.y > CENTRO.y and absf(medio.x - CENTRO.x) < HUECO + 2.0:
			continue          # el hueco de la salida
		_segmento(paredes, p, q)
	# las paredes del pasillo de salida
	for lado in [-1.0, 1.0]:
		var x: float = CENTRO.x + lado * HUECO
		_segmento(paredes, Vector2(x, CENTRO.y + RADIOS.y - 4), Vector2(x, CENTRO.y + RADIOS.y + 24))


func _segmento(cuerpo: StaticBody2D, p: Vector2, q: Vector2) -> void:
	var forma := CollisionShape2D.new()
	var segmento := SegmentShape2D.new()
	segmento.a = p
	segmento.b = q
	forma.shape = segmento
	cuerpo.add_child(forma)


func _caja(cuerpo: StaticBody2D, r: Rect2) -> void:
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = r.size
	forma.shape = caja
	forma.position = r.get_center()
	cuerpo.add_child(forma)


func _crear_muebles() -> void:
	var muebles := StaticBody2D.new()
	muebles.name = "Muebles"
	add_child(muebles)
	_caja(muebles, Rect2(44, 74, 52, 18))     # cama de hojas
	_caja(muebles, Rect2(103, 62, 18, 12))    # mesita
	_caja(muebles, Rect2(234, 56, 34, 12))    # estantería 1
	_caja(muebles, Rect2(274, 66, 34, 12))    # estantería 2
	_caja(muebles, Rect2(154, 40, 44, 14))    # raíces del fondo
	_caja(muebles, Rect2(CENTRO.x - 5, CENTRO.y - 3, 10, 5))   # brote
	# el brote del Árbol de la Vida (con orden de profundidad, para pasar por delante y por detrás)
	_brote = Sprite2D.new()
	_brote.texture = BROTE
	_brote.hframes = 4
	_brote.centered = false
	_brote.offset = Vector2(-10, -29)
	_brote.position = CENTRO + Vector2(0, 1)
	$Entidades.add_child(_brote)
	# cosas que se pueden mirar
	var brote: Node2D = BROTE_VIDA.new()
	brote.name = "BroteVida"
	brote.charla = "claro_brote"
	brote.position = CENTRO
	brote.radio_interaccion = 28.0
	brote.altura_bocadillo = 34.0
	add_child(brote)
	_cosa("claro_raices", Vector2(176, 62), 26.0, 34.0)
	_cosa("claro_libros", Vector2(270, 80), 34.0, 40.0)
	_cosa("claro_cama", Vector2(72, 98), 30.0, 22.0)


func _cosa(charla: String, pos: Vector2, radio: float, altura: float) -> void:
	var cosa: Node2D = COSA.new()
	cosa.charla = charla
	cosa.position = pos
	cosa.radio_interaccion = radio
	cosa.altura_bocadillo = altura
	add_child(cosa)


## Halos de luz cálida (mezcla aditiva) en los farolillos, el brote y la puerta
func _crear_luces() -> void:
	_luces = Node2D.new()
	_luces.z_index = 5
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luces.material = material
	_luces.draw.connect(_dibujar_luces)
	add_child(_luces)


func _process(delta: float) -> void:
	_tiempo += delta
	_brote.frame = int(_tiempo * 3.0) % 4
	_luces.queue_redraw()


func _dibujar_luces() -> void:
	var pulso := 0.5 + 0.5 * sin(_tiempo * 2.0)
	for f in [Vector2(36, 46), Vector2(160, 22), Vector2(196, 22), Vector2(318, 50)]:
		for i in 3:
			_luces.draw_circle(f, 6.0 + i * 6.0, Color(LUZ, 0.05))
	for i in 5:
		_luces.draw_circle(CENTRO + Vector2(0, -14), 8.0 + i * 8.0 + pulso * 3.0, Color(0.7, 1.0, 0.6, 0.035))
	for i in 3:
		_luces.draw_circle(CENTRO + Vector2(0, RADIOS.y + 8), 8.0 + i * 7.0, Color(LUZ, 0.05))
