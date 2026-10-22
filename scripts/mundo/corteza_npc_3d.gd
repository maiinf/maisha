extends Node3D
## CORTEZA NPC 3D (LA MAESTRA HERRERA TELÚRICA DE CUNA DE MUSGO)
## Guardiana de la Forja de Raíz, experta en templar madera sagrada y forjar cetros.
## Interacción con [E] y encuadre cinematográfico.

@export var distancia_hablar := 3.2

var _maisha: CharacterBody3D = null
var _dialogo_ui: CanvasLayer = null
var _jugador_cerca := false


func _ready() -> void:
	_dialogo_ui = get_parent().get_node_or_null("DialogoCinematico3D")


func _process(delta: float) -> void:
	if not is_instance_valid(_maisha):
		_maisha = get_parent().get_node_or_null("Maisha3D")
		return

	var dist := global_position.distance_to(_maisha.global_position)
	if dist <= distancia_hablar:
		if not _jugador_cerca:
			_jugador_cerca = true
			if _dialogo_ui and not _dialogo_ui.hablando:
				_dialogo_ui.mostrar_prompt("[E] Hablar con Corteza")

		# Girar con aplomo hacia Maisha durante el diálogo
		if _dialogo_ui and _dialogo_ui.hablando:
			var dir := (_maisha.global_position - global_position).normalized()
			dir.y = 0.0
			if dir.length() > 0.01:
				rotation.y = lerp_angle(rotation.y, atan2(dir.x, dir.z), 5.0 * delta)
	else:
		if _jugador_cerca:
			_jugador_cerca = false
			if _dialogo_ui:
				_dialogo_ui.ocultar_prompt()


func _unhandled_input(event: InputEvent) -> void:
	if not _jugador_cerca or not is_instance_valid(_dialogo_ui):
		return

	if _dialogo_ui.hablando:
		return

	if event is InputEventKey and event.keycode == KEY_E and event.pressed:
		_iniciar_conversacion()


func _iniciar_conversacion() -> void:
	_dialogo_ui.ocultar_prompt()
	var cam := get_parent().get_node_or_null("CamaraTerceraPersona")

	var lineas: Array[String] = [
		"Hmpf. Da un paso atrás si no quieres que te salte una chispa a la túnica.",
		"...Espera. Déjame ver ese leño que empuñas.",
		"Madera de roble milenario con una semilla de vida en la espiral de la contera. Es un Cetro de Raíz auténtico de la época previa al cataclismo.",
		"Soy Corteza. Forjadora de estas tierras. Mientras el fuego de esta fragua respire, ningún alma se quedará sin filo contra la oscuridad.",
		"Giza intentó asfixiar mi fuelle con costras de mineral corrupto, pero el fuego telúrico es más terco que su ceniza.",
		"Conforme recorras los biomas y derrotes a las aberraciones de Giza, tráeme brotes de hierro meteórico y ámbar fósil.",
		"Puedo templar tu báculo para aumentar la contundencia del impacto y tallar runas de ignición en la contera. Ahora muéstrame de qué pasta estás hecho."
	]

	_dialogo_ui.iniciar_dialogo("Corteza", lineas, cam, _maisha)
