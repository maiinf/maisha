extends "res://scripts/mundo/escena_mundo.gd"
## ORILLA DE JUNCOS: el camino de la Ciénaga Quieta (sur) al Embarcadero Junco (norte; todavía cerrado), el sexto
## de los caminos de Raíz. Por el este baja el río ancho, con playas de arena y juncos; en medio, un banco de arena
## con el sexto ECO PERDIDO. KASIA, la nutria barquera, vive en su casa de barcas, en la orilla (encargo: tres remos
## que la corriente se llevó y que han ido pescando los cangrejos; al devolverlos saca su BALSA del agua, y la balsa
## cruza a Maisha al banco de arena). Los CANGREJOS DE HERRUMBRE (enemigo nuevo) en una zona corrupta de la playa del
## sur, y un secreto entre los juncos del noroeste.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("orilla_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("orilla_llegada"):
		return
	Estado.marcar("orilla_llegada")
	await CHARLA_SCRIPT.hablar(self, "orilla_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡La Orilla de Juncos vuelve a sonar a agua y a ranas!")
