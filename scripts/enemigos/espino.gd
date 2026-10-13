extends StaticBody2D
## ESPINO DE GIZA (la galería de las espinas de la Gruta, «ę»): una mata de tallos de piedra con un capullo violeta.
## Cuando Maisha está cerca, se hincha (aviso) y le ESCUPE una espina. El escudo de corteza las para. El cetro rebota en
## él; una semilla lo deshace. Dibujo: arte/mundos/raiz/gruta/espino.png (0 quieto, 1 cargando, 2 escupiendo).

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const ESPINA := preload("res://scripts/enemigos/espina.gd")

var marca := ""
var vida := R.ESPINO_VIDA
var _t := 0.0
var _carga := 0.0
var _sprite: Sprite2D
var _luz: PointLight2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("espinos")
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/gruta/espino.png")
	_sprite.hframes = 3
	_sprite.offset = Vector2(0, -13)
	add_child(_sprite)
	_luz = PointLight2D.new()
	_luz.texture = OSCURIDAD.textura_luz()
	_luz.texture_scale = 0.3
	_luz.color = Color(0.75, 0.45, 1.0)
	_luz.position = Vector2(0, -14)
	add_child(_luz)
	_t = randf() * R.ESPINO_CADA


func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var cerca := maisha != null and maisha.global_position.distance_to(global_position) < R.ESPINO_ALCANCE
	if cerca:
		_t += delta
	if cerca and _t >= R.ESPINO_CADA - 0.5:
		_carga = clampf((_t - (R.ESPINO_CADA - 0.5)) / 0.5, 0.0, 1.0)
		_sprite.frame = 1
	else:
		_sprite.frame = 0 if _t > 0.2 or not cerca else 2
	_luz.energy = 0.35 + _carga * 0.9
	if cerca and _t >= R.ESPINO_CADA:
		_t = 0.0
		_carga = 0.0
		_sprite.frame = 2
		_escupir(maisha)


func _escupir(maisha: Node2D) -> void:
	var espina: Node2D = ESPINA.new()
	espina.position = global_position + Vector2(0, -16)
	espina.direccion = ((maisha.global_position + Vector2(0, -10)) - espina.position).normalized()
	get_parent().add_child(espina)
	Sonido.efecto("cangrejo_chasca", -6.0, global_position)


func recibir_golpe(_danio: int, _dir: Vector2) -> bool:
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo != "explosion":
		return
	vida -= 2
	if vida <= 0:
		Bestiario.vencido("espino", self)
		if marca != "":
			Estado.marcar(marca)
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 12
		astillas.chispas = 4
		astillas.position = global_position + Vector2(0, -10)
		get_parent().add_child(astillas)
		Sonido.efecto("petrino_muere", 0.0, global_position)
		queue_free()
