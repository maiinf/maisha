extends "res://scripts/mundo/escena_mundo.gd"
## PASO DE PIEDRA: el camino del Campo Segado (oeste) a la Gruta de las Raíces (este), entre dos paredes de peña.
## En un rellano del norte, la CASA DE NUNGU, el erizo científico, abandonada (por dentro: casa_nungu.gd, con el armario
## cerrado que lleva a la cueva de las setas). Una zona corrupta en el ensanche del sur, la cantera vieja al este y,
## al final, la maraña de raíces que tapa el paso a la Gruta (se aparta al despertar el Guardián).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("paso_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("paso_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "paso_llegada")
	Estado.marcar("paso_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Paso de Piedra vuelve a oler a tomillo!")
