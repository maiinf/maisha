extends StaticBody2D
## EDIFICIO DE LA ALDEA: en ruinas hasta que se reconstruye (marca «construido_<id>»).
## El dibujo tiene 2 fotogramas: 0 = en ruinas, 1 = reconstruido.
## En ruinas, al acercarse y pulsar Acción se lee su descripción (datos/dialogos/raiz.json, «ruina_<id>»).
## Reconstruido, si tiene interior, su puerta lleva dentro (como el Gran Árbol).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const POLVO := [Color("e2cea0"), Color("c9b07e"), Color("a57559")]

## Casas con interior: id -> [escena de dentro, dónde está la puerta respecto a la base]
const INTERIORES := {
	"casa_seta": ["casa_pino", Vector2(0, 4)],
	"taller": ["taller_corteza", Vector2(-6, 4)],
}

@export var id := ""
@export var textura: Texture2D
@export var colision := Vector2(40, 12)
@export var radio_interaccion := 30.0
@export var altura_bocadillo := 30.0

var _sprite: Sprite2D
var _puerta: Area2D
var _polvo: Array[Dictionary] = []
var _destellos: Array[Dictionary] = []


func _ready() -> void:
	add_to_group("edificios")
	add_to_group("interactuables")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", colision.x * 0.55)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = textura
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-textura.get_width() / 4, -textura.get_height() + 2)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = colision
	forma.shape = caja
	forma.position = Vector2(0, -colision.y / 2.0)
	add_child(forma)
	actualizar()
	Estado.marca_puesta.connect(_al_poner_marca)


func construido() -> bool:
	return Estado.tiene("construido_" + id)


func actualizar() -> void:
	_sprite.frame = 1 if construido() else 0
	if construido():
		remove_from_group("interactuables")
		_crear_puerta()


func _crear_puerta() -> void:
	if _puerta or not INTERIORES.has(id):
		return
	_puerta = PUERTA.new()
	_puerta.id = id
	_puerta.destino = INTERIORES[id][0]
	_puerta.destino_puerta = "salida"
	_puerta.salida = Vector2.DOWN
	_puerta.tam = Vector2(14, 8)
	_puerta.position = INTERIORES[id][1]
	add_child(_puerta)


func _al_poner_marca(marca: String) -> void:
	if marca == "construido_" + id:
		reconstruir()


## Se levanta delante de Maisha: tiembla, sale polvo, un destello y aparece reconstruido
func reconstruir() -> void:
	Sonido.efecto("construir")
	var azar := RandomNumberGenerator.new()
	var t := create_tween()
	for i in 8:
		t.tween_property(_sprite, "position:x", 1.0 if i % 2 == 0 else -1.0, 0.06)
	t.tween_callback(func() -> void:
		for i in 26:
			var a := azar.randf_range(PI, TAU)
			_polvo.append({"pos": Vector2(azar.randf_range(-colision.x / 2, colision.x / 2), azar.randf_range(-6, 0)),
				"vel": Vector2(cos(a) * azar.randf_range(10, 40), sin(a) * azar.randf_range(5, 25)),
				"color": POLVO[i % 3], "vida": 0.0})
		for i in 14:
			_destellos.append({"pos": Vector2(azar.randf_range(-colision.x / 2, colision.x / 2), -azar.randf_range(4, textura.get_height() - 8)),
				"vida": -azar.randf_range(0.0, 0.6)})
		_sprite.position.x = 0
		actualizar()
		_sprite.modulate = Color(2.2, 2.2, 1.9))
	t.tween_property(_sprite, "modulate", Color.WHITE, 0.6)


func _process(delta: float) -> void:
	if _polvo.is_empty() and _destellos.is_empty():
		return
	for p in _polvo:
		p["vida"] += delta
		p["pos"] += p["vel"] * delta
		p["vel"] *= 0.94
	_polvo = _polvo.filter(func(p: Dictionary) -> bool: return p["vida"] < 1.0)
	for d in _destellos:
		d["vida"] += delta
	_destellos = _destellos.filter(func(d: Dictionary) -> bool: return d["vida"] < 0.5)
	queue_redraw()


func _draw() -> void:
	for p in _polvo:
		draw_rect(Rect2(p["pos"].round(), Vector2(3, 2)), Color(p["color"], 1.0 - p["vida"]))
	for d in _destellos:
		if d["vida"] < 0.0:
			continue
		var q: Vector2 = d["pos"].round()
		var a: float = 1.0 - d["vida"] / 0.5
		draw_rect(Rect2(q, Vector2.ONE), Color(1, 0.97, 0.9, a))
		draw_rect(Rect2(q + Vector2(-1, 0), Vector2(3, 1)), Color(1, 0.95, 0.77, a * 0.6))
		draw_rect(Rect2(q + Vector2(0, -1), Vector2(1, 3)), Color(1, 0.95, 0.77, a * 0.6))


## Punto desde el que se habla: el frente del edificio
func punto_interaccion() -> Vector2:
	return global_position + Vector2(0, 4)


func interactuar() -> void:
	await CHARLA.hablar(self, "ruina_" + id)
