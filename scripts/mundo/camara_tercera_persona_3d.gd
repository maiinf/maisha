extends Node3D
## CÁMARA TERCERA PERSONA LIBRE (ESTILO GOD OF WAR / ZELDA TOTK)
## Orbita en 360° con ratón o stick, brazo elástico anticolisión (SpringArm3D),
## encuadre cinematográfico sobre el hombro y fijación de objetivo (Lock-on).

@export var objetivo_path: NodePath
@export var sensibilidad_raton := 0.0025
@export var suavidad_seguimiento := 14.0
@export var distancia_camara := 3.6
@export var altura_pivote := 1.45
@export var desplazamiento_hombro := 0.45   # Desplaza la cámara a la derecha para ver sobre el hombro

@export var limite_pitch_min := -45.0       # Ángulo mínimo al mirar hacia arriba (grados)
@export var limite_pitch_max := 65.0        # Ángulo máximo al mirar hacia abajo

var _objetivo: Node3D = null
var _yaw := 0.0
var _pitch := -12.0
var _camara: Camera3D = null
var _spring_arm: SpringArm3D = null
var _bloqueo_raton := true

# Lock-on
var objetivo_fijado: Node3D = null


func _ready() -> void:
	if not objetivo_path.is_empty():
		_objetivo = get_node_or_null(objetivo_path)

	# Crear estructura de brazo elástico y cámara si no existen
	_configurar_brazo_y_camara()

	# Capturar ratón para control libre
	if _bloqueo_raton:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	# Liberar/capturar ratón con ESCAPE
	if event.is_action_pressed("ui_cancel"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		return

	# Rotación orbital con ratón
	if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and event is InputEventMouseMotion:
		_yaw -= event.relative.x * sensibilidad_raton
		_pitch -= event.relative.y * sensibilidad_raton
		_pitch = clampf(_pitch, deg_to_rad(limite_pitch_min), deg_to_rad(limite_pitch_max))


func _physics_process(delta: float) -> void:
	if not _objetivo:
		if not objetivo_path.is_empty():
			_objetivo = get_node_or_null(objetivo_path)
		return

	# Si hay objetivo fijado (Lock-on), la cámara se orienta automáticamente hacia el enemigo
	if is_instance_valid(objetivo_fijado):
		var dir_hacia_enemigo := (objetivo_fijado.global_position - _objetivo.global_position).normalized()
		var yaw_meta := atan2(-dir_hacia_enemigo.x, -dir_hacia_enemigo.z)
		_yaw = lerp_angle(_yaw, yaw_meta, 8.0 * delta)
		_pitch = lerpf(_pitch, deg_to_rad(-8.0), 6.0 * delta)

	# Posición de seguimiento suave al objetivo (a la altura de los hombros)
	var pos_meta := _objetivo.global_position + Vector3(0, altura_pivote, 0)
	global_position = global_position.lerp(pos_meta, suavidad_seguimiento * delta)

	# Aplicar rotación orbital
	rotation.y = _yaw
	if _spring_arm:
		_spring_arm.rotation.x = _pitch


func _configurar_brazo_y_camara() -> void:
	_spring_arm = get_node_or_null("SpringArm3D")
	if not _spring_arm:
		_spring_arm = SpringArm3D.new()
		_spring_arm.name = "SpringArm3D"
		_spring_arm.spring_length = distancia_camara
		_spring_arm.margin = 0.25
		add_child(_spring_arm)

	_camara = _spring_arm.get_node_or_null("Camera3D")
	if not _camara:
		_camara = Camera3D.new()
		_camara.name = "Camera3D"
		_camara.fov = 68.0
		# Desplazamiento sobre el hombro
		_camara.transform.origin = Vector3(desplazamiento_hombro, 0.15, 0)
		_spring_arm.add_child(_camara)

	_camara.current = true
