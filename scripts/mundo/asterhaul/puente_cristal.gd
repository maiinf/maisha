extends Node2D
## UN PUENTE DE CRISTAL (Asterhaul, la Aguja Caída): losas de cristal tendidas sobre el viento astral (las casillas
## «=» de su rectángulo `casillas`). Cada losa solo existe mientras le llega la onda de un monolito que canta
## (asterhaul/monolito.gd) y AGUANTA s más. Fuera de eso es vacío: quien la pisa, cae (lo mira la escena con
## `firme()`; el puente está en «sostenes»).

const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const AGUANTA := 1.2

var casillas := Rect2i()
var _queda := {}                       # casilla → segundos que le quedan
var _sonaba := false
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("sostenes")
	add_to_group("puentes_cristal")
	z_index = -4
	for y in range(casillas.position.y, casillas.end.y):
		for x in range(casillas.position.x, casillas.end.x):
			_queda[Vector2i(x, y)] = 0.0


## ¿Hay losa bajo ese punto?
func firme(p: Vector2) -> bool:
	var c := Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))
	return float(_queda.get(c, 0.0)) > 0.0


## Cuántas losas hay ahora mismo
func losas() -> int:
	var n := 0
	for c: Vector2i in _queda:
		if float(_queda[c]) > 0.0:
			n += 1
	return n


func _process(delta: float) -> void:
	_tiempo += delta
	var alguna := false
	for c: Vector2i in _queda:
		if MONOLITO.que_suena_en(get_tree(), Vector2(c) * 16.0 + Vector2(8, 8)) != null:
			_queda[c] = AGUANTA
		else:
			_queda[c] = maxf(0.0, float(_queda[c]) - delta)
		alguna = alguna or float(_queda[c]) > 0.0
	if alguna and not _sonaba:
		Sonido.efecto("puente_cristal", 0.0, Vector2(casillas.get_center()) * 16.0)
	_sonaba = alguna
	queue_redraw()


## Cada losa: un cuadro de cristal turquesa con su brillo; cuando se va a deshacer, parpadea
func _draw() -> void:
	for c: Vector2i in _queda:
		var q := float(_queda[c])
		if q <= 0.0:
			continue
		var a := clampf(q / 0.5, 0.0, 1.0)
		if q < 0.6 and int(_tiempo * 16.0) % 2 == 0:
			a *= 0.45
		var r := Rect2(Vector2(c) * 16.0 + Vector2(0.5, 0.5), Vector2(15, 15))
		draw_rect(r, Color(0.18, 0.60, 0.75, 0.62 * a))
		draw_rect(r.grow(-2.0), Color(0.42, 0.82, 0.94, 0.5 * a))
		draw_line(r.position + Vector2(2, 4), r.position + Vector2(8, 2), Color(1, 1, 1, 0.7 * a), 1.0)
		draw_rect(r, Color(0.75, 0.96, 1.0, 0.85 * a), false, 1.0)
