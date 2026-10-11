extends StaticBody2D
## ARCO DE RAÍZ: dos pilares de piedra antigua con raíces enroscadas que se trenzan arriba
## alrededor de la Semilla del Arco (dibujo: herramientas/pintar_portal.py).
## Dormido (oscuro, con espinas de Giza) hasta que se pone su marca; entonces se abre con un destello:
## la semilla late en ámbar, las runas de los pilares brillan y dentro se ven los Prados.
## Al cruzarlo, Maisha pasa a la otra tierra.

const TEXTURA := preload("res://arte/mundos/kitovu/portal.png")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")

@export var id := ""
@export var destino := ""
@export var destino_puerta := ""
@export var abierto_si := ""          # marca que lo abre ("" = siempre abierto)
@export var radio_interaccion := 34.0
@export var altura_bocadillo := 96.0

var _sprite: Sprite2D
var _luz: Node2D
var _puerta: Area2D
var _tiempo := 0.0
var _destello := 0.0


func _ready() -> void:
	add_to_group("portales")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 40.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-48, -118)
	add_child(_sprite)
	_luz = Node2D.new()
	_luz.z_index = 2
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luz.material = suma
	_luz.draw.connect(_dibujar_luz)
	add_child(_luz)
	# los pilares chocan; por el centro se pasa
	for x in [-31.0, 31.0]:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(20, 8)
		forma.shape = caja
		forma.position = Vector2(x, -4)
		add_child(forma)
	# el fondo del arco tampoco se atraviesa (se entra por delante)
	var fondo := CollisionShape2D.new()
	var caja_fondo := RectangleShape2D.new()
	caja_fondo.size = Vector2(44, 4)
	fondo.shape = caja_fondo
	fondo.position = Vector2(0, -14)
	add_child(fondo)
	Estado.marca_puesta.connect(_al_poner_marca)
	if abierto():
		_abrir(false)
	else:
		add_to_group("interactuables")


func abierto() -> bool:
	return abierto_si == "" or Estado.tiene(abierto_si)


func _al_poner_marca(marca: String) -> void:
	if marca == abierto_si and _puerta == null:
		_abrir(true)


func _abrir(con_efecto: bool) -> void:
	_sprite.frame = 1
	remove_from_group("interactuables")
	_puerta = PUERTA.new()
	_puerta.id = id
	_puerta.destino = destino
	_puerta.destino_puerta = destino_puerta
	_puerta.salida = Vector2.DOWN
	_puerta.tam = Vector2(40, 10)
	_puerta.position = Vector2(0, -8)
	add_child(_puerta)
	if con_efecto:
		Sonido.efecto("portal_abre")
		_destello = 1.0
		_sprite.modulate = Color(2.0, 2.4, 1.8)
		create_tween().tween_property(_sprite, "modulate", Color.WHITE, 1.2)


func interactuar() -> void:
	await CHARLA.hablar(self, "kitovu_portal")


func _process(delta: float) -> void:
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta * 0.8)
	_luz.queue_redraw()


const SEMILLA := Vector2(0, -103)       # la Semilla del Arco, arriba en el nudo
const DENTRO := Vector2(0, -56)


func _dibujar_luz() -> void:
	if _sprite.frame == 0:
		# dormido: la semilla y el fondo laten violeta, muy débiles
		var p := 0.5 + 0.5 * sin(_tiempo * 1.5)
		_luz.draw_circle(DENTRO, 18.0 + p * 4.0, Color(0.55, 0.3, 0.75, 0.05 * p))
		_luz.draw_circle(SEMILLA, 4.0 + p, Color(0.6, 0.3, 0.8, 0.12 * p))
		return
	# abierto: la semilla late en ámbar (dos golpes, como un corazón)
	var t := fmod(_tiempo, 1.6)
	var latido := maxf(exp(-t * 7.0), 0.75 * exp(-maxf(0.0, t - 0.25) * 7.0) if t > 0.25 else 0.0)
	for i in 4:
		_luz.draw_circle(SEMILLA, 4.0 + i * 4.0 + latido * 4.0, Color(1.0, 0.75, 0.3, (0.07 + 0.08 * latido) / (i + 1)))
	# la luz de los Prados al otro lado
	var pulso := 0.7 + 0.3 * sin(_tiempo * 2.0)
	for i in 5:
		_luz.draw_circle(DENTRO, 12.0 + i * 8.0, Color(0.95, 0.9, 0.55, 0.035 * pulso))
	# runas de los pilares que se encienden por turnos
	for lado in [-31.0, 31.0]:
		for k in 5:
			var brillo := 0.5 + 0.5 * sin(_tiempo * 2.0 - k * 0.8 + lado)
			_luz.draw_circle(Vector2(lado, -48 - k * 8.5), 2.5, Color(1.0, 0.8, 0.4, 0.10 * brillo))
	# ondas en la superficie del paso (como agua de luz)
	for k in 3:
		var f := fmod(_tiempo * 0.35 + k / 3.0, 1.0)
		var r := 6.0 + f * 26.0
		_luz.draw_arc(DENTRO + Vector2(0, 8), r, 0.0, TAU, 32, Color(1.0, 0.97, 0.8, 0.10 * (1.0 - f)), 1.0)
	# motas de luz que salen del paso y suben
	for k in 9:
		var f := fmod(_tiempo * 0.4 + k / 9.0, 1.0)
		var a := k * 2.3
		var q := (DENTRO + Vector2(cos(a) * 20.0 * f, sin(a) * 24.0 * f - f * 22.0)).round()
		_luz.draw_rect(Rect2(q, Vector2.ONE), Color(1, 0.97, 0.8, 1.0 - f))
	if _destello > 0.0:
		_luz.draw_circle(DENTRO, 70.0 * (1.0 - _destello) + 10.0, Color(0.9, 1.0, 0.8, 0.4 * _destello))
		_luz.draw_circle(SEMILLA, 30.0 * (1.0 - _destello) + 6.0, Color(1.0, 0.85, 0.4, 0.5 * _destello))
