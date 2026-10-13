extends "res://scripts/mundo/escena_mundo.gd"
## EMBARCADERO JUNCO: el puerto del río de Raíz, al norte de la Orilla de Juncos (se llega al escuchar el sexto eco).
## En la orilla del oeste, el pueblo de barqueros: casas de juncos sobre pilotes, pasarelas, un almacén y una grúa
## rota. Arriba, el muelle del norte con el TRANSBORDADOR varado, que un día llevaba río arriba (La Travesía, cerrada
## hasta que vuelva a navegar). Abajo, la DÁRSENA, con su plataforma de madera y cuatro postes de amarre: allí
## acecha MAMBA, el cocodrilo de herrumbre (scripts/enemigos/mamba.gd); junto a ella, BATA, el pato barquero, de piedra.
## Tres zonas corruptas y tres secretos.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("embarcadero_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_al_poner_marca_embarcadero)


func _al_poner_marca_embarcadero(marca: String) -> void:
	if marca != "mamba_vencido":
		return
	await get_tree().create_timer(6.0).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "embarcadero_mamba_libre")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("embarcadero_llegada"):
		return
	Estado.marcar("embarcadero_llegada")
	await CHARLA_SCRIPT.hablar(self, "embarcadero_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Embarcadero Junco vuelve a oler a río y a madera mojada!")
