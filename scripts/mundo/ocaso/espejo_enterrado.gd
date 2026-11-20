extends "res://scripts/mundo/ocaso/espejo.gd"
## UN ESPEJO SEMIENTERRADO (las Dunas de Penumbra): un espejo de bronce (ocaso/espejo.gd) que la arena ha tapado.
## Mientras está enterrado solo asoma el borde: el cetro no lo mueve. Una CARGA SÍSMICA lo saca de la arena
## (`marca_fuera`), y desde entonces es un espejo como los del Mirador.
## Dibujo enterrado: arte/mundos/ocaso/dunas/enterrado.png.

const ENTERRADO := preload("res://arte/mundos/ocaso/dunas/enterrado.png")

var marca_fuera := ""
var radio_carga := 10.0
var _arena: Sprite2D


func _ready() -> void:
	super()
	if not Estado.tiene(marca_fuera):
		add_to_group("sismicos")
		_sprite.visible = false
		_arena = Sprite2D.new()
		_arena.texture = ENTERRADO
		_arena.offset = Vector2(0, -9)
		add_child(_arena)


func enterrado() -> bool:
	return not Estado.tiene(marca_fuera)


func comprobar() -> void:
	if enterrado():
		encendido = false
		return
	super()


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if enterrado():
		return false
	return super(danio, direccion)


func recibir_carga(_direccion: Vector2) -> bool:
	if not enterrado():
		return false
	Estado.marcar(marca_fuera)
	remove_from_group("sismicos")
	if _arena:
		_arena.queue_free()
	_sprite.visible = true
	Sonido.efecto("roca_romper", -4.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -8), Vector2.UP, Color("c8a4b8"))
	for e in get_tree().get_nodes_in_group("espejos"):
		e.comprobar()
	girado.emit()
	return true
