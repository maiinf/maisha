extends Node3D
## MZEE SHAMBA NPC 3D (EL SABIO Y CULTO BOTÁNICO DE EL KITOVU)
## Interacción conversacional con Maisha, detección de proximidad y
## activación del sistema de subtítulos cinematográficos en tiempo real.

@export var distancia_hablar := 3.0

var _maisha: CharacterBody3D = null
var _dialogo_ui: CanvasLayer = null
var _jugador_cerca := false


func _ready() -> void:
	# Buscar el sistema de diálogo cinematográfico en la escena
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
				_dialogo_ui.mostrar_prompt("[E] Hablar con Mzee Shamba")

		# Girar suavemente hacia Maisha al hablar
		if _dialogo_ui and _dialogo_ui.hablando:
			var dir := (_maisha.global_position - global_position).normalized()
			dir.y = 0.0
			if dir.length() > 0.01:
				rotation.y = lerp_angle(rotation.y, atan2(dir.x, dir.z), 6.0 * delta)
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
		"¡Alto ahí! ¿Quién anda rondando mi granja con esos pasos cautelosos?",
		"...Un momento. Esos grabados mnemotécnicos en tus brazos... No eres una sombra de Giza. Eres... un espíritu de la vida.",
		"Perdona a este viejo castor botánico. Desde que el mundo se volvió gris, por aquí ya solo merodean cosas marchitas.",
		"Soy Mzee Shamba. Cuido de las semillas y de estas raíces sagradas desde mucho antes de la gran caída.",
		"¿Que buscas el origen de tu despertar? Más allá de ese arco de madera antigua yace La Raíz, el corazón del bosque.",
		"Aquel arco es el Portal de Raíz. Primero debes purificar el nudo de corrupción que asfixia la tierra para que sus ramas vuelvan a abrirse.",
		"Pasa por mi casa cuando el camino se haga frío: junto a la lumbre siempre habrá un cuenco de sopa de zanahorias calientes para ti."
	]

	_dialogo_ui.iniciar_dialogo("Mzee Shamba", lineas, cam, _maisha)
