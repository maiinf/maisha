extends "res://scripts/mundo/escena_mundo.gd"
## CAÑADA DEL ECO: el camino del Bosque Cobrizo al Lago Espejo (el quinto de los caminos de Raíz).
## Una garganta entre dos paredes de peña, con mesetas de hierba encima; un arroyo baja hacia el lago y el camino
## lo cruza por un puentecito y un vado. MBUZI, la cabra montés pastora, vive en su aprisco del norte (encargo:
## tres cencerros que el eco esparció; al devolverlos descuelga la ESCALA DE CUERDA hasta la cornisa del quinto
## ECO PERDIDO). Una zona corrupta en el ensanche del sur y un secreto tras un matorral al noroeste.
## Al oeste, el paso al Lago Espejo (aún cerrado).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("canada_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("canada_llegada"):
		return
	Estado.marcar("canada_llegada")
	await CHARLA_SCRIPT.hablar(self, "canada_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡La Cañada del Eco vuelve a sonar a agua y a viento!")
