extends CharacterBody3D
## MAISHA 3D: Controlador de personaje para el mundo 3D estilizado / diorama de Maisha.
## Movimiento suave analógico, rotación hacia la dirección de avance,
## bamboleo tierno de paso (waddle), luz del Corazón de Asili y cetro mágico.

signal danio(vida: int)
signal paso(posicion: Vector3)

const VELOCIDAD := 4.2           # metros por segundo
const VELOCIDAD_CORRER := 6.8
const ACELERACION := 18.0
const GRAVEDAD := 14.0
const ROTACION_SUAVE := 12.0

@export var puede_moverse := true

var _tiempo_paso := 0.0
var _visual: Node3D = null
var _luz_corazon: OmniLight3D = null


func _ready() -> void:
	_visual = get_node_or_null("Visual")
	_luz_corazon = get_node_or_null("LuzCorazon")
	if not _luz_corazon and _visual:
		_luz_corazon = _visual.get_node_or_null("LuzCorazon")


func _physics_process(delta: float) -> void:
	# Gravedad
	if not is_on_floor():
		velocity.y -= GRAVEDAD * delta
	else:
		velocity.y = 0.0

	if not puede_moverse:
		velocity.x = move_toward(velocity.x, 0.0, ACELERACION * delta)
		velocity.z = move_toward(velocity.z, 0.0, ACELERACION * delta)
		move_and_slide()
		return

	# Entrada del jugador
	var input_dir := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo")
	var corriendo := Input.is_action_pressed("correr")
	var vel_objetivo := VELOCIDAD_CORRER if corriendo else VELOCIDAD

	# Proyección a 3D (X = horizontal, Z = profundidad en vista diorama 3/4)
	var dir_3d := Vector3(input_dir.x, 0.0, input_dir.y).normalized()

	if dir_3d.length() > 0.1:
		velocity.x = move_toward(velocity.x, dir_3d.x * vel_objetivo, ACELERACION * delta)
		velocity.z = move_toward(velocity.z, dir_3d.z * vel_objetivo, ACELERACION * delta)

		# Orientación visual hacia la marcha
		if _visual:
			var angulo_meta := atan2(dir_3d.x, dir_3d.z)
			_visual.rotation.y = lerp_angle(_visual.rotation.y, angulo_meta, ROTACION_SUAVE * delta)

			# Animación procedimental de paso alegre (bamboleo chibi)
			_tiempo_paso += delta * (14.0 if corriendo else 9.0)
			_visual.position.y = abs(sin(_tiempo_paso)) * 0.06
			_visual.rotation.z = sin(_tiempo_paso) * 0.05
	else:
		velocity.x = move_toward(velocity.x, 0.0, ACELERACION * delta)
		velocity.z = move_toward(velocity.z, 0.0, ACELERACION * delta)
		if _visual:
			_tiempo_paso = 0.0
			_visual.position.y = lerp(_visual.position.y, 0.0, 10.0 * delta)
			_visual.rotation.z = lerp_angle(_visual.rotation.z, 0.0, 10.0 * delta)

	# Latido cálido del Corazón de Asili
	if _luz_corazon:
		var t := Time.get_ticks_msec() * 0.003
		_luz_corazon.light_energy = 0.85 + sin(t * 3.0) * 0.25

	move_and_slide()
