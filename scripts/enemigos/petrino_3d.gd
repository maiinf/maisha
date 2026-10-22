extends CharacterBody3D
## PETRINO 3D: Esbirro rocoso corrompido por Giza.
## Embestida pesada con inercia, aturdimiento contra obstáculos,
## sonido espacial y desintegración en esquirlas de roca purificada.

signal vencido(posicion: Vector3)

enum FasePetrino { IDLE, ALERTA, EMBESTIDA, ATURDIDO, MUERTE }

@export var vida_maxima := 3
var vida := 3
var fase := FasePetrino.IDLE

const VELOCIDAD_PATRULLA := 1.8
const VELOCIDAD_EMBESTIDA := 12.0
const GRAVEDAD := 16.0
const RANGO_DETECCION := 10.5

var _jugador: Node3D = null
var _tiempo_estado := 0.0
var _dir_embestida := Vector3.ZERO
var _visual: Node3D = null
var _audio: AudioStreamPlayer3D = null
var _luz_ojos: OmniLight3D = null


func _ready() -> void:
	vida = vida_maxima
	_visual = get_node_or_null("Visual")
	_audio = AudioStreamPlayer3D.new()
	_audio.max_distance = 25.0
	add_child(_audio)

	# Luz violeta de corrupción en los ojos
	_luz_ojos = OmniLight3D.new()
	_luz_ojos.light_color = Color(0.75, 0.25, 0.95)
	_luz_ojos.light_energy = 1.8
	_luz_ojos.omni_range = 3.5
	_luz_ojos.transform.origin = Vector3(0, 0.7, 0.4)
	add_child(_luz_ojos)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= GRAVEDAD * delta
	else:
		velocity.y = 0.0

	if fase == FasePetrino.MUERTE:
		move_and_slide()
		return

	# Buscar a Maisha si no lo tiene localizado
	if not is_instance_valid(_jugador):
		var arbol_nodos := get_tree().get_nodes_in_group("jugador")
		if arbol_nodos.size() > 0:
			_jugador = arbol_nodos[0]
		else:
			var nodo_maisha := get_parent().get_node_or_null("Maisha3D")
			if nodo_maisha:
				_jugador = nodo_maisha

	_tiempo_estado += delta

	match fase:
		FasePetrino.IDLE:
			velocity.x = move_toward(velocity.x, 0.0, 10.0 * delta)
			velocity.z = move_toward(velocity.z, 0.0, 10.0 * delta)
			if is_instance_valid(_jugador):
				var dist := global_position.distance_to(_jugador.global_position)
				if dist <= RANGO_DETECCION:
					_cambiar_fase(FasePetrino.ALERTA)

		FasePetrino.ALERTA:
			# Rugido de advertencia y fijar dirección
			velocity.x = 0.0
			velocity.z = 0.0
			var dir := (_jugador.global_position - global_position).normalized()
			dir.y = 0.0
			if dir.length() > 0.01 and _visual:
				_visual.rotation.y = lerp_angle(_visual.rotation.y, atan2(dir.x, dir.z), 12.0 * delta)

			if _tiempo_estado >= 0.75:
				_dir_embestida = (_jugador.global_position - global_position).normalized()
				_dir_embestida.y = 0.0
				_reproducir_sonido("res://audio/sonidos/petrino_embiste.ogg")
				_cambiar_fase(FasePetrino.EMBESTIDA)

		FasePetrino.EMBESTIDA:
			velocity.x = _dir_embestida.x * VELOCIDAD_EMBESTIDA
			velocity.z = _dir_embestida.z * VELOCIDAD_EMBESTIDA

			# Colisión frontal
			if is_on_wall() or _tiempo_estado >= 1.4:
				_reproducir_sonido("res://audio/sonidos/piedra_rompe.ogg")
				_cambiar_fase(FasePetrino.ATURDIDO)

			# Daño al jugador si impacta
			if is_instance_valid(_jugador):
				if global_position.distance_to(_jugador.global_position) < 1.35:
					if _jugador.has_method("recibir_golpe"):
						_jugador.recibir_golpe(1, global_position)
					_cambiar_fase(FasePetrino.ATURDIDO)

		FasePetrino.ATURDIDO:
			velocity.x = move_toward(velocity.x, 0.0, 18.0 * delta)
			velocity.z = move_toward(velocity.z, 0.0, 18.0 * delta)
			if _tiempo_estado >= 2.2:
				_cambiar_fase(FasePetrino.IDLE)

	move_and_slide()


func recibir_ataque(danio_cetro: int, origen: Vector3 = Vector3.ZERO) -> void:
	if fase == FasePetrino.MUERTE:
		return

	vida = maxi(0, vida - danio_cetro)
	_reproducir_sonido("res://audio/sonidos/petrino_golpeado.ogg")

	# Retroceso físico por el impacto del Cetro
	if origen != Vector3.ZERO:
		var dir_retroceso := (global_position - origen).normalized()
		dir_retroceso.y = 0.15
		velocity = dir_retroceso * 7.0

	_cambiar_fase(FasePetrino.ATURDIDO)

	if vida <= 0:
		_morir()


func _morir() -> void:
	fase = FasePetrino.MUERTE
	_reproducir_sonido("res://audio/sonidos/petrino_muere.ogg")
	emit_signal("vencido", global_position)

	# Onda dorada de purificación al disolverse
	var escena_onda := load("res://escenas/efectos/onda_purificacion_3d.tscn")
	if escena_onda:
		var onda: Node3D = escena_onda.instantiate()
		onda.global_position = global_position
		onda.radio_maximo = 6.0
		get_parent().add_child(onda)

	# Desvanecer visual
	if _luz_ojos:
		_luz_ojos.queue_free()

	var tween := create_tween()
	tween.tween_property(self, "scale", Vector3.ZERO, 0.45).set_ease(Tween.EASE_IN)
	tween.tween_callback(queue_free)


func _cambiar_fase(nueva: FasePetrino) -> void:
	fase = nueva
	_tiempo_estado = 0.0


func _reproducir_sonido(ruta: String) -> void:
	var snd := load(ruta)
	if snd and _audio:
		_audio.stream = snd
		_audio.play()
