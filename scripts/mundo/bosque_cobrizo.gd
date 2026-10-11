extends "res://scripts/mundo/escena_mundo.gd"
## BOSQUE COBRIZO: la segunda región de Raíz, al norte de los Prados del Eco.
## Árboles cobrizos y rojizos muy juntos, senderos estrechos, un arroyo con puentes de troncos y hojas que caen.
## Tres zonas corruptas (junto a la segunda, Tawi de piedra), dos claros secretos tras matorrales, troncos
## podridos con madera (el encargo de Tawi) y el claro de Pembe, el ciervo de hierro (minijefe).
## Aquí salen también los jabalíes de hierro (cazadores): embisten en línea recta y se aturden al chocar.
## Al liberar a Pembe, el narrador lo cuenta con la ilustración 9_pembe_libre.


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("bosque_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_marca_de_region)


## Al liberar a Pembe: el narrador lo cuenta con su ilustración
func _marca_de_region(marca: String) -> void:
	if marca == "zona/bosque_cobrizo/4" and not Estado.tiene("narr/pembe"):
		await get_tree().create_timer(2.6).timeout
		if is_inside_tree():
			await CHARLA_SCRIPT.hablar(self, "narrador_pembe")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.2).timeout
	if not is_inside_tree() or Estado.tiene("bosque_llegada"):
		return
	Estado.marcar("bosque_llegada")
	await CHARLA_SCRIPT.hablar(self, "bosque_llegada")


const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡Las copas del Bosque Cobrizo vuelven a brillar!")
