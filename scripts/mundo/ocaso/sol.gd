extends Node2D
## EL SOL DEL ATARDECER (el Valle del Ocaso). Lo pone la escena. El sol está parado en una de tres horas: al OESTE,
## al SUR o al ESTE (lo cambian los Relojes de Sol, ocaso/reloj_sol.gd). La hora se guarda (Estado.extra["sol"]).
##   - SOMBRAS-PUENTE: cada obelisco (`obeliscos`: [casilla de su pie, largo en casillas]) echa una sombra larga
##     hacia el lado contrario del sol (sol al oeste → al este; al sur → al norte; al este → al oeste), de dos
##     casillas de ancho. La sombra es SÓLIDA: sobre el vacío se puede andar (está en «sostenes», `firme()`).
##   - LUZ: el sol solo da de lleno en el lado donde está (`luz`: {hora: Rect2 en px}); lo que está en ese lado y
##     fuera de las sombras está iluminado (`iluminado()`: los Kivuli, ahí, se quedan deslumbrados).

signal cambiada(hora: int)

enum { OESTE, SUR, ESTE }
const NOMBRE := ["al oeste", "al sur", "al este"]
const HACIA := [Vector2i.RIGHT, Vector2i.UP, Vector2i.LEFT]       # hacia dónde cae la sombra con cada hora
const COLOR_SOMBRA := Color(0.07, 0.02, 0.12, 0.8)
const COLOR_FILO := Color(1.0, 0.78, 0.48, 0.85)       # el filo de la sombra, donde le da el sol

var hora := OESTE
var obeliscos: Array = []                 # [[Vector2i pie, int largo], ...] o [pie, largo, nodo] si echa sombra
                                          # solo a veces (una Vela de Sombra: nodo.proyecta(hora))
var luz := {}                             # {hora: Rect2}
var _sombra := {}                         # casilla → true (las de la hora de ahora)
var _cambio := 0.0                        # el fundido de las sombras al girar


func _ready() -> void:
	add_to_group("sostenes")
	add_to_group("sol")
	z_index = -4
	hora = int(Estado.extra.get("sol", OESTE)) % 3
	_calcular()


## Las casillas de la sombra de un obelisco con la hora de ahora
func sombra_de(pie: Vector2i, largo: int) -> Array[Vector2i]:
	var d: Vector2i = HACIA[hora]
	var ancho := Vector2i(0, 1) if d.y == 0 else Vector2i(1, 0)
	var casillas: Array[Vector2i] = []
	for k in range(1, largo + 1):
		casillas.append(pie + d * k)
		casillas.append(pie + d * k + ancho)
	return casillas


## ¿Echa sombra ahora? (un obelisco, siempre; una vela, solo si el sol le da de cara)
func proyecta(o: Array) -> bool:
	return o.size() < 3 or o[2].proyecta(hora)


func recalcular() -> void:
	_cambio = 1.0
	_calcular()


func _calcular() -> void:
	_sombra.clear()
	for o in obeliscos:
		if not proyecta(o):
			continue
		for c in sombra_de(o[0], o[1]):
			_sombra[c] = true
	queue_redraw()


func girar() -> void:
	poner((hora + 1) % 3)


func poner(h: int) -> void:
	hora = h
	Estado.extra["sol"] = hora
	Estado.guardar_pronto()
	_cambio = 1.0
	_calcular()
	Sonido.efecto("sombra_tiende", -2.5)
	cambiada.emit(hora)


## ¿Hay sombra bajo ese punto? (la sombra sostiene sobre el vacío)
func firme(p: Vector2) -> bool:
	return _sombra.has(Vector2i(floori(p.x / 16.0), floori(p.y / 16.0)))


func en_sombra(p: Vector2) -> bool:
	return firme(p)


## ¿Le da el sol de lleno a ese punto?
func iluminado(p: Vector2) -> bool:
	var r: Rect2 = luz.get(hora, Rect2())
	return r.has_point(p) and not en_sombra(p)


func _process(delta: float) -> void:
	if _cambio > 0.0:
		_cambio = maxf(0.0, _cambio - delta * 2.5)
		queue_redraw()


## Las sombras: bandas casi negras sobre el suelo y el abismo, con un filo de luz cálida a cada lado (para que se
## lea bien dónde se puede pisar), más oscuras al pie del obelisco
func _draw() -> void:
	var a := 1.0 - _cambio
	for o in obeliscos:
		if not proyecta(o):
			continue
		var casillas := sombra_de(o[0], o[1])
		var largo: int = o[1]
		for i in casillas.size():
			var k := i / 2 + 1
			var c: Vector2i = casillas[i]
			var col := COLOR_SOMBRA
			col.a *= a * lerpf(1.0, 0.7, float(k) / largo)
			draw_rect(Rect2(Vector2(c) * 16.0, Vector2(16, 16)), col)
		# el filo de la sombra
		var d: Vector2i = HACIA[hora]
		var pie: Vector2 = Vector2(o[0]) * 16.0
		var fin := pie + Vector2(d) * 16.0 * (largo + 1)
		var borde := Color(COLOR_FILO, COLOR_FILO.a * a)
		var grosor := 3.0 if Estado.tiene("reloj_bolsillo") else 2.0      # (el reloj de bolsillo de Kikombe: el filo se ve mejor)
		if d.y == 0:
			var x0 := minf(pie.x, fin.x) + 16.0
			var w := 16.0 * largo
			draw_line(Vector2(x0, pie.y), Vector2(x0 + w, pie.y), borde, grosor)
			draw_line(Vector2(x0, pie.y + 32), Vector2(x0 + w, pie.y + 32), borde, grosor)
		else:
			var y0 := fin.y + 16.0
			draw_line(Vector2(pie.x, y0), Vector2(pie.x, pie.y), borde, grosor)
			draw_line(Vector2(pie.x + 32, y0), Vector2(pie.x + 32, pie.y), borde, grosor)
