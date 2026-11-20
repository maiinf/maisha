extends StaticBody2D
## UN ESPEJO DE BRONCE (el Valle del Ocaso): un golpe de cetro lo gira un cuarto (norte → este → sur → oeste).
## Se enciende (`encendido`) cuando mira hacia su luz: el sol, si `mira_al_sol`, o un espejo ya encendido (`fuente`)
## que esté en esa dirección. La escena decide qué hacer con eso. Su posición se guarda (`marca`, Estado.extra).
## Dibujo: arte/mundos/ocaso/mirador/espejo.png (0-3 apagado norte/este/sur/oeste · 4-7 encendido).

signal girado

const DIBUJO := preload("res://arte/mundos/ocaso/mirador/espejo.png")
const DIRECCION := [Vector2.UP, Vector2.RIGHT, Vector2.DOWN, Vector2.LEFT]
## hacia dónde tiene que mirar para ver el sol en cada hora (oeste, sur, este)
const AL_SOL := [3, 2, 1]

var marca := ""
var lado := 0
var mira_al_sol := false
var fuente: Node2D = null
var encendido := false
var _sprite: Sprite2D
var _sol: Node


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("espejos")
	if marca != "":
		lado = int(Estado.extra.get("espejos", {}).get(marca, lado)) % 4
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 8
	_sprite.offset = Vector2(0, -17)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(10, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_sol = get_tree().get_first_node_in_group("sol")
	_sol.cambiada.connect(func(_h: int) -> void: comprobar())
	comprobar()


func comprobar() -> void:
	if mira_al_sol:
		encendido = lado == AL_SOL[_sol.hora]
	elif fuente != null:
		var hacia := (fuente.global_position - global_position).normalized()
		encendido = fuente.get("encendido") and DIRECCION[lado].dot(hacia) > 0.9
	_sprite.frame = lado + (4 if encendido else 0)


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	lado = (lado + 1) % 4
	if marca != "":
		var espejos: Dictionary = Estado.extra.get("espejos", {}).duplicate()
		espejos[marca] = lado
		Estado.extra["espejos"] = espejos
		Estado.guardar_pronto()
	Sonido.efecto("aguja_cambiar", -3.0, global_position, 0.2)
	for e in get_tree().get_nodes_in_group("espejos"):
		e.comprobar()                       # (primero el que mira al sol: va antes en el árbol)
	girado.emit()
	return true
