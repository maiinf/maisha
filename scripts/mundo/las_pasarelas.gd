extends "res://scripts/mundo/escena_mundo.gd"
## LAS PASARELAS: el camino de Cuna de Musgo a la Ciénaga Quieta (el segundo de los caminos de Raíz).
## Un prado inundado de agua clara que se cruza por pasarelas de tablas entre islotes. El palafito de Korongo,
## la garza pescadora (encargo: tres nasas; al devolverlas arregla la pasarela rota del sureste), las RANAS DE
## PIEDRA (enemigo nuevo), una zona corrupta en el islote grande, un secreto en el islote del sur y el segundo ECO.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("pasarelas_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("pasarelas_llegada"):
		return
	Estado.marcar("pasarelas_llegada")
	await CHARLA_SCRIPT.hablar(self, "pasarelas_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡Las Pasarelas vuelven a brillar sobre el agua!")
