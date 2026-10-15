extends "res://scripts/mundo/aldea/aldeano.gd"
## TAA, el armiño farolero del Paso de la Escarcha. Al llegar está EN BLANCO (la Tinta Quieta le borró el nombre):
## pálido, sin voz (conversación «taa_blanco»). Su nombre está en una FICHA DEL ÍNDICE que se llevó el viento
## (objeto «ficha_taa»). Al dársela (marca «taa_nombre»), le vuelve el color de golpe y habla (conversación «taa»):
## le enseña a Maisha el SIGILO DE FUEGO.

const DIBUJO_COLOR := preload("res://arte/personajes/aldeanos/taa_anim.png")

var _destello := 0.0


func _ready() -> void:
	id = "taa" if Estado.tiene("taa_nombre") else "taa_blanco"
	super()


func _process(delta: float) -> void:
	super(delta)
	if _destello > 0.0:
		_destello = maxf(0.0, _destello - delta)
		modulate = Color(1, 1, 1).lerp(Color(2.2, 2.0, 1.6), _destello)


func _al_poner_marca(marca: String) -> void:
	if marca != "taa_nombre" or id == "taa":
		return
	# le vuelve el color: un destello y la tinta que le cubría cae en gotitas
	id = "taa"
	_destello = 1.0
	_sprite.texture = DIBUJO_COLOR
	Sonido.efecto("arte_sube", -4.0, global_position)
	var gotas := preload("res://scripts/efectos/astillas.gd").new()
	gotas.cantidad = 10
	gotas.position = global_position + Vector2(0, -16)
	get_parent().add_child(gotas)
	# en cuanto acaba lo que dice Maisha, habla él (ya con su voz)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	while is_inside_tree() and is_instance_valid(dialogo) and dialogo.hablando:
		await get_tree().process_frame
	await get_tree().create_timer(0.5).timeout
	if is_inside_tree():
		await CHARLA.hablar(self, "taa")
