extends Node2D
## ESCENA DE PRUEBA: Maisha paseando por un prado de Raíz (sin combate).
## El suelo es provisional hasta tener el tileset dibujado.

const TAM := Vector2i(60, 34)   # casillas de 16x16


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("1d2e18"))
	var suelo := Sprite2D.new()
	suelo.texture = SueloPrado.generar(TAM.x, TAM.y)
	suelo.centered = false
	suelo.z_index = -10
	add_child(suelo)
	var maisha := $Maisha as Node2D
	maisha.position = Vector2(TAM) * 8.0
	var camara := Camera2D.new()
	camara.limit_left = 0
	camara.limit_top = 0
	camara.limit_right = TAM.x * 16
	camara.limit_bottom = TAM.y * 16
	camara.position_smoothing_enabled = true
	maisha.add_child(camara)


func _draw() -> void:
	var fuente := ThemeDB.fallback_font
	draw_string(fuente, Vector2(TAM.x * 8 - 95, TAM.y * 8 - 40), "WASD: andar   1: cabeza   3: espalda (cambiar ropa)", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("fff3c4"))


## Solo para probar la ropa: las teclas 1 a 8 cambian la prenda de cada zona
## (1 cabeza, 2 cara, 3 espalda, 4 torso, 5 brazos, 6 piernas, 7 aura, 8 arma)
func _unhandled_input(evento: InputEvent) -> void:
	if evento is InputEventKey and evento.pressed and not evento.echo:
		var tecla := (evento as InputEventKey).physical_keycode
		if tecla >= KEY_1 and tecla <= KEY_8:
			var ropa := $Maisha/Ropa
			ropa.siguiente_en_zona(ropa.ZONAS[tecla - KEY_1])
