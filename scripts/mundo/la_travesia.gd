extends "res://scripts/mundo/escena_mundo.gd"
## LA TRAVESÍA: el río río arriba, del Embarcadero Junco a la Gruta de las Raíces. No se anda: se viaja en el
## transbordador con Bata (scripts/mundo/travesia/viaje.gd). A media subida, una isla (el séptimo eco); arriba, el
## muelle de piedra de la Gruta.

const VIAJE := preload("res://scripts/mundo/travesia/viaje.gd")


func _ready() -> void:
	super()
	var viaje: Node2D = VIAJE.new()
	viaje.name = "Viaje"
	$Entidades.add_child(viaje)
	_maisha.caida.connect(_al_caer)


## Si Maisha cae en el viaje, vuelve en la cubierta (y lo que había a bordo se va)
func _al_caer() -> void:
	_hud.fundido(func() -> void:
		for e in get_tree().get_nodes_in_group("enemigos"):
			e.queue_free()
		var viaje: Node2D = $Entidades/Viaje
		_maisha.revivir(viaje.position + Vector2(0, -6)))
