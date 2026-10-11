extends "res://scripts/mundo/escena_mundo.gd"
## CAMINO COBRIZO: el camino de los Prados del Eco al Bosque Cobrizo (el tercero de los caminos de Raíz).
## Sube de sur a norte: el prado verde se va volviendo bosque cobrizo y el suelo se llena de hojas. Un arroyo con
## un puentecito; la madriguera de FUKO, el topo minero (encargo: tres campanillas de cobre; al devolverlas despeja
## el DERRUMBE de la vieja galería); los TOPOS DE PIEDRA (enemigo nuevo) en una zona corrupta al oeste; un secreto
## entre los árboles del noroeste y, tras la peña de la mina, el tercer ECO PERDIDO.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("cobrizo_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("cobrizo_llegada"):
		return
	Estado.marcar("cobrizo_llegada")
	await CHARLA_SCRIPT.hablar(self, "cobrizo_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Camino Cobrizo vuelve a brillar entre las hojas!")
