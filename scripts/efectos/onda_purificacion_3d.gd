extends Node3D
## ONDA CATÁRTICA DE PURIFICACIÓN 3D (ESTILO OKAMI / KENA)
## Esfera expansiva de luz áurea y partículas de vida de Asili que disipa la ceniza
## y restaura el mundo al derrotar un nudo de corrupción o enemigo de Giza.

@export var radio_maximo := 16.0
@export var duracion := 1.8
@export var color_onda := Color(1.0, 0.88, 0.35, 0.85)

var _tiempo := 0.0
var _malla_esfera: MeshInstance3D = null
var _luz_expansion: OmniLight3D = null
var _audio: AudioStreamPlayer3D = null


func _ready() -> void:
	# 1. Luz de expansión central
	_luz_expansion = OmniLight3D.new()
	_luz_expansion.light_color = Color(1.0, 0.85, 0.40)
	_luz_expansion.light_energy = 4.5
	_luz_expansion.omni_range = 6.0
	add_child(_luz_expansion)

	# 2. Esfera translúcida de choque áureo
	_malla_esfera = MeshInstance3D.new()
	var esfera := SphereMesh.new()
	esfera.radius = 0.5
	esfera.height = 1.0

	var mat := StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = color_onda
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.82, 0.30)
	mat.emission_energy_multiplier = 2.4
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	esfera.material = mat

	_malla_esfera.mesh = esfera
	add_child(_malla_esfera)

	# 3. Sonido espacial de purificación
	_audio = AudioStreamPlayer3D.new()
	var snd := load("res://audio/sonidos/ola_purga.ogg")
	if snd:
		_audio.stream = snd
		_audio.volume_db = 2.0
		_audio.max_distance = 35.0
		add_child(_audio)
		_audio.play()


func _process(delta: float) -> void:
	_tiempo += delta
	var t := clampf(_tiempo / duracion, 0.0, 1.0)
	# Easing suave exponencial hacia afuera
	var factor_expansion := 1.0 - pow(1.0 - t, 3.0)
	var radio_actual := lerpf(0.5, radio_maximo, factor_expansion)

	_malla_esfera.scale = Vector3.ONE * (radio_actual * 2.0)
	_luz_expansion.omni_range = radio_actual * 1.5
	_luz_expansion.light_energy = lerpf(5.0, 0.0, t)

	# Desvanecimiento alfa al alcanzar el límite
	var mat: StandardMaterial3D = _malla_esfera.mesh.material
	if mat:
		mat.albedo_color.a = lerpf(0.85, 0.0, t)
		mat.emission_energy_multiplier = lerpf(2.4, 0.0, t)

	if t >= 1.0:
		queue_free()
