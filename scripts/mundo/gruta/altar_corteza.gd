extends StaticBody2D
## EL SANTUARIO DE CORTEZA (Gruta de las Raíces, «ą»): un tocón enorme del Primer Árbol con un escudo de corteza encima,
## que brilla. Al tocarlo, la corteza se enrosca en el cetro: Maisha consigue el ESCUDO DE CORTEZA (marca
## «escudo_corteza»; J mantenida lo levanta, maisha.gd).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const DIBUJO := preload("res://arte/mundos/raiz/gruta/altar_corteza.png")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")

var radio_interaccion := 34.0
var altura_bocadillo := 46.0
var _sprite: Sprite2D
var _luz: PointLight2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("interactuables")
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(34, 10)
	forma.shape = caja
	forma.position = Vector2(0, -5)
	add_child(forma)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.frame = 1 if Estado.tiene("escudo_corteza") else 0
	_sprite.offset = Vector2(0, -24)
	add_child(_sprite)
	_luz = PointLight2D.new()
	_luz.texture = OSCURIDAD.textura_luz()
	_luz.texture_scale = 0.95
	_luz.color = Color(1.0, 0.8, 0.45)
	_luz.position = Vector2(0, -36)
	add_child(_luz)


func _process(delta: float) -> void:
	_tiempo += delta
	_luz.energy = (0.55 if Estado.tiene("escudo_corteza") else 1.1) + sin(_tiempo * 1.5) * 0.1


func interactuar() -> void:
	if Estado.tiene("escudo_corteza"):
		await CHARLA.hablar(self, "gruta_altar_vacio")
		return
	await CHARLA.hablar(self, "gruta_altar")
	Estado.marcar("escudo_corteza")
	_sprite.frame = 1
	Sonido.fanfarria("objeto")
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		maisha.call("celebrar")
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.call("mostrar_mensaje", "Escudo de corteza: mantén J para levantarlo")
