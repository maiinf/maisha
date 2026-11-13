extends StaticBody2D
## UN PEDESTAL DE SIGILO (Sigilia, la Sección Prohibida): una columna corta de mármol con un cuenco de oro y la runa
## de su sigilo (`tipo`: «fuego», «hielo» o «rayo»). Solo responde a SU sigilo: el de fuego está en «encendibles»
## (encender), el de hielo en «congelables» (congelar) y el de rayo en «cargables» (cargar).
##   - `dormido`: no responde (lo dice Maisha al mirarlo) hasta que algo lo despierta (despertar()).
##   - Con `marca`: una vez activado se queda encendido para siempre (los sellos de las cámaras y los del Claustro).
##   - Sin marca: se enciende `dura` s y se apaga (los de la Rotonda, en la pelea con el Grimorio).
## Dibujo: arte/mundos/sigilia/seccion/pedestal.png (6 fotogramas: fuego, hielo y rayo, apagado y encendido).

signal activado(tipo: String)

const DIBUJO := preload("res://arte/mundos/sigilia/seccion/pedestal.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const TIPOS := ["fuego", "hielo", "rayo"]
const COLORES := {"fuego": Color("ff6a20"), "hielo": Color("a0dcf4"), "rayo": Color("ffe860")}

@export var tipo := "fuego"
@export var marca := ""
@export var dura := 2.5
@export var dormido := false

var encendido := false
## (la pelea lo pone: un aro que late alrededor del pedestal que toca)
var marcado := false
var radio_interaccion := 24.0
var altura_bocadillo := 34.0
var _queda := 0.0
var _tiempo := 0.0
var _sprite: Sprite2D
var _luz: PointLight2D


func _ready() -> void:
	add_to_group({"fuego": "encendibles", "hielo": "congelables", "rayo": "cargables"}[tipo])
	add_to_group("pedestales")
	add_to_group("interactuables")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 9.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -15)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	_luz = PointLight2D.new()
	_luz.position = Vector2(0, -24)
	_luz.color = COLORES[tipo]
	_luz.texture = preload("res://scripts/mundo/sigilia/farol_runico.gd")._textura_luz()
	_luz.texture_scale = 0.9
	_luz.height = 24.0
	add_child(_luz)
	_poner(marca != "" and Estado.tiene(marca))


func _poner(si: bool) -> void:
	encendido = si
	_sprite.frame = TIPOS.find(tipo) * 2 + (1 if si else 0)
	_luz.visible = si


func despertar() -> void:
	dormido = false


## Lo activa su sigilo (cada uno llama al suyo; los tres hacen lo mismo)
func encender() -> void:
	_activar()


func congelar() -> bool:
	return _activar()


func cargar() -> void:
	_activar()


func _activar() -> bool:
	if dormido:
		Sonido.efecto("clinc", -6.0, global_position)
		return false
	if marca != "":
		if encendido:
			return true
		Estado.marcar(marca)
	_queda = dura
	Sonido.efecto("geoda_encender", -2.0, global_position)
	_poner(true)
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position + Vector2(0, -20), COLORES[tipo], 0.9, 0.9, 0.4)
	activado.emit(tipo)
	return true


func interactuar() -> void:
	await CHARLA.hablar(self, "seccion_pedestal_dormido" if dormido else "seccion_pedestal_" + tipo)


func _process(delta: float) -> void:
	_tiempo += delta
	if encendido and marca == "":
		_queda -= delta
		if _queda <= 0.0:
			_poner(false)
	if encendido:
		_luz.energy = (0.8 + 0.12 * sin(_tiempo * 9.0)) * (0.6 + 0.4 * Reloj.oscuridad)
	queue_redraw()


func _draw() -> void:
	if marcado and not encendido:
		var r := 13.0 + 2.5 * sin(_tiempo * 6.0)
		draw_arc(Vector2(0, -2), r, 0, TAU, 24, Color(COLORES[tipo], 0.85), 1.0)
		draw_arc(Vector2(0, -2), r + 4.0, 0, TAU, 24, Color(COLORES[tipo], 0.3), 1.0)
