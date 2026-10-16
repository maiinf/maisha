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
## Con animación (arte/personajes/aldeanos/<id>_anim.png: quieto, respira, parpadea y su gesto, de
## herramientas/dibujar_aldeanos.py): respira, parpadea de vez en cuando y hace su gesto cada poco y al hablar
var _animado := false
var _parpadeo := 0.0
var _gesto := 0.0
var _proximo_parpadeo := 3.0
var _proximo_gesto := 7.0


func _ready() -> void:
	if (requiere != "" and not Estado.tiene(requiere)) or (esconder_si != "" and Estado.tiene(esconder_si)):
		set_process(false)
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
	var anim := "res://arte/personajes/aldeanos/%s_anim.png" % id
	if ResourceLoader.exists(anim):
		_animado = true
		_sprite.texture = load(anim)
		_sprite.hframes = 4
	else:
		_sprite.texture = load("res://arte/personajes/aldeanos/%s_frente.png" % id)
	_sprite.centered = false
	var ancho := _sprite.texture.get_width() / _sprite.hframes
	_sprite.offset = Vector2(-ancho / 2, -_sprite.texture.get_height())
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
	if _sprite == null or not is_instance_valid(_sprite):
		return
	_tiempo += delta
	if _animado:
		_animar(delta)
	else:
		# respiración: el cuerpo se estira un píxel de vez en cuando
		_sprite.scale.y = 1.0 + (1.0 / _sprite.texture.get_height() if fmod(_tiempo, 1.6) < 0.8 else 0.0)
	queue_redraw()


func _animar(delta: float) -> void:
	_parpadeo = maxf(0.0, _parpadeo - delta)
	_gesto = maxf(0.0, _gesto - delta)
	_proximo_parpadeo -= delta
	_proximo_gesto -= delta
	if _proximo_parpadeo <= 0.0:
		_proximo_parpadeo = randf_range(2.5, 5.0)
		_parpadeo = 0.14
	if _proximo_gesto <= 0.0:
		_proximo_gesto = randf_range(7.0, 12.0)
		_gesto = 0.9
	if _gesto > 0.0:
		_sprite.frame = 3
	elif _parpadeo > 0.0:
		_sprite.frame = 2
	else:
		_sprite.frame = 1 if fmod(_tiempo, 1.6) < 0.8 else 0


func interactuar() -> void:
	if _animado:
		_gesto = 1.0                           # al empezar a hablar, su gesto
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
