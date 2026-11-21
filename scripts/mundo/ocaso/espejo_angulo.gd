extends StaticBody2D
## UN ESPEJO DE ÁNGULO (el Jardín de los Faroles): una luna de bronce en diagonal que dobla un cuarto la luz que le
## llega (ocaso/luz_jardin.gd). Un golpe de cetro la cambia de «/» a «\». Si una POLILLA DE PAPEL se le posa encima
## (`tapado`), la tapa y la luz se para ahí. Su postura se guarda (`marca`, Estado.extra["espejos"]).
## Dibujo: arte/mundos/ocaso/jardin/espejo.png (0 «/» · 1 «\» · 2-3 con luz).

const DIBUJO := preload("res://arte/mundos/ocaso/jardin/espejo.png")

var casilla := Vector2i.ZERO
var barra := true                         # «/» (si no, «\»)
var marca := ""
var encendido := false
var tapado: Node = null                   # la polilla que lo tapa
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("opticas")
	add_to_group("espejos")
	if marca != "" and Estado.extra.get("espejos", {}).has(marca):
		barra = int(Estado.extra["espejos"][marca]) == 0
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -15)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func _process(_delta: float) -> void:
	_sprite.frame = (0 if barra else 1) + (2 if encendido and not is_instance_valid(tapado) else 0)


func ocupa(c: Vector2i) -> bool:
	return c == casilla


## «/»: este → norte, norte → este, oeste → sur, sur → oeste · «\»: este → sur, sur → este, ...
func desviar(d: Vector2i, color: int) -> Array:
	if is_instance_valid(tapado):
		return []
	return [[Vector2i(-d.y, -d.x) if barra else Vector2i(d.y, d.x), color]]


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if is_instance_valid(tapado):
		return false                      # (el golpe es para la polilla)
	barra = not barra
	if marca != "":
		var espejos: Dictionary = Estado.extra.get("espejos", {}).duplicate()
		espejos[marca] = 0 if barra else 1
		Estado.extra["espejos"] = espejos
		Estado.guardar_pronto()
	Sonido.efecto("espejo_gira", -2.0, global_position, 0.08)
	get_tree().call_group("luz_jardin", "cambiar")
	return true
