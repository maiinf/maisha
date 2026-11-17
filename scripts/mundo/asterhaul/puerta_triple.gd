extends StaticBody2D
## LA PUERTA TRIPLE (Asterhaul, el Núcleo de la Estrella): tres hojas de basalto con un ojo por sello. Cada ojo se
## enciende con su marca (`sellos`, en orden: sísmico, magnético, resonante); con los tres, la puerta se abre y se
## queda abierta (`marca`).
## Dibujo: arte/mundos/asterhaul/nucleo/puerta_triple.png, 0 cerrada · 1 abierta; los ojos se encienden aquí.

signal abierta

const DIBUJO := preload("res://arte/mundos/asterhaul/nucleo/puerta_triple.png")
const OJOS := [Vector2(-22, -66), Vector2(0, -77), Vector2(22, -66)]
const LUZ := [Color("ffb040"), Color("6ad0f0"), Color("ffd878")]

var sellos: Array[String] = []
var marca := ""
var _sprite: Sprite2D
var _forma: CollisionShape2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("puertas_triples")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -40)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(64, 14)
	_forma.shape = caja
	_forma.position = Vector2(0, -7)
	add_child(_forma)
	Estado.marca_puesta.connect(_al_poner_marca)
	if Estado.tiene(marca):
		_abrir(false)


func encendidos() -> int:
	return sellos.filter(func(s: String) -> bool: return Estado.tiene(s)).size()


func esta_abierta() -> bool:
	return _sprite.frame == 1


func _al_poner_marca(m: String) -> void:
	if m in sellos:
		Sonido.efecto("diapason_ambar", 0.0, global_position)
		if encendidos() == sellos.size() and not Estado.tiene(marca):
			Estado.marcar(marca)
	elif m == marca and not esta_abierta():
		_abrir(true)


func _abrir(con_sonido: bool) -> void:
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	if con_sonido:
		Sonido.efecto("puerta_crater", 0.0, global_position)
		Impacto.temblar(4.0, 0.6)
		abierta.emit()


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()


func _draw() -> void:
	for i in OJOS.size():
		if i < sellos.size() and Estado.tiene(sellos[i]):
			var late := 0.75 + 0.25 * sin(_tiempo * 3.0 + i)
			draw_circle(OJOS[i], 5.0, Color(LUZ[i], 0.3 * late))
			draw_circle(OJOS[i], 2.6, LUZ[i])
			draw_circle(OJOS[i] + Vector2(-0.6, -0.6), 1.0, Color.WHITE)
