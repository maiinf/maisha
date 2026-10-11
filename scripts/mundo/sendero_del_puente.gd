extends "res://scripts/mundo/escena_mundo.gd"
## SENDERO DEL PUENTE: el camino de los Prados del Eco a Cuna de Musgo (el primero de los caminos de Raíz).
## Prado con el campamento de Msafiri, el pangolín viajero (encargo: tres páginas de su diario); el Río Lento con
## el gran PUENTE DE PIEDRA de los antiguos; bajo el puente, el vado y el islote con el primer ECO PERDIDO;
## una zona corrupta junto al camino y, al norte, las ruinas de quienes construyeron el puente (con un secreto).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("sendero_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("sendero_llegada"):
		return
	Estado.marcar("sendero_llegada")
	await CHARLA_SCRIPT.hablar(self, "sendero_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Sendero del Puente vuelve a tener color!")
