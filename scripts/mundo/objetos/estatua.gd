extends StaticBody2D
## ESTATUA: un aldeano convertido en piedra por Giza, junto a una zona corrupta.
## Al purgar la zona, la piedra se resquebraja y el aldeano vuelve a la vida:
## da las gracias, se marcha a la aldea y queda la marca «rescatado_<id>».

signal rescatado

const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const PIEDRAS := [Color("a0a596"), Color("7a806d"), Color("525649")]

@export var id := ""
@export var radio_interaccion := 26.0
@export var altura_bocadillo := 46.0

var despierto := false
var _sprite: Sprite2D
var _forma: CollisionShape2D
var _trozos: Array[Dictionary] = []
var _destello := 0.0


func _ready() -> void:
	add_to_group("estatuas")
	add_to_group("interactuables")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/aldea/estatua_%s.png" % id)
	_sprite.centered = false
	_sprite.offset = Vector2(-_sprite.texture.get_width() / 2, -_sprite.texture.get_height())
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 6)
	_forma.shape = caja
	_forma.position = Vector2(0, -3)
	add_child(_forma)


func interactuar() -> void:
	if not despierto:
		await CHARLA.hablar(self, "estatua_" + id)


## La zona se ha purgado: la piedra se rompe y el aldeano despierta
func despertar() -> void:
	if despierto:
		return
	despierto = true
	Sonido.efecto("estatua_despierta")
	remove_from_group("interactuables")
	# tiembla cada vez más
	var t := create_tween()
	for i in 10:
		t.tween_property(_sprite, "position:x", 1.0 if i % 2 == 0 else -1.0, 0.05 + 0.01 * (10 - i))
	t.tween_property(_sprite, "position:x", 0.0, 0.03)
	await t.finished
	# estalla la piedra: trozos que saltan y un destello
	var azar := RandomNumberGenerator.new()
	for i in 22:
		var a := azar.randf_range(PI * 1.05, TAU * 0.98)
		_trozos.append({"pos": Vector2(azar.randf_range(-8, 8), azar.randf_range(-30, -4)),
			"vel": Vector2(cos(a), sin(a)) * azar.randf_range(30, 75), "color": PIEDRAS[i % 3], "vida": 0.0})
	_destello = 0.25
	_sprite.texture = load("res://arte/personajes/aldeanos/%s_frente.png" % id)
	_sprite.offset = Vector2(-12, -32)
	_sprite.material = null
	await get_tree().create_timer(0.8).timeout
	await CHARLA.hablar(self, "rescate_" + id)
	Estado.marcar("rescatado_" + id)
	rescatado.emit()
	# se va hacia la aldea (al este) y desaparece
	_forma.set_deferred("disabled", true)
	var salida := create_tween().set_parallel(true)
	salida.tween_property(self, "position", position + Vector2(70, 0), 1.4)
	salida.tween_property(self, "modulate:a", 0.0, 1.4).set_delay(0.4)
	salida.chain().tween_callback(queue_free)


func _process(delta: float) -> void:
	if _trozos.is_empty() and _destello <= 0.0:
		return
	_destello = maxf(0.0, _destello - delta)
	for tr in _trozos:
		tr["vida"] += delta
		tr["vel"].y += 220.0 * delta
		tr["pos"] += tr["vel"] * delta
	_trozos = _trozos.filter(func(tr: Dictionary) -> bool: return tr["vida"] < 0.7)
	_sprite.modulate = Color(1, 1, 1).lerp(Color(3, 3, 2.6), _destello / 0.25)
	queue_redraw()


func _draw() -> void:
	for tr in _trozos:
		draw_rect(Rect2(tr["pos"].round(), Vector2(2, 2)), Color(tr["color"], 1.0 - tr["vida"] / 0.7))
