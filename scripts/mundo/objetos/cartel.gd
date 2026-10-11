extends StaticBody2D
## CARTEL: muestra su texto cuando Maisha se acerca.

const TEXTURA := preload("res://arte/mundos/raiz/objetos/cartel.png")

var texto := ""
var _cerca := false


func _ready() -> void:
	var sprite := Sprite2D.new()
	sprite.texture = TEXTURA
	sprite.offset = Vector2(0, -8)
	add_child(sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(6, 4)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(sprite)


func _process(_delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var ahora := maisha.global_position.distance_to(global_position) < 28.0
	if ahora and not _cerca:
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje(texto)
	_cerca = ahora
