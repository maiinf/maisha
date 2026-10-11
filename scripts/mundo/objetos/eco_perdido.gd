extends StaticBody2D
## ECO PERDIDO: una piedra alta con una espiral tallada que guarda la voz de quien vivía en Raíz antes de Giza.
## Al acercarse brilla y suelta motas de luz; al usarla (Acción), el mundo se tiñe de verde-agua y Maisha oye
## el recuerdo (la conversación «eco_<id>» de datos/dialogos/raiz.json, con su ilustración). Deja la marca
## «eco/<id>» (la pone la conversación). Hay ECOS_TOTAL en todo Raíz: juntos abren el Sendero Olvidado.

const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const TEXTURA := preload("res://arte/mundos/raiz/sendero/eco.png")
const ECOS_TOTAL := 9
const VERDE_AGUA := Color("6db0b0")
const CLARO := Color("d8f0ec")

@export var id := ""
@export var radio_interaccion := 28.0
@export var altura_bocadillo := 46.0

var _sprite: Sprite2D
var _halo: Node2D
var _tiempo := 0.0
var _cerca := 0.0                  # 0..1: lo cerca que está Maisha (brilla más)
var _motas: Array[Dictionary] = []
var _escuchando := false


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("ecos_perdidos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 11.0)
	add_child(sombra)
	_halo = Node2D.new()
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_halo.material = suma
	_halo.draw.connect(_dibujar_halo)
	add_child(_halo)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-13, -39)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	_tiempo = randf() * 4.0


func escuchado() -> bool:
	return Estado.tiene("eco/" + id)


static func cuantos_escuchados() -> int:
	var n := 0
	for m in Estado.marcas:
		if String(m).begins_with("eco/"):
			n += 1
	return n


func _process(delta: float) -> void:
	_tiempo += delta
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var objetivo := 0.0
	if maisha:
		objetivo = clampf(1.0 - (maisha.global_position.distance_to(global_position) - 20.0) / 90.0, 0.0, 1.0)
	_cerca = move_toward(_cerca, 1.0 if _escuchando else objetivo, delta * 2.0)
	_sprite.frame = 1 if (_cerca > 0.35 or escuchado()) and fmod(_tiempo, 3.0) > 0.25 else 0
	# motas de luz que suben de la espiral (más cuanto más cerca)
	if randf() < delta * (1.5 + _cerca * 9.0):
		_motas.append({"p": Vector2(randf_range(-6, 6), randf_range(-28, -12)), "v": Vector2(randf_range(-3, 3), randf_range(-14, -6)),
			"t": 0.0, "dura": randf_range(1.0, 2.2)})
	for m in _motas:
		m["t"] += delta
		m["p"] += m["v"] * delta
		m["p"].x += sin(_tiempo * 3.0 + m["dura"] * 7.0) * 4.0 * delta
	_motas = _motas.filter(func(m: Dictionary) -> bool: return m["t"] < m["dura"])
	_halo.queue_redraw()


func _dibujar_halo() -> void:
	var pulso := 0.5 + 0.5 * sin(_tiempo * 2.2)
	var fuerza := 0.45 + _cerca * 0.75 + (0.4 if _escuchando else 0.0)
	_halo.draw_circle(Vector2(0, -20), 20.0 + pulso * 4.0, Color(VERDE_AGUA, 0.10 * fuerza))
	_halo.draw_circle(Vector2(0, -20), 11.0 + pulso * 2.0, Color(VERDE_AGUA, 0.2 * fuerza))
	_halo.draw_circle(Vector2(0, -21), 5.0, Color(CLARO, 0.35 * fuerza))
	for m in _motas:
		var f: float = m["t"] / m["dura"]
		var a := sin(f * PI) * (0.5 + _cerca * 0.5)
		_halo.draw_rect(Rect2((m["p"] as Vector2).round(), Vector2.ONE), Color(CLARO if f < 0.4 else VERDE_AGUA, a))


func interactuar() -> void:
	if _escuchando:
		return
	_escuchando = true
	var nuevo := not escuchado()
	Sonido.efecto("eco_voz", 0.0, global_position)
	# el mundo se tiñe de verde-agua mientras suena el recuerdo
	var velo := CanvasLayer.new()
	velo.layer = 12
	var color := ColorRect.new()
	color.mouse_filter = Control.MOUSE_FILTER_IGNORE
	color.set_anchors_preset(Control.PRESET_FULL_RECT)
	color.color = Color(0.25, 0.6, 0.6, 0.0)
	velo.add_child(color)
	get_tree().current_scene.add_child(velo)
	var t := create_tween()
	t.tween_property(color, "color:a", 0.28, 0.8)
	await t.finished
	await CHARLA.hablar(self, "eco_" + id)
	if is_instance_valid(color):
		var t2 := color.create_tween()
		t2.tween_property(color, "color:a", 0.0, 0.8)
		t2.tween_callback(velo.queue_free)
	_escuchando = false
	if nuevo and escuchado():
		Sonido.fanfarria("objeto")
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Eco perdido escuchado (%d/%d)" % [cuantos_escuchados(), ECOS_TOTAL])
