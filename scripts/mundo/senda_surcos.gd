extends "res://scripts/mundo/escena_mundo.gd"
## SENDA DE LOS SURCOS: el camino de Cuna de Musgo al Campo Segado (el cuarto de los caminos de Raíz).
## Huertas viejas, vallas y pacas; una ACEQUIA con un puentecito que sube por el este hasta un huerto rodeado de
## agua, con el cuarto ECO PERDIDO. SUNGURA, la liebre guardasemillas, vive en un hórreo junto a la acequia
## (encargo: tres mazorcas antiguas; al devolverlas cierra la compuerta y el foso del huerto se vacía).
## Los CUERVOS DE ÓXIDO (enemigo nuevo) en una zona corrupta al este, y un secreto en el seto del oeste.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("surcos_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("surcos_llegada"):
		return
	Estado.marcar("surcos_llegada")
	await CHARLA_SCRIPT.hablar(self, "surcos_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡La Senda de los Surcos vuelve a oler a tierra buena!")
