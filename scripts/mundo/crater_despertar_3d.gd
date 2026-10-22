extends Node3D
## CRÁTER DEL DESPERTAR 3D (EL KITOVU)
## Lugar de impacto de la chispa cósmica de Asili. Sus glifos ancestrales grabados
## en la roca madre laten en sincronía con los tatuajes mnemotécnicos de Maisha.

@onready var luz_crater: OmniLight3D = get_node_or_null("LuzCrater")

var _tiempo := 0.0
var _maisha: CharacterBody3D = null


func _ready() -> void:
	pass


func _process(delta: float) -> void:
	_tiempo += delta
	# Latido orgánico tenue de energía telúrica
	if is_instance_valid(luz_crater):
		var pulso := 1.2 + 0.45 * sin(_tiempo * 2.2)
		luz_crater.light_energy = pulso

	if not is_instance_valid(_maisha):
		_maisha = get_parent().get_node_or_null("Maisha3D")
