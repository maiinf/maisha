extends "res://scripts/mundo/escena_mundo.gd"
## CIÉNAGA QUIETA: la tercera región de Raíz, al este de Cuna de Musgo.
## Agua quieta, sauces, árboles muertos, juncos y nenúfares; una niebla baja que se levanta al purgar.
## Tres zonas corruptas (junto a la segunda, Juncia de piedra), dos islas con secretos, un secreto tras un
## matorral, bayas y juncos (el encargo de Juncia, vuelven a salir) y la poza de Konokono (minijefe).
## Aquí salen las babosas de óxido (errantes): dejan un rastro pegajoso que frena a Maisha.
## Al liberar a Konokono, el narrador lo cuenta con la ilustración 10_konokono_libre.


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("cienaga_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_marca_de_region)


## Al liberar a Konokono: el narrador lo cuenta con su ilustración
func _marca_de_region(marca: String) -> void:
	if marca == "zona/cienaga_quieta/4" and not Estado.tiene("narr/konokono"):
		await get_tree().create_timer(2.6).timeout
		if is_inside_tree():
			await CHARLA_SCRIPT.hablar(self, "narrador_konokono")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.2).timeout
	if not is_inside_tree() or Estado.tiene("cienaga_llegada"):
		return
	Estado.marcar("cienaga_llegada")
	await CHARLA_SCRIPT.hablar(self, "cienaga_llegada")


const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	var ambiente := get_tree().get_first_node_in_group("ambiente")
	if ambiente:
		create_tween().tween_property(ambiente, "niebla", 0.25, 6.0)
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡La Ciénaga Quieta vuelve a croar!")
