extends "res://scripts/mundo/interiores/interior_casa.gd"
## TALLER DE CORTEZA, por dentro: la forja encendida, el yunque, las herramientas y el banco
## con dibujos de cetros. Corteza trabaja aquí desde que se reconstruye el taller.

const FONDO := preload("res://arte/mundos/raiz/aldea/interior_taller.png")
const YUNQUE := preload("res://arte/mundos/raiz/aldea/yunque.png")
const ALDEANO := preload("res://scripts/mundo/aldea/aldeano.gd")


func _fondo() -> Texture2D:
	return FONDO


func _muebles() -> Array[Rect2]:
	return [
		Rect2(58, 40, 68, 36),      # forja
		Rect2(128, 74, 20, 10),     # carbón
		Rect2(224, 70, 62, 30),     # banco de trabajo
		Rect2(38, 142, 24, 26),     # barril
		Rect2(147, 122, 26, 8),     # yunque
	]


func _cosas() -> Array:
	return [
		["taller_forja", Vector2(92, 92), 24.0, 30.0],
		["taller_banco", Vector2(255, 108), 22.0, 30.0],
		["taller_herramientas", Vector2(212, 84), 18.0, 34.0],
		["taller_barril", Vector2(50, 176), 18.0, 34.0],
	]


func _preparar() -> void:
	# el yunque, con orden de profundidad (se puede pasar por delante y por detrás)
	var yunque := Sprite2D.new()
	yunque.texture = YUNQUE
	yunque.centered = false
	yunque.offset = Vector2(-14, -19)
	yunque.position = Vector2(160, 129)
	$Entidades.add_child(yunque)
	# Corteza, junto al yunque
	var corteza: StaticBody2D = ALDEANO.new()
	corteza.id = "corteza"
	corteza.requiere = "construido_taller"
	corteza.position = Vector2(196, 132)
	$Entidades.add_child(corteza)


func _dibujar_luces() -> void:
	super()
	# la forja: un resplandor que tiembla
	var temblor := 0.75 + 0.25 * sin(_tiempo * 9.0) * sin(_tiempo * 3.7)
	for i in 5:
		_luces.draw_circle(Vector2(92, 66), (10.0 + i * 9.0) * temblor, Color(1.0, 0.6, 0.25, 0.06))
