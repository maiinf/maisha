extends Node3D
## PINO NPC 3D (EL EXPLORADOR DE CUNA DE MUSGO)
## Joven explorador leal y curioso con su icónico sombrero de seta roja.
## Interacción con [E] y subtítulos cinematográficos sobre el hombro.

@export var distancia_hablar := 3.0

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
				_dialogo_ui.mostrar_prompt("[E] Hablar con Pino")

		# Girar suavemente hacia Maisha durante el diálogo
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
		"¡Eh! ¡Mira qué porte! ¡Por las esporas sagradas, estás de una pieza!",
		"¡Soy Pino! El explorador y vigía oficial de Cuna de Musgo.",
		"Estuve atrapado en una costra de piedra gris durante quién sabe cuántas lunas... ¡Ser de piedra es lo más aburrido que existe! ¡Ni rascarse la nariz!",
		"Pero cuando purificaste el Kitovu, sentí un cosquilleo cálido en los pies y... ¡pum!, la piedra se desmoronó.",
		"Esa de ahí es mi casa con tejado de seta roja. Desde el tejado vigilo los senderos que conducen al Bosque Cobrizo y la Ciénaga Quieta.",
		"Ten cuidado al adentrarte en la maleza: las bestias petrificadas de Giza se despiertan si escuchan pasos pesados. ¡Usa tu esquiva rodando y tu báculo!",
		"Si ves algo brillante entre los helechos... ¡es mío! Bueno, o de los dos. ¡Buena suerte, compañero!"
	]

	_dialogo_ui.iniciar_dialogo("Pino", lineas, cam, _maisha)
