extends "res://scripts/mundo/escena_mundo.gd"
## LAGO ESPEJO: un lugar al oeste de la Cañada del Eco (se llega al escuchar el quinto eco).
## Un lago grande con una ISLA en el centro, donde aparecerá KIMYA, la Quietud. Su agua está TURBIA mientras vive
## KAMBARE, el siluro de cieno (en la orilla sur). Sin él, si Maisha se queda quieta junto al agua, el lago se vuelve
## ESPEJO y lo que solo existe en el reflejo se hace real: el puente de luz hasta la isla y el del islote del secreto
## (scripts/mundo/lago/espejo_lago.gd y scripts/mundo/objetos/puente_reflejo.gd).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESPEJO := preload("res://scripts/mundo/lago/espejo_lago.gd")


func _ready() -> void:
	super()
	var espejo: Node2D = ESPEJO.new()
	espejo.name = "Espejo"
	$Region.add_child(espejo)
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("lago_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_al_poner_marca_lago)


func _al_poner_marca_lago(marca: String) -> void:
	if marca != "kambare_vencido":
		return
	await get_tree().create_timer(6.0).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "lago_kambare_libre")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("lago_llegada"):
		return
	Estado.marcar("lago_llegada")
	await CHARLA_SCRIPT.hablar(self, "lago_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Lago Espejo vuelve a reflejar el cielo!")
