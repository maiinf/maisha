extends StaticBody2D
## UNA BOBINA ASTRAL (Sigilia, el Observatorio de la Aurora): un carrete de hilo de cobre sobre un pie de piedra,
## con una bola de latón arriba. Se CARGA con el SIGILO DE RAYO (está en «cargables»: sigilo_rayo.gd llama a cargar()).
##   - Normal: se queda encendida `dura` s y se apaga (los últimos 2 s parpadea). Los PUENTES DE CONSTELACIÓN
##     (sigilia/puente_constelacion.gd) piden que todas las suyas estén encendidas a la vez.
##   - Con `marca` (una bobina mayor): se queda encendida para siempre.
##   - fijar(): la deja encendida para siempre (lo hace su puente cuando se enciende).
## El mismo nodo, con otro `dibujo`, hace de DIAPASÓN de la Gran Cúpula (los de Kengele).
## Dibujos (2 fotogramas: apagada, encendida): arte/mundos/sigilia/observatorio/ (herramientas/pintar_observatorio.py).

signal cambiada(encendida: bool)

const CHARLA := preload("res://scripts/mundo/charla.gd")
const RAYO := [Color("ffffff"), Color("fff6b0"), Color("ffd84a"), Color("7fd6ff")]

@export var marca := ""
@export var dura := 7.0
@export var dibujo := "bobina"

var encendida := false
var radio_interaccion := 24.0
var altura_bocadillo := 34.0
var _queda := 0.0
var _fija := false
var _tiempo := 0.0
var _sprite: Sprite2D
var _luz: PointLight2D
var _chispas: Node2D


func _ready() -> void:
	add_to_group("cargables")
	add_to_group("bobinas")
	add_to_group("interactuables")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 9.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/sigilia/observatorio/%s.png" % dibujo)
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -_sprite.texture.get_height() / 2.0 + 3)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	_chispas = Node2D.new()
	_chispas.z_index = 1
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_chispas.material = suma
	_chispas.draw.connect(_dibujar_chispas)
	add_child(_chispas)
	_luz = PointLight2D.new()
	_luz.position = Vector2(0, -22)
	_luz.color = Color(0.75, 0.9, 1.0)
	_luz.texture = preload("res://scripts/mundo/sigilia/farol_runico.gd")._textura_luz()
	_luz.texture_scale = 0.9
	_luz.height = 24.0
	add_child(_luz)
	_tiempo = randf() * 3.0
	_fija = marca != "" and Estado.tiene(marca)
	_poner(_fija)


func _poner(si: bool) -> void:
	var antes := encendida
	encendida = si
	_sprite.frame = 1 if si else 0
	_luz.visible = si
	_chispas.visible = si
	if antes != si:
		cambiada.emit(si)


## La carga el Sigilo de Rayo
func cargar() -> void:
	_queda = dura
	if marca != "":
		Estado.marcar(marca)
		_fija = true
	if encendida:
		return
	Sonido.efecto("geoda_encender", -2.0, global_position)
	Sonido.efecto("campanilla", -8.0, global_position, 0.1)
	_poner(true)


## Encendida para siempre (su puente ya está tendido)
func fijar() -> void:
	_fija = true
	_poner(true)


func apagar() -> void:
	if not _fija:
		_poner(false)


func interactuar() -> void:
	await CHARLA.hablar(self, "observatorio_%s" % dibujo)


func _process(delta: float) -> void:
	if not encendida:
		return
	_tiempo += delta
	if not _fija:
		_queda -= delta
		if _queda <= 0.0:
			Sonido.efecto("clinc", -8.0, global_position)
			_poner(false)
			return
		# los últimos 2 s, parpadea: se está apagando
		_sprite.frame = 0 if _queda < 2.0 and int(_queda * 8.0) % 2 == 0 else 1
	_luz.energy = (0.8 + 0.15 * sin(_tiempo * 17.0)) * (0.6 + 0.4 * Reloj.oscuridad)
	_chispas.queue_redraw()


## Los rayitos que saltan de la bola de arriba
func _dibujar_chispas() -> void:
	var arriba := Vector2(0, -_sprite.texture.get_height() + 8)
	var semilla := int(_tiempo * 14.0)
	for k in 3:
		var a := float((semilla * 37 + k * 101) % 360) * PI / 180.0
		var largo := 5.0 + float((semilla * 13 + k * 7) % 5)
		var medio := arriba + Vector2(cos(a), sin(a)) * largo * 0.5 + Vector2(sin(a * 3.0), cos(a * 2.0)) * 2.0
		var fin := arriba + Vector2(cos(a), sin(a)) * largo
		_chispas.draw_polyline(PackedVector2Array([arriba, medio.round(), fin.round()]), RAYO[(semilla + k) % 4], 1.0)
	_chispas.draw_circle(arriba, 2.0 + 0.6 * sin(_tiempo * 20.0), Color(1.0, 0.98, 0.8, 0.9))
