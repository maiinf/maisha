extends Node3D
## ALTAR DE LA RAÍZ SAGRADA 3D (CUNA DE MUSGO)
## Santuario milenario al pie del Gran Árbol donde Maisha comulga con el espíritu
## del bosque, despertando sus tatuajes mnemotécnicos y escuchando ecos ancestrales.

@export var distancia_comulgar := 3.5

var _maisha: CharacterBody3D = null
var _dialogo_ui: CanvasLayer = null
var _jugador_cerca := false
var _comulgado := false

@onready var luz_altar: OmniLight3D = $LuzAltar


func _ready() -> void:
	_dialogo_ui = get_parent().get_node_or_null("DialogoCinematico3D")


func _process(delta: float) -> void:
	if not is_instance_valid(_maisha):
		_maisha = get_parent().get_node_or_null("Maisha3D")
		return

	# Suave pulso rítmico de luz sagrada
	if luz_altar:
		var t := Time.get_ticks_msec() / 1000.0
		luz_altar.light_energy = 2.0 + 0.8 * sin(t * 1.8)

	var dist := global_position.distance_to(_maisha.global_position)
	if dist <= distancia_comulgar:
		if not _jugador_cerca:
			_jugador_cerca = true
			if _dialogo_ui and not _dialogo_ui.hablando:
				var prompt_texto := "[E] Comulgar con la Raíz Sagrada" if not _comulgado else "[E] Escuchar el susurro del Gran Árbol"
				_dialogo_ui.mostrar_prompt(prompt_texto)
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
		_iniciar_comunion()


func _iniciar_comunion() -> void:
	_dialogo_ui.ocultar_prompt()
	var cam := get_parent().get_node_or_null("CamaraTerceraPersona")

	var lineas: Array[String] = []
	if not _comulgado:
		_comulgado = true
		lineas = [
			"...Un murmullo profundo de savia ancestral resuena bajo la corteza del Gran Árbol.",
			"Tus manos rozan las hendiduras milenarias de la madera... y los tatuajes de tus brazos se encienden con un destello ambarino.",
			"«Hiciste esta promesa antes del cataclismo... cuando el mundo aún recordaba el calor del alba.»",
			"«No dejes que el miedo petrifique el último brote. Despierta a los durmientes de los prados.»",
			"El calor del Corazón de Asili late al unísono con el bosque. Tu energía vital se ha restaurado por completo."
		]
	else:
		lineas = [
			"El Gran Árbol respira sereno. La savia dorada fluye con vigor por sus raíces.",
			"«Hacia el norte se alza el Bosque Cobrizo; hacia el este, las aguas místicas de la Ciénaga Quieta aguardan tu paso.»"
		]

	_dialogo_ui.iniciar_dialogo("Gran Árbol Sagrado", lineas, cam, _maisha)
