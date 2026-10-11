extends "res://scripts/mundo/interiores/interior_casa.gd"
## CASA DE PINO, por dentro: la casa-seta reconstruida. Su cama, el mapa de sus «exploraciones»,
## el catalejo y la escalera al tejado, desde donde vigila los prados.

const FONDO := preload("res://arte/mundos/raiz/aldea/interior_casa_pino.png")


func _fondo() -> Texture2D:
	return FONDO


func _muebles() -> Array[Rect2]:
	return [
		Rect2(38, 64, 49, 42),      # cama
		Rect2(40, 108, 25, 21),     # baúl
		Rect2(212, 80, 22, 18),     # catalejo
		Rect2(256, 70, 22, 14),     # pie de la escalera
		Rect2(260, 156, 22, 22),    # macetas
	]


func _cosas() -> Array:
	return [
		["casa_mapa", Vector2(118, 80), 24.0, 24.0],
		["casa_tarros", Vector2(176, 80), 20.0, 24.0],
		["casa_catalejo", Vector2(222, 104), 20.0, 30.0],
		["casa_escalera", Vector2(267, 92), 20.0, 30.0],
		["casa_cama", Vector2(62, 114), 20.0, 20.0],
		["casa_baul", Vector2(52, 136), 16.0, 22.0],
	]


func _dibujar_luces() -> void:
	super()
	var pulso := 0.5 + 0.5 * sin(_tiempo * 2.0)
	for i in 3:
		_luces.draw_circle(Vector2(176, 42), 8.0 + i * 7.0 + pulso * 2.0, Color(0.43, 0.69, 0.69, 0.05))   # tarros de luz
		_luces.draw_circle(Vector2(224, 44), 10.0 + i * 7.0, Color(0.8, 0.95, 1.0, 0.04))                 # ventana
	for i in 3:
		_luces.draw_circle(Vector2(267, 4), 8.0 + i * 8.0, Color(1.0, 0.95, 0.8, 0.05))                 # trampilla
