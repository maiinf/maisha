extends StaticBody2D
## UN CHARCO DE TINTA QUIETA (Sigilia): tinta negra helada que tapa una calle. Se derrite con el SIGILO DE FUEGO
## (está en «derretibles»: sigilo_fuego.gd llama a derretir()): con dos sigilos queda medio derretido y con el tercero
## desaparece. Dibujo charco.png: 0 entero, 1 medio derretido, 2 casi nada. Se guarda (marca «<marca>/<n>»).

signal derretido

const DIBUJO := preload("res://arte/mundos/sigilia/maandiko/charco.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const SIGILOS := 3

@export var marca := ""

var golpes := 0
var radio_interaccion := 30.0
var altura_bocadillo := 26.0
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	for n in SIGILOS:
		if marca != "" and Estado.tiene("%s/%d" % [marca, n + 1]):
			golpes = n + 1
	if golpes >= SIGILOS:
		queue_free()
		return
	add_to_group("derretibles")
	add_to_group("interactuables")
	add_to_group("charcos_tinta")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.centered = false
	_sprite.offset = Vector2(-24, -26)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(56, 14)
	_forma.shape = caja
	_forma.position = Vector2(0, -6)
	add_child(_forma)
	_poner()


func _poner() -> void:
	_sprite.frame = clampi(golpes, 0, 2)


func derretir() -> void:
	if golpes >= SIGILOS:
		return
	golpes += 1
	if marca != "":
		Estado.marcar("%s/%d" % [marca, golpes])
	Sonido.efecto("clinc", -4.0, global_position)
	var gotas: Node2D = ASTILLAS.new()
	gotas.cantidad = 8
	gotas.position = global_position + Vector2(0, -10)
	get_parent().add_child(gotas)
	if golpes >= SIGILOS:
		remove_from_group("derretibles")
		remove_from_group("interactuables")
		derretido.emit()
		var t := create_tween()
		t.tween_property(self, "modulate:a", 0.0, 0.5)
		t.tween_callback(queue_free)
		return
	_poner()


func interactuar() -> void:
	await CHARLA.hablar(self, "charco_tinta")
