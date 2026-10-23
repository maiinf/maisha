extends CharacterBody3D
## MAISHA 3D: Controlador en tercera persona AAA (God of War / Zelda TotK).
## Movimiento relativo a cámara orbital, salto libre con peso, esquiva rodando,
## combate táctico de cetro con hit-box y latido de luz del Corazón de Asili.

signal danio(vida_actual: int)
signal paso(posicion: Vector3)
signal purificacion_lanzada(posicion: Vector3)
signal cetro_golpe(impacto: Vector3)

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

# Estados de acción
var en_salto := false
var esquivando := false
var tiempo_esquiva := 0.0
const DURACION_ESQUIVA := 0.38
var cooldown_esquiva := 0.0

var atacando := false
var tiempo_ataque := 0.0
const DURACION_ATAQUE := 0.55       # lo que dura el barrido del cetro (la animación va acelerada a ese tiempo)
var cooldown_ataque := 0.0

## Tatuajes de la Memoria: 0 = dormidos (al despertar en el Kitovu), 1 = despiertos del todo (los 9 Ecos).
@export_range(0.0, 1.0) var memoria := 0.0
const BRILLO_TATUAJES := 1.5        # emisión de los tatuajes despiertos (ficha: tatuajes_memoria_activos)
const ECOS_TOTALES := 9

# Animaciones del modelo (modelos/personajes/maisha.glb): reposo, caminar_atento, correr, golpe_cetro,
# idle_mirar_tatuajes, eco_despertar, esquivar_rodando, saltar, aterrizar y trepar (esta, para cuando haya
# escalada). Velocidades naturales de cada ciclo, para que los pies no patinen.
const PASO_CAMINAR := 1.35          # m/s a los que el ciclo de caminar va a velocidad 1
const PASO_CORRER := 3.3            # m/s a los que el ciclo de correr va a velocidad 1
const QUIETO_PARA_MIRAR := 8.0      # segundos sin moverse antes de mirarse los tatuajes

var _dir_esquiva := Vector3.ZERO
var _tiempo_paso := 0.0
var _visual: Node3D = null
var _luz_corazon: OmniLight3D = null
var _audio_cetro: AudioStreamPlayer3D = null
var _anim: AnimationPlayer = null
var _piel: BaseMaterial3D = null
var _tiempo_quieto := 0.0
var _en_el_aire := false


func _ready() -> void:
	add_to_group("jugador")
	vida = vida_maxima
	_visual = get_node_or_null("Visual")
	_luz_corazon = get_node_or_null("LuzCorazon")
	if not _luz_corazon and _visual:
		_luz_corazon = _visual.get_node_or_null("LuzCorazon")

	_audio_cetro = AudioStreamPlayer3D.new()
	var snd := load("res://audio/sonidos/cetro_golpe.ogg")
	if snd:
		_audio_cetro.stream = snd
	_audio_cetro.max_distance = 25.0
	add_child(_audio_cetro)

	if _visual:
		var reproductores := _visual.find_children("*", "AnimationPlayer", true, false)
		if not reproductores.is_empty():
			_anim = reproductores[0]
			for ciclo in ["reposo", "caminar_atento", "correr", "trepar"]:
				if _anim.has_animation(ciclo):
					_anim.get_animation(ciclo).loop_mode = Animation.LOOP_LINEAR
		_preparar_piel()
	despertar_memoria(memoria)
	_animar("reposo")


## Cada Maisha lleva su propia copia del material de piel, para encender sus tatuajes sin tocar el modelo.
func _preparar_piel() -> void:
	for nodo in _visual.find_children("*", "MeshInstance3D", true, false):
		var malla := nodo as MeshInstance3D
		for i in malla.mesh.get_surface_count():
			var mat := malla.mesh.surface_get_material(i) as BaseMaterial3D
			if mat and mat.resource_name == "piel_humanizada":
				_piel = mat.duplicate()
				malla.set_surface_override_material(i, _piel)
				return


## Enciende los tatuajes: 0 = dormidos, 1 = toda la cartografía en oro.
func despertar_memoria(valor: float) -> void:
	memoria = clampf(valor, 0.0, 1.0)
	if _piel:
		_piel.emission_energy_multiplier = BRILLO_TATUAJES * memoria


## Al recuperar un Eco: la animación del despertar y un noveno más de brillo en los tatuajes.
func recuperar_eco() -> void:
	_animar("eco_despertar", 1.0, 0.3)
	var meta := minf(1.0, memoria + 1.0 / ECOS_TOTALES)
	create_tween().tween_method(despertar_memoria, memoria, meta, 1.2).set_delay(0.4)


func _animar(nombre: String, velocidad := 1.0, mezcla := 0.25) -> void:
	if not _anim or not _anim.has_animation(nombre):
		return
	_anim.speed_scale = velocidad
	if _anim.current_animation != nombre:
		_anim.play(nombre, mezcla)


func _process(delta: float) -> void:
	if not _anim or atacando:
		return
	var rapidez := Vector2(velocity.x, velocity.z).length()
	var en_suelo := is_on_floor()
	if esquivando:
		# la voltereta entera dura lo que dura el impulso de la esquiva
		var largo := _anim.get_animation("esquivar_rodando").length if _anim.has_animation("esquivar_rodando") else 1.0
		_animar("esquivar_rodando", largo / DURACION_ESQUIVA, 0.05)
		return
	if not en_suelo:
		_en_el_aire = true
		_animar("saltar", 1.0, 0.1)   # se agacha, se impulsa y se queda en la pose de vuelo
		return
	if _en_el_aire:
		_en_el_aire = false
		_animar("aterrizar", 1.0, 0.05)
		return
	var unica := _anim.current_animation in ["idle_mirar_tatuajes", "eco_despertar", "aterrizar"]
	if unica and _anim.is_playing() and rapidez < 0.3:
		return
	if rapidez > 0.3:
		_tiempo_quieto = 0.0
		if rapidez > 2.2:
			_animar("correr", clampf(rapidez / PASO_CORRER, 0.8, 2.2), 0.2)
		else:
			_animar("caminar_atento", clampf(rapidez / PASO_CAMINAR, 0.6, 1.6), 0.2)
	else:
		_tiempo_quieto += delta
		if _tiempo_quieto > QUIETO_PARA_MIRAR:
			_tiempo_quieto = -QUIETO_PARA_MIRAR  # no repetirlo enseguida
			_animar("idle_mirar_tatuajes", 1.0, 0.4)
		else:
			_animar("reposo", 1.0, 0.3)


func _unhandled_input(event: InputEvent) -> void:
	# Ataque con Click Izquierdo del ratón o tecla J
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_intentar_ataque()
	elif event is InputEventKey and event.keycode == KEY_J and event.pressed:
		_intentar_ataque()


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
	if cooldown_ataque > 0.0:
		cooldown_ataque -= delta

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


func _intentar_ataque() -> void:
	if atacando or esquivando or cooldown_ataque > 0.0 or not puede_moverse:
		return

	atacando = true
	tiempo_ataque = DURACION_ATAQUE
	cooldown_ataque = 0.45
	if _anim and _anim.has_animation("golpe_cetro"):
		_anim.speed_scale = _anim.get_animation("golpe_cetro").length / DURACION_ATAQUE
		_anim.play("golpe_cetro", 0.08)
		_anim.seek(0.0, true)

	if _audio_cetro:
		_audio_cetro.play()

	# Detección de impacto en abanico frontal (1.7 metros)
	var espacio := get_world_3d().direct_space_state
	var frente := -global_transform.basis.z if not _visual else Vector3(sin(_visual.rotation.y), 0, cos(_visual.rotation.y))
	var centro_golpe := global_position + frente * 1.35 + Vector3(0, 0.7, 0)

	var query := PhysicsShapeQueryParameters3D.new()
	var esfera := SphereShape3D.new()
	esfera.radius = 1.2
	query.shape = esfera
	query.transform = Transform3D(Basis(), centro_golpe)
	query.collision_mask = 4 | 1 # Capa de enemigos y objetos interactuables

	var resultados := espacio.intersect_shape(query, 8)
	for r in resultados:
		var collider: Object = r.collider
		if collider and collider != self:
			if collider.has_method("recibir_ataque"):
				collider.recibir_ataque(1, global_position)
				emit_signal("cetro_golpe", centro_golpe)


func recibir_golpe(cantidad: int, origen: Vector3 = Vector3.ZERO) -> void:
	if esquivando:
		return # Invulnerabilidad durante la esquiva
	vida = maxi(0, vida - cantidad)
	emit_signal("danio", vida)

	# Retroceso físico por impacto
	if origen != Vector3.ZERO:
		var dir_empuje := (global_position - origen).normalized()
		dir_empuje.y = 0.3
		velocity += dir_empuje * 5.5
