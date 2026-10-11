extends "res://scripts/mundo/escena_mundo.gd"
## INTERIOR DE UNA CASA: habitación rectangular vista desde arriba, centrada en la pantalla y
## rodeada de negro (como las casas de Pokémon en la Nintendo DS).
## El dibujo de la habitación sale de herramientas/dibujar_aldea.py, con estas medidas:
##   suelo que se pisa: de (32, 72) a (288, 184) · hueco de la puerta: x de 148 a 172, abajo.
## Cada casa (casa_pino.gd, taller_corteza.gd) pone su dibujo, sus muebles y lo que se puede mirar.

const PUERTA := preload("res://scripts/mundo/puerta.gd")
const COSA := preload("res://scripts/mundo/objetos/cosa.gd")
const SUELO := Rect2(32, 72, 256, 112)
const HUECO := Vector2(148, 172)

## Escena de fuera y puerta por la que se vuelve a ella
@export var exterior := "cuna_de_musgo"
@export var puerta_exterior := ""

var _luces: Node2D
var _tiempo := 0.0


func _ready() -> void:
	var fondo := Sprite2D.new()
	fondo.texture = _fondo()
	fondo.centered = false
	fondo.z_index = -10
	add_child(fondo)
	move_child(fondo, 0)
	var paredes := StaticBody2D.new()
	paredes.name = "Paredes"
	add_child(paredes)
	_caja(paredes, Rect2(0, 0, 320, SUELO.position.y + 4))                       # fondo
	_caja(paredes, Rect2(0, 0, SUELO.position.x + 4, 208))                       # izquierda
	_caja(paredes, Rect2(SUELO.end.x - 4, 0, 40, 208))                           # derecha
	_caja(paredes, Rect2(0, SUELO.end.y, HUECO.x, 30))                           # delante, a la izquierda
	_caja(paredes, Rect2(HUECO.y, SUELO.end.y, 320 - HUECO.y, 30))               # delante, a la derecha
	var muebles := StaticBody2D.new()
	muebles.name = "Muebles"
	add_child(muebles)
	for r in _muebles():
		_caja(muebles, r)
	for cosa in _cosas():
		_cosa(cosa[0], cosa[1], cosa[2], cosa[3])
	var salida: Area2D = PUERTA.new()
	salida.id = "salida"
	salida.destino = exterior
	salida.destino_puerta = puerta_exterior
	salida.salida = Vector2.UP
	salida.tam = Vector2(HUECO.y - HUECO.x, 10)
	salida.position = Vector2((HUECO.x + HUECO.y) / 2.0, SUELO.end.y + 12)
	add_child(salida)
	_luces = Node2D.new()
	_luces.z_index = 5
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luces.material = material
	_luces.draw.connect(_dibujar_luces)
	add_child(_luces)
	_preparar()
	super()


# --- Lo que cambia en cada casa ------------------------------------------------------

func _fondo() -> Texture2D:
	return null


## Rectángulos que no se pueden pisar (camas, mesas...)
func _muebles() -> Array[Rect2]:
	return []


## Cosas que se pueden mirar: [charla, posición, radio, altura del bocadillo]
func _cosas() -> Array:
	return []


## Para añadir lo que haga falta (aldeanos, sprites con profundidad...)
func _preparar() -> void:
	pass


## Halos de luz de la habitación
func _dibujar_luces() -> void:
	for i in 3:
		_luces.draw_circle(Vector2(160, SUELO.end.y + 8), 8.0 + i * 7.0, Color(1.0, 0.8, 0.45, 0.05))


# --- Comunes --------------------------------------------------------------------------

func _crear_camara() -> void:
	var camara := Camera2D.new()
	camara.position = Vector2(160, 104)
	add_child(camara)
	camara.make_current()


func _process(delta: float) -> void:
	_tiempo += delta
	_luces.queue_redraw()


func _caja(cuerpo: StaticBody2D, r: Rect2) -> void:
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = r.size
	forma.shape = caja
	forma.position = r.get_center()
	cuerpo.add_child(forma)


func _cosa(charla: String, pos: Vector2, radio: float, altura: float) -> void:
	var cosa: Node2D = COSA.new()
	cosa.charla = charla
	cosa.position = pos
	cosa.radio_interaccion = radio
	cosa.altura_bocadillo = altura
	add_child(cosa)
