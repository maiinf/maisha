extends StaticBody2D
## NUNGU, EN SU CASA (después de liberarlo de Kuvu): junto a su mesa, apuntando cosas en el cuaderno. Con Acción habla
## («nungu_casa»). Dibujo: arte/zonas/raiz/nungu.png (5-6 libre, 9 saludando).

const DIBUJO := preload("res://arte/zonas/raiz/nungu.png")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")

var radio_interaccion := 26.0
var altura_bocadillo := 36.0
var _sprite: Sprite2D
var _tiempo := 0.0
var _saluda := 0.0


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("aldeanos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 10
	_sprite.offset = Vector2(0, -17)
	_sprite.flip_h = true
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func _process(delta: float) -> void:
	_tiempo += delta
	_saluda = maxf(0.0, _saluda - delta)
	_sprite.frame = 9 if _saluda > 0.0 else 5 + int(_tiempo * 1.5) % 2


func interactuar() -> void:
	_saluda = 1.2
	await CHARLA.hablar(self, "nungu_casa")
