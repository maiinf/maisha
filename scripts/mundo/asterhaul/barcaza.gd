extends Node2D
## UNA BARCAZA DE HIERRO (Asterhaul, la Fundición de Escoria): una plancha de 3×3 casillas que flota en la escoria
## entre dos MUELLES (`muelle_a` y `muelle_b`: la esquina de arriba a la izquierda de cada hueco, en casillas).
## Las casillas de los dos huecos son suelo en el mapa; el hueco donde NO está la barcaza no se pisa (lo tapa un
## choque). Responde al PULSO MAGNÉTICO (está en «magneticos»):
##   - con Maisha ENCIMA: se despega del muelle y la lleva al otro lado;
##   - con Maisha en la orilla del hueco vacío: viene hacia ella.
## También la mueve un CABRESTANTE (asterhaul/cabrestante.gd → `cruzar()`): al cabo de un momento, sale hacia el
## otro lado (con Maisha, si se ha subido). Con `cerrojo` (una marca) no se mueve hasta que se tiene.
## Dibujo: arte/mundos/asterhaul/fundicion/barcaza.png.

signal llegada

const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/barcaza.png")
const LADO := 48.0
const VELOCIDAD := 46.0
const CERCA := 46.0                 # a cuánto del hueco vacío tiene que estar Maisha para llamarla

var muelle_a := Vector2i.ZERO
var muelle_b := Vector2i.ZERO
var cerrojo := ""
var en_b := false
var moviendose := false
var _lleva: Node2D = null
var _huecos: Array[CollisionShape2D] = []
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("magneticos")
	add_to_group("barcazas")
	z_index = -4
	var sprite := Sprite2D.new()
	sprite.texture = DIBUJO
	sprite.centered = false
	add_child(sprite)
	# los choques de los dos huecos (el de donde está la barcaza, apagado)
	var cuerpo := StaticBody2D.new()
	cuerpo.top_level = true
	add_child(cuerpo)
	for m in [muelle_a, muelle_b]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(LADO - 2, LADO - 2)
		forma.shape = caja
		forma.position = Vector2(m) * 16.0 + Vector2(LADO, LADO) / 2.0
		cuerpo.add_child(forma)
		_huecos.append(forma)
	global_position = _sitio(en_b)
	_tapar()


func _sitio(b: bool) -> Vector2:
	return Vector2(muelle_b if b else muelle_a) * 16.0


func _tapar() -> void:
	_huecos[0].set_deferred("disabled", not en_b and not moviendose)
	_huecos[1].set_deferred("disabled", en_b and not moviendose)


## ¿Está ese punto encima de la barcaza?
func encima(p: Vector2) -> bool:
	return Rect2(global_position, Vector2(LADO, LADO)).grow(-3.0).has_point(p)


func recibir_pulso(origen: Vector2) -> bool:
	if moviendose or (cerrojo != "" and not Estado.tiene(cerrojo)):
		return false
	if encima(origen):
		cruzar()
		return true
	# desde la orilla del hueco vacío: viene
	var vacio := Rect2(_sitio(not en_b), Vector2(LADO, LADO))
	if vacio.grow(CERCA).has_point(origen):
		cruzar()
		return true
	return false


## Sale hacia el otro muelle (y se lleva a Maisha si está encima)
func cruzar() -> void:
	if moviendose:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_lleva = maisha if maisha and encima(maisha.global_position) else null
	if _lleva:
		_lleva.set("puede_actuar", false)
	moviendose = true
	_tapar()
	Sonido.efecto("bloque_atraer", 0.0, global_position + Vector2(LADO, LADO) / 2.0)


func _process(delta: float) -> void:
	_tiempo += delta
	if not moviendose:
		return
	var meta := _sitio(not en_b)
	var antes := global_position
	global_position = global_position.move_toward(meta, VELOCIDAD * delta)
	if is_instance_valid(_lleva):
		_lleva.global_position += global_position - antes
	if global_position.distance_to(meta) > 0.1:
		return
	en_b = not en_b
	moviendose = false
	_tapar()
	if is_instance_valid(_lleva):
		_lleva.set("puede_actuar", true)
	_lleva = null
	Sonido.efecto("clinc", -4.0, global_position + Vector2(LADO, LADO) / 2.0)
	Impacto.temblar(1.0, 0.1)
	llegada.emit()
