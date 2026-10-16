extends StaticBody2D
## BRASERO del Sendero Olvidado: un cuenco de piedra con las espirales de los ecos talladas.
## Apagado tiene ceniza y escarcha; se ENCIENDE con el fuego de una semilla (semilla.gd llama a encender() si el
## brasero cae en la cruz de la explosión) y se queda encendido para siempre (marca «brasero/<mapa>/<x>,<y>»).
## Encendido: llamas que se mueven (dibujadas aquí), luz cálida y, alrededor, calor: la escarcha de Maisha se
## derrite (escarcha.gd) y, si se congela, vuelve aquí (el último brasero encendido junto al que estuvo).

const DIBUJO := preload("res://arte/mundos/raiz/olvidado/brasero.png")
const RADIO_CALOR := 56.0
const LLAMA := [Color("fff4c0"), Color("ffc860"), Color("ff8a2a"), Color("c84a14")]

@export var marca := ""
@export var encendido_al_empezar := false

var encendido := false
var _sprite: Sprite2D
var _llamas: Node2D
var _luz: PointLight2D
var _tiempo := 0.0
var _chispas: Array[Dictionary] = []


func _ready() -> void:
	add_to_group("encendibles")
	add_to_group("braseros")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 9.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-11, -23)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_llamas = Node2D.new()
	_llamas.position = Vector2(0, -15)
	_llamas.z_index = 1
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_llamas.material = suma
	_llamas.draw.connect(_dibujar_llamas)
	add_child(_llamas)
	_luz = PointLight2D.new()
	_luz.position = Vector2(0, -16)
	_luz.color = Color(1.0, 0.62, 0.3)
	_luz.texture = _textura_luz()
	_luz.texture_scale = 0.9
	_luz.height = 20.0
	add_child(_luz)
	_tiempo = randf() * 3.0
	_poner_encendido(encendido_al_empezar or (marca != "" and Estado.tiene(marca)))


func _poner_encendido(si: bool) -> void:
	encendido = si
	_sprite.frame = 1 if si else 0
	_llamas.visible = si
	_luz.visible = si


## Lo enciende el fuego de una semilla
func encender() -> void:
	if encendido:
		return
	_poner_encendido(true)
	if marca != "":
		Estado.marcar(marca)
	Sonido.efecto("fuego_quema", 0.0, global_position)
	for i in 14:
		_chispas.append({"p": Vector2(randf_range(-5, 5), -14), "v": Vector2(randf_range(-20, 20), randf_range(-50, -20)), "t": 0.0})


## ¿Está dentro de su calor?
func calienta(punto: Vector2) -> bool:
	return encendido and punto.distance_to(global_position) <= RADIO_CALOR


func _process(delta: float) -> void:
	if not encendido:
		return
	_tiempo += delta
	_luz.energy = (0.75 + 0.12 * sin(_tiempo * 7.0) + 0.06 * sin(_tiempo * 13.0)) * (0.55 + 0.45 * Reloj.oscuridad)
	if randf() < delta * 5.0:
		_chispas.append({"p": Vector2(randf_range(-4, 4), -16), "v": Vector2(randf_range(-6, 6), randf_range(-30, -16)), "t": 0.0})
	for c in _chispas:
		c["t"] += delta
		c["p"] += c["v"] * delta
		c["v"].x += sin(_tiempo * 4.0 + c["p"].y) * 12.0 * delta
	_chispas = _chispas.filter(func(c: Dictionary) -> bool: return c["t"] < 1.1)
	_llamas.queue_redraw()


## Llamas de píxeles: tres lenguas que suben y se mueven, más claras dentro
func _dibujar_llamas() -> void:
	for k in 3:
		var x := (k - 1) * 3.0
		var alto := 6.0 + 2.5 * sin(_tiempo * (8.0 + k) + k * 2.0) + (2.0 if k == 1 else 0.0)
		for i in int(alto):
			var t := float(i) / alto
			var ancho := (1.0 - t) * (2.6 if k == 1 else 2.0)
			var vaiven := sin(_tiempo * 9.0 + i * 0.7 + k) * t * 1.4
			var col: Color = LLAMA[clampi(int(t * 3.2), 0, 3)]
			_llamas.draw_rect(Rect2(Vector2(x - ancho + vaiven, -i).floor(), Vector2(maxf(1.0, ancho * 2.0), 1)), Color(col, 0.9 - t * 0.4))
	for c in _chispas:
		var vida: float = 1.0 - c["t"] / 1.1
		_llamas.draw_rect(Rect2((c["p"] as Vector2 - _llamas.position).floor(), Vector2.ONE), Color(1.0, 0.7, 0.3, vida))


func _textura_luz() -> GradientTexture2D:
	return preload("res://scripts/mundo/relieve.gd").textura_luz(128)
