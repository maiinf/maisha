extends StaticBody2D
## TRONCO CAÍDO con unas tablas apoyadas: de aquí salen las tablas para arreglar la cerca.

const TEXTURA := preload("res://arte/mundos/kitovu/tronco.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")

@export var radio_interaccion := 26.0
@export var altura_bocadillo := 22.0

var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("troncos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 16.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-18, -17)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(30, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)
	_sprite.frame = 1 if Estado.tiene("tablas_cogidas") else 0


func interactuar() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if Estado.tiene("tablas_cogidas"):
		await CHARLA.hablar(self, "kitovu_tronco_vacio")
	elif not Estado.tiene("tarea_cerca"):
		await dialogo.decir("Maisha", ["Un tronco caído con unas tablas apoyadas."], "pensamiento")
	else:
		_sprite.frame = 1
		Sonido.efecto("tablas_coger")
		Estado.marcar("tablas_cogidas")
		Estado.dar("tablas")
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("¡Tablas! Ahora, al hueco de la cerca")
