extends Node2D
## LA ESPINA que escupe el espino de Giza: vuela en línea recta; si toca a Maisha, le hace daño (o rebota en el escudo).

const R := preload("res://scripts/combate/reglas_combate.gd")
const DIBUJO := preload("res://arte/mundos/raiz/gruta/espina.png")

var direccion := Vector2.RIGHT
var _vida := 0.0


func _ready() -> void:
	add_to_group("espinas")
	var s := Sprite2D.new()
	s.texture = DIBUJO
	s.rotation = direccion.angle()
	add_child(s)


func _process(delta: float) -> void:
	_vida += delta
	position += direccion * R.ESPINA_VELOCIDAD * delta
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position + Vector2(0, 10)) < 9.0:
		maisha.call("recibir_danio", 1, global_position - direccion * 6.0, "espina")
		queue_free()
		return
	if _vida > 2.6:
		queue_free()
