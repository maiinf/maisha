extends StaticBody2D
## UN PRISMA DE CRISTAL (el Jardín de los Faroles): la luz DORADA que le entra sigue recta y, además, sale un haz
## VIOLETA por su cara de color (`lado`: 0 norte · 1 este · 2 sur · 3 oeste; nunca hacia atrás). La luz violeta pasa
## sin partirse. Un golpe de cetro lo gira un cuarto. Su cara se guarda (`marca`, Estado.extra["espejos"]).
## Dibujo: arte/mundos/ocaso/jardin/prisma.png (0-3 la cara violeta · 4-7 con luz).

const DIBUJO := preload("res://arte/mundos/ocaso/jardin/prisma.png")
const LADOS := [Vector2i.UP, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT]

var casilla := Vector2i.ZERO
var lado := 0
var marca := ""
var encendido := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("opticas")
	add_to_group("prismas")
	if marca != "":
		lado = int(Estado.extra.get("espejos", {}).get(marca, lado)) % 4
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 8
	_sprite.offset = Vector2(0, -14)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func _process(_delta: float) -> void:
	_sprite.frame = lado + (4 if encendido else 0)


func ocupa(c: Vector2i) -> bool:
	return c == casilla


func desviar(d: Vector2i, color: int) -> Array:
	var salen: Array = [[d, color]]
	var cara: Vector2i = LADOS[lado]
	if color == 1 and cara != -d and cara != d:            # (1: dorado)
		salen.append([cara, 2])
	return salen


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	lado = (lado + 1) % 4
	if marca != "":
		var espejos: Dictionary = Estado.extra.get("espejos", {}).duplicate()
		espejos[marca] = lado
		Estado.extra["espejos"] = espejos
		Estado.guardar_pronto()
	Sonido.efecto("prisma_gira", -2.0, global_position, 0.08)
	get_tree().call_group("luz_jardin", "cambiar")
	return true
