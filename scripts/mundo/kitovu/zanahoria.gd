extends Node2D
## ZANAHORIA DEL HUERTO: se arranca con Acción (solo cuando Mzee Shamba lo ha pedido).

const TEXTURA := preload("res://arte/mundos/kitovu/zanahoria.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")

@export var marca := ""
@export var radio_interaccion := 14.0
@export var altura_bocadillo := 16.0

var _sprite: Sprite2D


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-6, -11)
	add_child(_sprite)
	if marca != "" and Estado.tiene(marca):
		_sprite.frame = 1
	else:
		add_to_group("interactuables")
		add_to_group("zanahorias")


func interactuar() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if not Estado.tiene("tarea_cosecha"):
		await dialogo.decir("Maisha", ["Un huerto bien cuidado. Mejor no tocar nada sin permiso."], "pensamiento")
		return
	arrancar()


func arrancar() -> void:
	remove_from_group("interactuables")
	remove_from_group("zanahorias")
	_sprite.frame = 1
	Sonido.efecto("zanahoria_arrancar")
	if marca != "":
		Estado.marcar(marca)
	Estado.dar("zanahoria")
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje(Estado.texto_recogido("zanahoria"))
	# la zanahoria sale volando un momento
	var vuelo := Sprite2D.new()
	vuelo.texture = preload("res://arte/interfaz/objetos.png")
	vuelo.region_enabled = true
	vuelo.region_rect = Rect2(0, 0, 16, 16)
	vuelo.position = Vector2(0, -8)
	add_child(vuelo)
	var t := create_tween().set_parallel(true)
	t.tween_property(vuelo, "position:y", -26.0, 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_property(vuelo, "modulate:a", 0.0, 0.5)
	t.chain().tween_callback(vuelo.queue_free)
