extends StaticBody2D
## FAROLILLO: una llama que tiembla y un halo de luz cálida alrededor.

const TEXTURA := preload("res://arte/mundos/raiz/aldea/farol.png")
const LUZ := Color(1.0, 0.82, 0.45)

var _sprite: Sprite2D
var _halo: Node2D
var _tiempo := 0.0


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-5, -25)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(6, 4)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	# halo: se suma a lo que hay debajo (mezcla aditiva), por encima de los personajes
	_halo = Node2D.new()
	_halo.position = Vector2(0, -22)
	_halo.z_index = 2
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_halo.material = material
	_halo.draw.connect(_dibujar_halo)
	add_child(_halo)
	_tiempo = randf() * 2.0


func _process(delta: float) -> void:
	_tiempo += delta
	_sprite.frame = int(_tiempo * 5.0) % 2
	_halo.queue_redraw()


func _dibujar_halo() -> void:
	var pulso := 0.85 + 0.15 * sin(_tiempo * 7.0) * sin(_tiempo * 2.3)
	for i in 4:
		var r := (6.0 + i * 5.0) * pulso
		_halo.draw_circle(Vector2.ZERO, r, Color(LUZ, 0.05))
