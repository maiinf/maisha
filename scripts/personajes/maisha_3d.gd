extends CharacterBody3D
## MAISHA 3D: Controlador en tercera persona AAA (God of War / Zelda TotK).
## Movimiento relativo a cámara orbital, salto libre con peso, esquiva rodando,
## combate táctico de cetro y latido de luz del Corazón de Asili.

signal danio(vida_actual: int)
signal paso(posicion: Vector3)
signal purificacion_lanzada(posicion: Vector3)

# Parámetros físicos de movimiento
const VELOCIDAD := 4.5              # m/s al caminar
const VELOCIDAD_CORRER := 7.2       # m/s al correr
const VELOCIDAD_ESQUIVA := 10.5     # m/s durante el impulso de esquiva
const ACELERACION := 22.0
const FRICCION := 18.0
const GRAVEDAD := 16.0
const FUERZA_SALTO := 6.6
const ROTACION_SUAVE := 14.0

@export var vida_maxima := 5
var vida := 5
@export var puede_moverse := true

# Estados
var en_salto := false
var esquivando := false
var tiempo_esquiva := 0.0
const DURACION_ESQUIVA := 0.38
var cooldown_esquiva := 0.0

var atacando := false
var tiempo_ataque := 0.0
const DURACION_ATAQUE := 0.42

var _dir_esquiva := Vector3.ZERO
var _tiempo_paso := 0.0
var _visual: Node3D = null
var _luz_corazon: OmniLight3D = null


func _ready() -> void:
	vida = vida_maxima
	_visual = get_node_or_null("Visual")
	_luz_corazon = get_node_or_null("LuzCorazon")
	if not _luz_corazon and _visual:
		_luz_corazon = _visual.get_node_or_null("LuzCorazon")


func _physics_process(delta: float) -> void:
	# Gravedad con peso físico
	if not is_on_floor():
		velocity.y -= GRAVEDAD * delta
	else:
		if en_salto and velocity.y <= 0.0:
			en_salto = false

	# Cooldowns
	if cooldown_esquiva > 0.0:
		cooldown_esquiva -= delta

	# 1. Manejo de Esquiva rodando
	if esquivando:
		tiempo_esquiva -= delta
		velocity.x = _dir_esquiva.x * VELOCIDAD_ESQUIVA
		velocity.z = _dir_esquiva.z * VELOCIDAD_ESQUIVA
		if tiempo_esquiva <= 0.0:
			esquivando = false
		move_and_slide()
		return

	# 2. Manejo de Ataque con Cetro
	if atacando:
		tiempo_ataque -= delta
		velocity.x = move_toward(velocity.x, 0.0, FRICCION * delta)
		velocity.z = move_toward(velocity.z, 0.0, FRICCION * delta)
		if tiempo_ataque <= 0.0:
			atacando = false
		move_and_slide()
		return

	if not puede_moverse:
		velocity.x = move_toward(velocity.x, 0.0, FRICCION * delta)
		velocity.z = move_toward(velocity.z, 0.0, FRICCION * delta)
		move_and_slide()
		return

	# 3. Entrada de movimiento
	var input_dir := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo")
	var corriendo := Input.is_action_pressed("correr")
	var vel_objetivo := VELOCIDAD_CORRER if corriendo else VELOCIDAD

	# Proyección relativa a la orientación de la cámara
	var cam := get_viewport().get_camera_3d()
	var dir_3d := Vector3.ZERO
	if cam:
		var cam_fwd := -cam.global_transform.basis.z
		cam_fwd.y = 0.0
		cam_fwd = cam_fwd.normalized()
		var cam_right := cam.global_transform.basis.x
		cam_right.y = 0.0
		cam_right = cam_right.normalized()
		dir_3d = (cam_right * input_dir.x + cam_fwd * -input_dir.y).normalized()
	else:
		dir_3d = Vector3(input_dir.x, 0.0, input_dir.y).normalized()

	# 4. Salto libre con peso
	if is_on_floor() and Input.is_action_just_pressed("ui_accept"):
		velocity.y = FUERZA_SALTO
		en_salto = true

	# 5. Esquiva con botón de correr/rodar
	if is_on_floor() and Input.is_action_just_pressed("correr") and cooldown_esquiva <= 0.0:
		if dir_3d.length() > 0.1:
			esquivando = true
			tiempo_esquiva = DURACION_ESQUIVA
			cooldown_esquiva = 0.6
			_dir_esquiva = dir_3d
			if _visual:
				_visual.rotation.y = atan2(_dir_esquiva.x, _dir_esquiva.z)
			move_and_slide()
			return

	# 6. Desplazamiento en el plano XZ
	if dir_3d.length() > 0.1:
		velocity.x = move_toward(velocity.x, dir_3d.x * vel_objetivo, ACELERACION * delta)
		velocity.z = move_toward(velocity.z, dir_3d.z * vel_objetivo, ACELERACION * delta)

		# Orientación suave hacia la dirección de avance
		if _visual:
			var angulo_meta := atan2(dir_3d.x, dir_3d.z)
			_visual.rotation.y = lerp_angle(_visual.rotation.y, angulo_meta, ROTACION_SUAVE * delta)

		_tiempo_paso += delta * (14.0 if corriendo else 9.0)
		if _tiempo_paso > PI:
			_tiempo_paso = 0.0
			emit_signal("paso", global_position)
	else:
		velocity.x = move_toward(velocity.x, 0.0, FRICCION * delta)
		velocity.z = move_toward(velocity.z, 0.0, FRICCION * delta)

	# 7. Pulsación mágica del Corazón de Asili
	if _luz_corazon:
		var pulso := 0.9 + sin(Time.get_ticks_msec() * 0.0035) * 0.25
		_luz_corazon.light_energy = pulso

	move_and_slide()


func recibir_golpe(cantidad: int, origen: Vector3 = Vector3.ZERO) -> void:
	if esquivando:
		return # Invulnerabilidad en la esquiva
	vida = maxi(0, vida - cantidad)
	emit_signal("danio", vida)

	# Retroceso físico por impacto
	if origen != Vector3.ZERO:
		var dir_empuje := (global_position - origen).normalized()
		dir_empuje.y = 0.3
		velocity += dir_empuje * 5.5
