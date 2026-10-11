extends Node2D
## PROTOTIPO DE COMBATE: un prado de Raíz con una zona corrupta.
## Acércate a la zona gris de la derecha: el color se apaga, aparecen Vida y Aliento,
## y al cruzar las espinas la zona se cierra hasta que rompas el Núcleo con semillas.

const TAM := Vector2i(110, 64)          # casillas del prado

@onready var _maisha: Node2D = $Entidades/Maisha
@onready var _suelo: Sprite2D = $Suelo


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("1d2e18"))
	_suelo.texture = SueloPrado.generar(TAM.x, TAM.y, 11)
	$Corrupcion.aplicar_a(_suelo)
	_maisha.position = Vector2(20, 32) * 16.0
	_maisha.get_node("Ropa").poner("cetro_raiz")
	var camara := Camera2D.new()
	camara.limit_left = 0
	camara.limit_top = 0
	camara.limit_right = TAM.x * 16
	camara.limit_bottom = TAM.y * 16
	camara.position_smoothing_enabled = true
	camara.position_smoothing_speed = 6.0
	_maisha.add_child(camara)
	_maisha.caida.connect(_al_caer_fuera_de_zona)


## Si Maisha cae fuera de una zona cerrada (p. ej. con su propia semilla), vuelve donde estaba
func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	$HUD.fundido(func() -> void: _maisha.revivir(punto))


## Teclas 1 a 8: cambiar la ropa de cada zona (solo para probar)
func _unhandled_input(evento: InputEvent) -> void:
	if evento is InputEventKey and evento.pressed and not evento.echo:
		var tecla := (evento as InputEventKey).physical_keycode
		if tecla >= KEY_1 and tecla <= KEY_8:
			var ropa := _maisha.get_node("Ropa")
			ropa.siguiente_en_zona(ropa.ZONAS[tecla - KEY_1])
