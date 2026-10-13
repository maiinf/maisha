extends "res://scripts/mundo/escena_mundo.gd"
## LA GRUTA DE LAS RAÍCES: una cueva por dentro, al final de La Travesía (las raíces de la boca se apartan con la hoja
## de Mauti). A oscuras (scripts/mundo/gruta/oscuridad.gd): solo alumbran Maisha, las semillas dormidas de los nichos
## y las huellas lilas de Mauti, que llevan al fondo. Salas: el vestíbulo de las semillas, el pasillo de las raíces
## dormidas, el santuario de corteza (el escudo), la galería de las espinas y el fondo, donde algo duerme.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")


func _ready() -> void:
	super()
	var oscuridad: Node2D = OSCURIDAD.new()
	oscuridad.name = "Oscuridad"
	add_child(oscuridad)
	_maisha.caida.connect(_al_caer)
	if not Estado.tiene("gruta_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.5).timeout
	if not is_inside_tree() or Estado.tiene("gruta_llegada"):
		return
	Estado.marcar("gruta_llegada")
	await CHARLA_SCRIPT.hablar(self, "gruta_llegada")


func _al_caer() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))
