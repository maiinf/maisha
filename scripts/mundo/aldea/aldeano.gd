extends StaticBody2D
## ALDEANO: un personaje de la aldea con el que se puede hablar.
## Si tiene algo nuevo que contar, muestra una «!» encima.
## Solo aparece si se cumple «requiere» (p. ej. Pino, cuando ya se le ha rescatado)
## y desaparece con «esconder_si» (p. ej. Corteza se mete en su taller al reconstruirlo:
## si pasa delante de Maisha, camina hasta la puerta del edificio «se_mete_en»).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const AMBAR := Color("e6a852")
const OSCURO := Color("140e18")

@export var id := ""
@export var requiere := ""
@export var esconder_si := ""
@export var se_mete_en := ""
@export var radio_interaccion := 26.0
@export var altura_bocadillo := 40.0

var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	if (requiere != "" and not Estado.tiene(requiere)) or (esconder_si != "" and Estado.tiene(esconder_si)):
		queue_free()
		return
	Estado.marca_puesta.connect(_al_poner_marca)
	add_to_group("interactuables")
	add_to_group("aldeanos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 8.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/personajes/aldeanos/%s_frente.png" % id)
	_sprite.centered = false
	_sprite.offset = Vector2(-_sprite.texture.get_width() / 2, -_sprite.texture.get_height())
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	forma.name = "CollisionShape2D"
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_tiempo = randf() * 3.0


func _process(delta: float) -> void:
	_tiempo += delta
	# respiración: el cuerpo se estira un píxel de vez en cuando
	_sprite.scale.y = 1.0 + (1.0 / _sprite.texture.get_height() if fmod(_tiempo, 1.6) < 0.8 else 0.0)
	queue_redraw()


func interactuar() -> void:
	await CHARLA.hablar(self, id)


func _al_poner_marca(marca: String) -> void:
	if marca != esconder_si or esconder_si == "":
		return
	remove_from_group("interactuables")
	# espera a que acabe del todo la conversación (también lo que dice «después») y se va a su casa
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var calma := 0.0
	while calma < 2.2:
		if not is_inside_tree():
			return            # se ha cambiado de escena mientras tanto
		await get_tree().process_frame
		if not is_inside_tree() or not is_instance_valid(dialogo):
			return
		calma = 0.0 if dialogo.hablando else calma + get_process_delta_time()
	var destino := global_position + Vector2(0, 20)
	for e in get_tree().get_nodes_in_group("edificios"):
		if e.id == se_mete_en:
			destino = e.global_position + Vector2(0, 6)
	var forma := get_node_or_null("CollisionShape2D") as CollisionShape2D
	if forma:
		forma.set_deferred("disabled", true)
	var t := create_tween()
	t.tween_property(self, "global_position", destino, global_position.distance_to(destino) / 30.0)
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.tween_callback(queue_free)


func _draw() -> void:
	if not CHARLA.tiene_novedad(id):
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < radio_interaccion:
		return
	# «!» que bota sobre la cabeza
	var p := Vector2(0, -altura_bocadillo - 4 + round(sin(_tiempo * 5.0) * 1.5))
	draw_rect(Rect2(p + Vector2(-2, -1), Vector2(5, 11)), OSCURO)
	draw_rect(Rect2(p + Vector2(-1, 0), Vector2(3, 6)), AMBAR)
	draw_rect(Rect2(p + Vector2(-1, 7), Vector2(3, 2)), AMBAR)
