extends StaticBody2D
## UNA COMPUERTA DEL CANAL DE TINTA: una hoja de tablones con flejes de latón que corta el cauce de orilla a orilla
## («ŧ», en la columna `columna`) y, en el muelle norte, su RUEDA DORADA («ŵ», donde va este nodo).
##   - Cerrada, para las placas de hielo (sigilia/placa_hielo.gd mira la marca «compuerta/<columna>»).
##   - Con la LLAVE DE COMPUERTA de Mfereji, Acción en la rueda: gira y la compuerta SUBE (abierta) o BAJA (cerrada).
##   - Sin la llave, la rueda no se mueve (lo dice Maisha).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const ALTO := 10                       # casillas de cauce que corta
const LATON := [Color("4a3417"), Color("8a6224"), Color("c89a3e"), Color("f0d27a")]
const MADERA := [Color("1e1410"), Color("3a2619"), Color("57392a"), Color("6f4a36")]

@export var columna := 0
var abierta := false
var radio_interaccion := 26.0
var _subida := 0.0                     # 0 abajo, 1 arriba (para dibujarla mientras se mueve)
var _giro := 0.0
var _girando := false


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("compuertas")
	abierta = Estado.tiene(marca())
	_subida = 1.0 if abierta else 0.0
	z_index = 0
	var forma := CollisionShape2D.new()
	var caja := CircleShape2D.new()
	caja.radius = 7.0
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func marca() -> String:
	return "compuerta/%d" % columna


func punto_interaccion() -> Vector2:
	return global_position + Vector2(0, -4)


func interactuar() -> void:
	if _girando:
		return
	if Estado.cuantos("llave_compuerta") == 0:
		await CHARLA.hablar(self, "canal_rueda_sin_llave")
		return
	await mover(not abierta)


## Gira la rueda y sube (o baja) la hoja
func mover(abrir: bool) -> void:
	_girando = true
	Sonido.efecto("rueda_abrir", -2.0, global_position)
	abierta = abrir
	if abrir:
		Estado.marcar(marca())
	else:
		Estado.marcas.erase(marca())
	var t := create_tween()
	t.tween_property(self, "_giro", _giro + (TAU if abrir else -TAU), 1.2)
	t.parallel().tween_property(self, "_subida", 1.0 if abrir else 0.0, 1.2).set_trans(Tween.TRANS_SINE)
	await t.finished
	Impacto.temblar(1.0, 0.15)
	_girando = false


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	# la hoja de la compuerta: de la orilla norte (y=21) a la sur, en su columna; abierta, sube y se esconde en la caseta
	var x0 := columna * 16.0 - global_position.x
	var y_cauce := 21 * 16.0 - global_position.y
	var largo := ALTO * 16.0 * (1.0 - _subida * 0.92)
	var y_hoja := y_cauce + ALTO * 16.0 - largo
	if largo > 2.0:
		draw_rect(Rect2(x0 + 1, y_hoja + 2, 14, largo), Color(0.04, 0.02, 0.07, 0.6))        # su sombra en la tinta
		draw_rect(Rect2(x0 + 2, y_hoja, 12, largo), MADERA[2])
		var y := y_hoja
		while y < y_hoja + largo - 1:                                                     # los tablones
			draw_line(Vector2(x0 + 2, y), Vector2(x0 + 13, y), MADERA[0], 1.0)
			draw_line(Vector2(x0 + 3, y + 1), Vector2(x0 + 12, y + 1), MADERA[3], 1.0)
			y += 6.0
		draw_rect(Rect2(x0 + 2, y_hoja, 2, largo), MADERA[1])
		var f := y_hoja + 4.0
		while f < y_hoja + largo - 2:                                                     # los flejes de latón
			draw_rect(Rect2(x0 + 1, f, 14, 2), LATON[1])
			draw_rect(Rect2(x0 + 1, f, 14, 1), LATON[2])
			draw_rect(Rect2(x0 + 3, f, 1, 1), LATON[3])
			draw_rect(Rect2(x0 + 12, f, 1, 1), LATON[3])
			f += 26.0
		# donde la hoja toca la tinta, la tinta se arremolina
		if _subida < 0.05:
			for k in 3:
				draw_line(Vector2(x0 - 3 - k * 2, y_cauce + 30 + k * 40), Vector2(x0 - 1, y_cauce + 30 + k * 40), Color(0.62, 0.52, 0.9, 0.5), 1.0)
	# las dos guías de hierro, a cada lado de la hoja (siempre están)
	draw_rect(Rect2(x0, y_cauce - 6, 2, ALTO * 16.0 + 6), Color("2b2a34"))
	draw_rect(Rect2(x0 + 14, y_cauce - 6, 2, ALTO * 16.0 + 6), Color("2b2a34"))
	# la rueda dorada, en su poste
	draw_rect(Rect2(-2, -6, 4, 8), MADERA[1])
	draw_circle(Vector2(0, -8), 7.0, LATON[0])
	draw_arc(Vector2(0, -8), 6.0, 0, TAU, 20, LATON[2], 2.0)
	draw_arc(Vector2(0, -8), 6.5, PI * 1.1, PI * 1.6, 6, LATON[3], 1.0)
	for k in 4:
		var a := _giro + k * PI / 4.0
		draw_line(Vector2(0, -8) - Vector2(cos(a), sin(a)) * 5.0, Vector2(0, -8) + Vector2(cos(a), sin(a)) * 5.0, LATON[1], 1.0)
	draw_circle(Vector2(0, -8), 1.5, LATON[3])
	for k in 8:                                                                           # los tiradores del aro
		var a := _giro + k * TAU / 8.0
		draw_rect(Rect2((Vector2(0, -8) + Vector2(cos(a), sin(a)) * 7.5).floor(), Vector2.ONE), LATON[3])
