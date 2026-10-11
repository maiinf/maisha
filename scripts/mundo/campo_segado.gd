extends "res://scripts/mundo/escena_mundo.gd"
## CAMPO SEGADO: la última región de Raíz, al norte de Cuna de Musgo. Se abre al liberar a los dos minijefes.
## Campos de cultivo abandonados: surcos, trigo seco, espantapájaros, vallas, pacas, máquinas oxidadas,
## un granero en ruinas y un molino roto. Dos zonas corruptas (salen jabalíes, babosas y Petrinos: lo aprendido
## en todo Raíz) y, al norte, el gran campo de la COSECHADORA OXIDADA, el jefe del mundo.
## Al vencerla, el narrador lo cuenta con la ilustración 11_cosecha_libre, Raíz queda libre de Giza
## y sale la pantalla del final del mundo (scripts/interfaz/fin_mundo.gd).


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("campo_llegada"):
		_pensar_al_llegar.call_deferred()
	Estado.marca_puesta.connect(_marca_de_region)


## Al vencer a la Cosechadora: el narrador lo cuenta con su ilustración
func _marca_de_region(marca: String) -> void:
	if marca == "zona/campo_segado/3" and not Estado.tiene("narr/cosechadora"):
		await get_tree().create_timer(3.0).timeout
		if is_inside_tree():
			await CHARLA_SCRIPT.hablar(self, "narrador_cosechadora")
		if is_inside_tree() and Estado.tiene("raiz_libre") and not Estado.tiene("fin_raiz_visto"):
			mostrar_fin_de_raiz()


## La pantalla del final del mundo (lo conseguido en Raíz, con «Raíz respira»)
func mostrar_fin_de_raiz() -> void:
	Estado.marcar("fin_raiz_visto")
	var fin: CanvasLayer = load("res://scripts/interfaz/fin_mundo.gd").new()
	add_child(fin)
	fin.abrir()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.2).timeout
	if not is_inside_tree() or Estado.tiene("campo_llegada"):
		return
	Estado.marcar("campo_llegada")
	await CHARLA_SCRIPT.hablar(self, "campo_llegada")


const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡El Campo Segado vuelve a dar fruto!")
