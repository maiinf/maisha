extends Node2D
## EL FOSO DE LA ACEQUIA («"» en la Senda de los Surcos): el agua que rodea el huerto del eco. No se puede cruzar.
## Cuando se pone su «marca» (Sungura cierra la compuerta al devolverle sus mazorcas), el agua baja poco a poco,
## con un gorgoteo, y queda el fondo de barro húmedo: ya se puede pasar.
## El fondo (tierra) lo pinta pintar_suelo.py; el agua la dibuja este nodo, encima.

const R := preload("res://scripts/combate/reglas_combate.gd")
const AGUA := [Color("1c3535"), Color("28484a"), Color("346161"), Color("4c8d8d"), Color("9fd0d0")]

var casillas: Array[Vector2i] = []
var marca := ""
var nivel := 1.0                  # 1 = lleno, 0 = vacío (se anima al vaciarlo)
var _cuerpo: StaticBody2D
var _tiempo := 0.0
var _hay := {}


func _ready() -> void:
	z_index = -6
	add_to_group("acequias")
	for c in casillas:
		_hay[c] = true
	if Estado.tiene(marca):
		nivel = 0.0
		queue_redraw()
		return
	_cuerpo = StaticBody2D.new()
	add_child(_cuerpo)
	for c in casillas:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(R.CASILLA, R.CASILLA)
		forma.shape = caja
		forma.position = Vector2(c) * R.CASILLA + Vector2.ONE * 8
		_cuerpo.add_child(forma)
	Estado.marca_puesta.connect(_al_poner_marca)


func vacia() -> bool:
	return nivel <= 0.0 and _cuerpo == null


## (para las pruebas: como la pasarela rota y el derrumbe)
func arreglada() -> bool:
	return vacia()


func _al_poner_marca(m: String) -> void:
	if m != marca:
		return
	Sonido.efecto("agua_baja")
	var t := create_tween()
	t.tween_property(self, "nivel", 0.0, 2.4).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
	t.tween_callback(func() -> void:
		if _cuerpo:
			_cuerpo.queue_free()
			_cuerpo = null)


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()


func _draw() -> void:
	for c in casillas:
		var o := Vector2(c) * R.CASILLA
		# el barro mojado que queda (más oscuro cuanto más reciente)
		draw_rect(Rect2(o, Vector2(R.CASILLA, R.CASILLA)), Color(0.08, 0.06, 0.04, 0.35 - 0.1 * (1.0 - nivel)))
		if nivel <= 0.0:
			continue
		# el agua: más clara en los bordes, con ondas que se mueven
		var a := clampf(nivel * 1.4, 0.0, 1.0)
		draw_rect(Rect2(o, Vector2(R.CASILLA, R.CASILLA)), Color(AGUA[2], a))
		for k in 3:
			var y := o.y + 3 + k * 5 + sin(_tiempo * 1.6 + c.x * 0.9 + k) * 1.0
			var x := o.x + fmod(_tiempo * 6.0 + c.y * 5.0 + k * 7.0, 16.0)
			draw_rect(Rect2(Vector2(x, y).round(), Vector2(5, 1)), Color(AGUA[3], 0.55 * a))
			draw_rect(Rect2(Vector2(o.x + fmod(x - o.x + 9.0, 16.0), y + 2).round(), Vector2(3, 1)), Color(AGUA[1], 0.5 * a))
		# la orilla: espuma clara donde el agua toca tierra (y baja con el nivel)
		for v: Vector2i in [Vector2i(0, -1), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(1, 0)]:
			if _hay.has(c + v):
				continue
			var borde := Rect2(o + Vector2(0 if v.x <= 0 else 15, 0 if v.y <= 0 else 15), Vector2(16 if v.x == 0 else 1, 16 if v.y == 0 else 1))
			draw_rect(borde, Color(AGUA[4], 0.6 * a))
		if (c.x * 7 + c.y * 3) % 9 == 0 and nivel > 0.5:
			var brillo := 0.5 + 0.5 * sin(_tiempo * 3.0 + c.x)
			draw_rect(Rect2(o + Vector2(6, 7), Vector2(2, 1)), Color(1, 1, 0.9, 0.6 * brillo * a))
