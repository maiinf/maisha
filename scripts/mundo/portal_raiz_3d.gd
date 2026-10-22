extends Node3D
## PORTAL DE RAÍZ 3D: Conexión orgánica entre El Kitovu y Cuna de Musgo.
## Permanece dormido hasta que el jugador purifica la corrupción.
## Al cruzar el arco, realiza una transición fluida al poblado de Cuna de Musgo.

signal portal_cruzado

@export var escena_destino := "res://escenas/mundo_3d/cuna_de_musgo_3d.tscn"
@export var activo := false

var _maisha: CharacterBody3D = null
var _luz_portal: OmniLight3D = null
var _audio: AudioStreamPlayer3D = null
var _transicionando := false


func _ready() -> void:
	_luz_portal = get_node_or_null("LuzPortal")
	_audio = AudioStreamPlayer3D.new()
	var snd := load("res://audio/sonidos/portal_abre.ogg")
	if snd:
		_audio.stream = snd
	_audio.max_distance = 25.0
	add_child(_audio)

	# Conectar con el nudo de corrupción de la escena si existe
	var nudo := get_parent().get_node_or_null("NudoCorrupcion")
	if nudo and nudo.has_signal("purificado"):
		nudo.connect("purificado", Callable(self, "_on_nudo_purificado"))


func _process(_delta: float) -> void:
	if _transicionando:
		return

	if not is_instance_valid(_maisha):
		_maisha = get_parent().get_node_or_null("Maisha3D")
		return

	# Pulsación de energía del portal
	if _luz_portal:
		var brillo := (2.2 if activo else 0.4) + sin(Time.get_ticks_msec() * 0.003) * 0.3
		_luz_portal.light_energy = brillo

	# Cruce del portal al entrar en el vano
	var dist := global_position.distance_to(_maisha.global_position)
	if dist <= 2.2 and activo:
		_cruzar_portal()


func _on_nudo_purificado(_pos: Vector3) -> void:
	activo = true
	if _luz_portal:
		_luz_portal.light_color = Color(0.40, 0.95, 0.65)
	if _audio:
		_audio.play()


func _cruzar_portal() -> void:
	_transicionando = true
	emit_signal("portal_cruzado")

	if _maisha:
		_maisha.puede_moverse = false

	if _audio:
		_audio.play()

	# Transición fluida a Cuna de Musgo
	var arbol := get_tree()
	if arbol:
		arbol.change_scene_to_file(escena_destino)
