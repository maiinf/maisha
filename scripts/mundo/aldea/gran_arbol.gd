extends StaticBody2D
## EL GRAN ÁRBOL de Cuna de Musgo. Su origen (0, 0) es la base del tronco, en el centro.
## La puerta del tronco lleva al Claro de Calma. Cuando Maisha pasa por detrás,
## el árbol se vuelve medio transparente para que no se pierda de vista.

const TEXTURA := preload("res://arte/mundos/raiz/aldea/gran_arbol.png")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const BASE := Vector2(88, 198)          # dónde está la base del tronco dentro del dibujo
const COPA := Rect2(-88, -198, 176, 176)  # zona del dibujo que puede tapar a Maisha

var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 58.0)
	sombra.position = Vector2(0, -2)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.centered = false
	_sprite.offset = -BASE
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	# colisión del tronco, con un hueco para la puerta
	_caja(Rect2(-54, -22, 40, 22))
	_caja(Rect2(14, -22, 40, 22))
	_caja(Rect2(-14, -22, 28, 8))
	# puerta al Claro de Calma (y punto de llegada al salir de él)
	var puerta: Area2D = PUERTA.new()
	puerta.id = "arbol"
	puerta.destino = "claro_de_calma"
	puerta.destino_puerta = "salida"
	puerta.salida = Vector2.DOWN
	puerta.tam = Vector2(18, 8)
	puerta.position = Vector2(0, -9)
	add_child(puerta)


func _caja(r: Rect2) -> void:
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = r.size
	forma.shape = caja
	forma.position = r.get_center()
	add_child(forma)


func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var p := maisha.global_position - global_position
	var detras := p.y < -2.0 and COPA.grow_individual(-6, 0, -6, 0).has_point(p + Vector2(0, -14))
	_sprite.modulate.a = move_toward(_sprite.modulate.a, 0.55 if detras else 1.0, delta * 3.0)
