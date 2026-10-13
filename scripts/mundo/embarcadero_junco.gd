extends "res://scripts/mundo/escena_mundo.gd"
## EMBARCADERO JUNCO: el puerto del río de Raíz, al norte de la Orilla de Juncos (se llega al escuchar el sexto eco).
## En la orilla del oeste, el pueblo de barqueros: casas de juncos sobre pilotes, pasarelas, un almacén y una grúa
## rota. Arriba, el muelle del norte con el TRANSBORDADOR varado, que un día llevaba río arriba (La Travesía, cerrada
## hasta que vuelva a navegar). Abajo, la DÁRSENA, con su plataforma de madera y cuatro postes de amarre: allí
## acecha MAMBA, el cocodrilo de herrumbre (scripts/enemigos/mamba.gd); junto a ella, BATA, el pato barquero, de piedra.
## Tres zonas corruptas y tres secretos.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const CASA_SELLADA := preload("res://scripts/mundo/embarcadero/casa_sellada.gd")
const ARREGLO := preload("res://scripts/mundo/embarcadero/arreglo_transbordador.gd")


func _ready() -> void:
	super()
	_crear_casa_sellada()
	_crear_arreglo.call_deferred()
	_activar_darsena.call_deferred()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("embarcadero_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_al_poner_marca_embarcadero)


func _al_poner_marca_embarcadero(marca: String) -> void:
	if marca == "casa_bata_abierta":
		_activar_darsena()
		return
	if marca != "mamba_vencido":
		return
	await get_tree().create_timer(6.0).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "embarcadero_mamba_libre")


## La casa de Bata, sellada por raíces de Giza (scripts/mundo/embarcadero/casa_sellada.gd)
func _crear_casa_sellada() -> void:
	var casa_sellada: Node2D = CASA_SELLADA.new()
	casa_sellada.name = "CasaSellada"
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			var c := filas[y][x]
			if c == "{":
				casa_sellada.casa = $Region._base(x, y)
			elif c == "œ":
				casa_sellada.almacen = $Region._base(x, y)
			elif c == "}":
				casa_sellada.sitio_bata = $Region._base(x, y)
	add_child(casa_sellada)


## La dársena (zona 1, la de Mamba) no despierta hasta que Bata está libre: sola, Maisha no se atreve
func _activar_darsena() -> void:
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave", "") == "1":
			z.activa = Estado.tiene("casa_bata_abierta")


func _process(_delta: float) -> void:
	if Estado.tiene("casa_bata_abierta") or Estado.tiene("darsena_vista"):
		return
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave", "") == "1" and z.en_borde(_maisha.global_position):
			Estado.marcar("darsena_vista")
			CHARLA_SCRIPT.hablar(self, "embarcadero_darsena_sola")


## Arreglar el transbordador con los poderes de Maisha (scripts/mundo/embarcadero/arreglo_transbordador.gd)
func _crear_arreglo() -> void:
	var arreglo: Node2D = ARREGLO.new()
	arreglo.name = "ArregloTransbordador"
	for cuerpo in $Entidades.get_children():
		for h in cuerpo.get_children():
			if h is Sprite2D and (h as Sprite2D).texture and (h as Sprite2D).texture.resource_path.ends_with("transbordador.png"):
				arreglo.sprite = h
				arreglo.base = (cuerpo as Node2D).global_position
	if arreglo.sprite:
		add_child(arreglo)


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
