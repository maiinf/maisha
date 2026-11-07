extends "res://scripts/mundo/sigilia/vecino.gd"
## UN ESCRIBA DE MAANDIKO con nombre propio (Daftari, ...). Al principio está EN BLANCO (sin color, sin voz): su
## nombre está en una FICHA DEL ÍNDICE perdida por los caminos («ficha_<nombre>»). Al devolvérsela (la marca
## «<nombre>_nombre» la pone su conversación), le vuelve el color de golpe y habla.
## Su conversación es la de su nombre («daftari», ...), con sus partes en blanco y con nombre.

@export var nombre := ""
## su dibujo con color (el de en blanco es «<dibujo>_blanco»): el de escriba, o uno propio (Mfereji)
@export var dibujo := "escriba"


func _ready() -> void:
	charla = nombre
	id = dibujo if Estado.tiene(nombre + "_nombre") else dibujo + "_blanco"
	super()
	add_to_group("escribas")


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca != nombre + "_nombre" or id == dibujo:
		return
	id = dibujo
	_sprite.texture = load("res://arte/personajes/aldeanos/%s_anim.png" % dibujo)
	Sonido.efecto("arte_sube", -4.0, global_position)
	modulate = Color(2.2, 2.0, 1.6)
	create_tween().tween_property(self, "modulate", Color.WHITE, 0.9)
	var gotas: Node2D = preload("res://scripts/efectos/astillas.gd").new()
	gotas.cantidad = 10
	gotas.position = global_position + Vector2(0, -16)
	get_parent().add_child(gotas)
	# en cuanto acaba lo que piensa Maisha, habla él (ya con su voz)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	while is_inside_tree() and is_instance_valid(dialogo) and dialogo.hablando:
		await get_tree().process_frame
	await get_tree().create_timer(0.5).timeout
	if is_inside_tree():
		await CHARLA.hablar(self, nombre)
