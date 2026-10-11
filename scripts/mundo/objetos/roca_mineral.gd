extends StaticBody2D
## ROCA CON MINERAL: los cristales asoman, pero la roca es muy dura para el cetro.
## Una semilla la rompe y deja el mineral en el suelo para recogerlo.

const TEXTURA := preload("res://arte/mundos/raiz/objetos/roca_mineral.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")

@export var marca := ""          # se pone al romperla: así sigue rota en otras visitas

var rota := false
var _sprite: Sprite2D
var _forma: CollisionShape2D
var _avisada := false
var _brillo: Node2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("rocas_mineral")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-10, -17)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 8)
	_forma.shape = caja
	_forma.position = Vector2(0, -3)
	add_child(_forma)
	# destellos en las puntas de los cristales (no se vuelven grises con la corrupción)
	_brillo = Node2D.new()
	_brillo.z_index = 1
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_brillo.material = material
	_brillo.draw.connect(_dibujar_brillo)
	add_child(_brillo)
	_tiempo = randf() * 4.0
	if marca != "" and Estado.tiene(marca):
		_romper(false)


func _process(delta: float) -> void:
	if rota:
		return
	_tiempo += delta
	_brillo.queue_redraw()


## Las puntas de los cristales (respecto a la base de la roca)
const PUNTAS := [Vector2(-3, -15), Vector2(2, -16), Vector2(5, -11)]


func _dibujar_brillo() -> void:
	for i in PUNTAS.size():
		var fase := fmod(_tiempo * 0.7 + i * 0.37, 1.0)
		var p: Vector2 = PUNTAS[i]
		_brillo.draw_circle(p + Vector2(0.5, 2.5), 4.0, Color(0.9, 0.6, 0.2, 0.18))
		if fase < 0.18:
			var a := 1.0 - fase / 0.18
			_brillo.draw_rect(Rect2(p, Vector2.ONE), Color(1, 0.97, 0.85, a))
			_brillo.draw_rect(Rect2(p + Vector2(-1, 0), Vector2(3, 1)), Color(1, 0.85, 0.5, a * 0.7))
			_brillo.draw_rect(Rect2(p + Vector2(0, -1), Vector2(1, 3)), Color(1, 0.85, 0.5, a * 0.7))


## El cetro rebota: da una pista la primera vez
func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if rota:
		return false
	var t := create_tween()
	t.tween_property(_sprite, "position:x", 1.0, 0.03)
	t.tween_property(_sprite, "position:x", 0.0, 0.05)
	if not _avisada:
		_avisada = true
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Es demasiado dura para el cetro... ¿y con una semilla?")
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if rota or tipo != "explosion":
		return
	_romper(true)


func _romper(ahora: bool) -> void:
	rota = true
	if ahora:
		Sonido.efecto("mineral_romper", 0.0, global_position)
	_brillo.visible = false
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	if marca != "":
		Estado.marcar(marca)
	# el mineral queda en el suelo (si no se recogió ya en otra visita)
	var mineral: Node2D = RECOGIBLE.new()
	mineral.objeto = "mineral"
	mineral.marca = marca + "/recogido" if marca != "" else ""
	mineral.color_halo = Color(0.9, 0.6, 0.2)
	mineral.position = position + Vector2(0, 6)
	get_parent().add_child.call_deferred(mineral)
	if ahora:
		var t := create_tween()
		t.tween_property(_sprite, "position:x", 2.0, 0.04)
		t.tween_property(_sprite, "position:x", -2.0, 0.06)
		t.tween_property(_sprite, "position:x", 0.0, 0.04)
