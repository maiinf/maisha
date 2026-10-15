extends StaticBody2D
## FAROL RÚNICO (Sigilia, Paso de la Escarcha): un poste de piedra morada con un fanal de cobre y una runa de fuego.
## Se enciende con el SIGILO DE FUEGO (sigilo_fuego.gd llama a encender_runa) y se queda encendido para siempre
## (marca «farol/<mapa>/<x>,<y>»). Encendido, ABRIGA a su alrededor (abriga()): ahí el viento no empuja (ventisca.gd)
## y la nieve se ablanda (nieve_honda.gd). Las llamas, la luz y las chispas se dibujan aquí.

signal encendido_ahora

const DIBUJO := preload("res://arte/mundos/sigilia/paso/farol.png")
const RADIO := 52.0
const LLAMA := [Color("fff4c0"), Color("ffd870"), Color("ff9a3a"), Color("c85a1a")]

@export var marca := ""

var encendido := false
var _sprite: Sprite2D
var _llama: Node2D
var _luz: PointLight2D
var _tiempo := 0.0
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	add_to_group("faroles_runicos")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 8.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-9, -33)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(10, 5)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	_llama = Node2D.new()
	_llama.position = Vector2(0, -24)
	_llama.z_index = 1
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_llama.material = suma
	_llama.draw.connect(_dibujar_llama)
	add_child(_llama)
	_luz = PointLight2D.new()
	_luz.position = Vector2(0, -24)
	_luz.color = Color(1.0, 0.72, 0.4)
	_luz.texture = _textura_luz()
	_luz.texture_scale = 1.1
	_luz.height = 24.0
	add_child(_luz)
	_tiempo = randf() * 3.0
	_poner(marca != "" and Estado.tiene(marca))


func _poner(si: bool) -> void:
	encendido = si
	_sprite.frame = 1 if si else 0
	_llama.visible = si
	_luz.visible = si


## Lo enciende el sigilo de fuego
func encender_runa() -> void:
	if encendido:
		return
	_poner(true)
	if marca != "":
		Estado.marcar(marca)
	Sonido.efecto("fuego_quema", 0.0, global_position)
	Sonido.efecto("campanilla", -10.0, global_position, 0.1)
	for i in 16:
		_chispas.append({"p": Vector2(randf_range(-3, 3), -24), "v": Vector2(randf_range(-22, 22), randf_range(-50, -16)), "t": 0.0})
	encendido_ahora.emit()


## ¿Abriga este punto? (encendido y cerca)
func abriga(punto: Vector2) -> bool:
	return encendido and punto.distance_to(global_position) <= RADIO


func _process(delta: float) -> void:
	if not encendido:
		return
	_tiempo += delta
	_luz.energy = (0.85 + 0.1 * sin(_tiempo * 6.0) + 0.05 * sin(_tiempo * 11.0)) * (0.6 + 0.4 * Reloj.oscuridad)
	if randf() < delta * 3.0:
		_chispas.append({"p": Vector2(randf_range(-2, 2), -26), "v": Vector2(randf_range(-5, 5), randf_range(-22, -12)), "t": 0.0})
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
		c["v"].x += sin(_tiempo * 4.0 + c["p"].y) * 10.0 * delta
	_chispas = _chispas.filter(func(c: Dictionary) -> bool: return c["t"] < 1.0)
	_llama.queue_redraw()


## La llamita dentro del fanal (pequeña: está tras el cristal) y las chispas que salen por arriba
func _dibujar_llama() -> void:
	var alto := 4.0 + 1.5 * sin(_tiempo * 9.0) + sin(_tiempo * 14.0) * 0.6
	for i in int(alto):
		var t := float(i) / alto
		var ancho := (1.0 - t) * 1.8
		var vaiven := sin(_tiempo * 10.0 + i) * t * 0.8
		var col: Color = LLAMA[clampi(int(t * 3.2), 0, 3)]
		_llama.draw_rect(Rect2(Vector2(-ancho + vaiven, 2 - i).floor(), Vector2(maxf(1.0, ancho * 2.0), 1)), Color(col, 0.95 - t * 0.4))
	for c in _chispas:
		var vida: float = 1.0 - c["t"]
		_llama.draw_rect(Rect2((c["p"] as Vector2 - _llama.position).floor(), Vector2.ONE), Color(1.0, 0.75, 0.35, vida))


func _textura_luz() -> GradientTexture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.35, 0.7, 1.0])
	g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.55), Color(1, 1, 1, 0.15), Color(1, 1, 1, 0)])
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 128
	t.height = 128
	return t
