extends Node2D
## KUKU, LA GALLINA PERDIDA de Mzee Shamba. Se ha escapado y anda asustada entre los árboles secos.
## Si Maisha corre hacia ella, huye; tras unas cuantas carreras se cansa y se sienta a jadear:
## entonces se puede coger (Acción). Cloquea de vez en cuando, para que se la encuentre por el oído.

signal cogida

const TEXTURA := preload("res://arte/mundos/kitovu/gallina.png")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const RADIO := 64.0               # no se aleja más de esto de su sitio
const HUIDAS_PARA_CANSARSE := 3

@export var radio_interaccion := 20.0
@export var altura_bocadillo := 16.0

var cansada := false
var _origen := Vector2.ZERO
var _destino := Vector2.ZERO
var _huidas := 0
var _huyendo := 0.0
var _cansancio := 0.0
var _cacareo := 2.0
var _tiempo := 0.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("gallina_perdida")
	_origen = position
	_destino = position
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 4.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-5, -10)
	add_child(_sprite)


func _process(delta: float) -> void:
	_tiempo += delta
	_cacareo -= delta
	if _cacareo <= 0.0:
		_cacareo = randf_range(4.0, 7.0)
		Sonido.efecto("gallina_cacareo", 0.0, global_position, 0.08)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	queue_redraw()
	if cansada:
		_cansancio -= delta
		_sprite.frame = 0
		_sprite.position.y = 1.0 + (1.0 if fmod(_tiempo, 0.6) < 0.3 else 0.0)    # jadea
		if _cansancio <= 0.0:
			_levantarse()
		return
	if maisha and maisha.global_position.distance_to(global_position) < 40.0 and _huyendo <= 0.0:
		# ¡se asusta y sale corriendo!
		_huyendo = 0.7
		_huidas += 1
		Sonido.efecto("gallina_asustada", 0.0, global_position, 0.1)
		var lejos := (global_position - maisha.global_position).normalized().rotated(randf_range(-0.7, 0.7))
		_destino = _origen + (position + lejos * 50.0 - _origen).limit_length(RADIO)
		if _huidas >= HUIDAS_PARA_CANSARSE:
			get_tree().create_timer(0.7).timeout.connect(cansar)
	_huyendo = maxf(0.0, _huyendo - delta)
	var rapidez := 80.0 if _huyendo > 0.0 else 16.0
	if position.distance_to(_destino) > 0.5:
		var antes := position
		position = position.move_toward(_destino, rapidez * delta)
		_sprite.flip_h = position.x > antes.x
		_sprite.frame = int(_tiempo * (14.0 if _huyendo > 0.0 else 8.0)) % 2
		_sprite.position.y = -1.0 if _huyendo > 0.0 and int(_tiempo * 14.0) % 2 == 0 else 0.0
	else:
		_sprite.frame = 0
		_sprite.position.y = 1.0 if fmod(_tiempo, 1.4) < 0.2 else 0.0           # picotea
		if randf() < delta * 0.5:
			var a := randf() * TAU
			_destino = _origen + Vector2(cos(a), sin(a) * 0.6) * randf_range(8.0, RADIO * 0.6)


## Agotada: se sienta unos segundos y se deja coger
func cansar() -> void:
	if cansada:
		return
	cansada = true
	_cansancio = 6.0
	_destino = position
	add_to_group("interactuables")


func _levantarse() -> void:
	cansada = false
	_huidas = HUIDAS_PARA_CANSARSE - 1        # la próxima vez se cansa antes
	remove_from_group("interactuables")


func interactuar() -> void:
	if not cansada:
		return
	remove_from_group("interactuables")
	Sonido.efecto("gallina_cacareo", -3.0)
	cogida.emit()
	queue_free()


func _draw() -> void:
	# gotitas de cansancio
	if cansada:
		for i in 2:
			var p := Vector2(6 + i * 3, -12 + fmod(_tiempo * 8.0 + i * 3.0, 6.0)).round()
			draw_rect(Rect2(p, Vector2(1, 2)), Color("8ec7d6"))
