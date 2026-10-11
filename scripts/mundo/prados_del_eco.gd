extends "res://scripts/mundo/escena_mundo.gd"
## PRADOS DEL ECO: la primera región jugable de Raíz.
## Maisha despierta entre ruinas, en un prado gris. Hay tres zonas corruptas que purgar
## (junto a dos de ellas, Pino y Corteza convertidos en piedra), dos secretos
## (uno tras un matorral y otro tras las piedras-eco) y un puente hacia Cuna de Musgo.


func _ready() -> void:
	super()
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡Los Prados del Eco recuperan su color!")


## Teclas 1 a 8: cambiar la ropa de cada zona (solo para probar)
func _unhandled_input(evento: InputEvent) -> void:
	if evento is InputEventKey and evento.pressed and not evento.echo:
		var tecla := (evento as InputEventKey).physical_keycode
		if tecla >= KEY_1 and tecla <= KEY_8:
			var ropa := _maisha.get_node("Ropa")
			ropa.siguiente_en_zona(ropa.ZONAS[tecla - KEY_1])
