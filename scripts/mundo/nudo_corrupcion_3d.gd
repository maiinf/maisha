extends StaticBody3D
## NUDO DE CORRUPCIÓN DE GIZA 3D (OBJETIVO DE PURIFICACIÓN)
## Bloquea el paso y marchita el entorno. Al ser golpeado con el Cetro de Raíz,
## desencadena la onda catártica de vida que reverdece el bioma y abre los caminos.

signal purificado(posicion: Vector3)

@export var vida := 2
var purificada := false

var _mesh: Node3D = null
var _luz_corrupcion: OmniLight3D = null
var _audio: AudioStreamPlayer3D = null


func _ready() -> void:
	_mesh = get_node_or_null("Visual")

	# Luz pulsante violeta de Giza
	_luz_corrupcion = OmniLight3D.new()
	_luz_corrupcion.light_color = Color(0.70, 0.20, 0.95)
	_luz_corrupcion.light_energy = 2.4
	_luz_corrupcion.omni_range = 6.5
	_luz_corrupcion.transform.origin = Vector3(0, 1.2, 0)
	add_child(_luz_corrupcion)

	_audio = AudioStreamPlayer3D.new()
	_audio.max_distance = 30.0
	add_child(_audio)


func _process(_delta: float) -> void:
	if purificada:
		return
	# Pulsación tétrica de Giza
	if _luz_corrupcion:
		_luz_corrupcion.light_energy = 2.2 + sin(Time.get_ticks_msec() * 0.004) * 0.8


func recibir_ataque(danio_cetro: int, _origen: Vector3 = Vector3.ZERO) -> void:
	if purificada:
		return

	vida -= danio_cetro

	# Sonido de impacto en cristal pétreo
	var snd := load("res://audio/sonidos/cristal.ogg")
	if snd and _audio:
		_audio.stream = snd
		_audio.play()

	if vida <= 0:
		purificar()


func purificar() -> void:
	if purificada:
		return
	purificada = true
	emit_signal("purificado", global_position)

	# Desactivar colisiones para permitir el paso
	collision_layer = 0
	collision_mask = 0

	# 1. Desencadenar la Gran Onda Catártica de Vida
	var escena_onda := load("res://escenas/efectos/onda_purificacion_3d.tscn")
	if escena_onda:
		var onda: Node3D = escena_onda.instantiate()
		onda.global_position = global_position + Vector3(0, 0.5, 0)
		onda.radio_maximo = 18.0
		get_parent().add_child(onda)

	# 2. Desvanecer la luz de Giza y disolver la malla corrupta
	if _luz_corrupcion:
		var tween_luz := create_tween()
		tween_luz.tween_property(_luz_corrupcion, "light_color", Color(1.0, 0.85, 0.35), 0.35)
		tween_luz.tween_property(_luz_corrupcion, "light_energy", 0.0, 0.8)

	var tween_mesh := create_tween()
	tween_mesh.tween_property(self, "scale", Vector3(1.15, 1.15, 1.15), 0.2)
	tween_mesh.tween_property(self, "scale", Vector3.ZERO, 0.6).set_ease(Tween.EASE_IN)
	tween_mesh.tween_callback(queue_free)
