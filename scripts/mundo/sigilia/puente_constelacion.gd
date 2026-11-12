extends Node2D
## UN PUENTE DE CONSTELACIÓN (Sigilia, el Observatorio de la Aurora): un camino de luz de estrellas entre dos
## terrazas, sobre el vacío (las casillas «=» de `casillas`). No está hasta que TODAS sus `bobinas` (sigilia/bobina.gd)
## están encendidas a la vez; entonces se tiende para siempre (marca `marca`) y las bobinas se quedan encendidas.
## Apagado, cierra el paso (un muro invisible) y solo se ven sus estrellas sueltas, muy tenues.

signal tendido

@export var casillas := Rect2i()
@export var marca := ""
var bobinas: Array = []
var encendido := false
var _aparece := 0.0                 # 0 apagado, 1 tendido (para dibujarlo mientras aparece)
var _tiempo := 0.0
var _muro: StaticBody2D
var _estrellas: Array[Vector2] = []


func _ready() -> void:
	z_index = -2
	add_to_group("puentes_constelacion")
	position = Vector2(casillas.position) * 16.0
	var tam := Vector2(casillas.size) * 16.0
	_muro = StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = tam
	forma.shape = caja
	forma.position = tam * 0.5
	_muro.add_child(forma)
	add_child(_muro)
	# las estrellas del puente: dos hileras (los pretiles) y unas cuantas por medio, siempre las mismas
	var azar := RandomNumberGenerator.new()
	azar.seed = casillas.position.x * 31 + casillas.position.y * 17
	var a_lo_largo := tam.y >= tam.x
	var largo := tam.y if a_lo_largo else tam.x
	var ancho := tam.x if a_lo_largo else tam.y
	var n := int(largo / 12.0)
	for k in n + 1:
		for lado in [2.0, ancho - 2.0, ancho * 0.5]:
			var u := k * largo / n + azar.randf_range(-2.0, 2.0)
			var v: float = lado + azar.randf_range(-1.5, 1.5) + (azar.randf_range(-ancho * 0.25, ancho * 0.25) if lado == ancho * 0.5 else 0.0)
			_estrellas.append((Vector2(v, u) if a_lo_largo else Vector2(u, v)).round())
	for b in bobinas:
		b.cambiada.connect(_al_cambiar_bobina)
	if marca != "" and Estado.tiene(marca):
		_tender(false)


func _al_cambiar_bobina(_encendida: bool) -> void:
	if encendido:
		return
	for b in bobinas:
		if not b.encendida:
			return
	_tender(true)


func _tender(ahora: bool) -> void:
	encendido = true
	_muro.get_child(0).set_deferred("disabled", true)
	for b in bobinas:
		b.fijar()
	if marca != "":
		Estado.marcar(marca)
	if ahora:
		Sonido.efecto("diapason_ambar", 0.0, global_position + Vector2(casillas.size) * 8.0)
		Sonido.efecto("arte_sube", -6.0, global_position + Vector2(casillas.size) * 8.0)
		create_tween().tween_property(self, "_aparece", 1.0, 1.2).set_trans(Tween.TRANS_SINE)
		tendido.emit()
	else:
		_aparece = 1.0


func _process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()


func _draw() -> void:
	var tam := Vector2(casillas.size) * 16.0
	var a_lo_largo := tam.y >= tam.x
	# el camino de luz: una pasarela translúcida con su filo, que aparece de un extremo al otro
	if _aparece > 0.0:
		var hecho := Rect2(Vector2.ZERO, Vector2(tam.x, tam.y * _aparece) if a_lo_largo else Vector2(tam.x * _aparece, tam.y))
		if a_lo_largo:
			hecho.position.y = tam.y - hecho.size.y           # (crece desde el sur, desde donde llega Maisha)
		draw_rect(hecho, Color(0.35, 0.5, 0.95, 0.28))
		draw_rect(hecho.grow(-3.0), Color(0.55, 0.75, 1.0, 0.16))
		draw_rect(hecho, Color(0.8, 0.92, 1.0, 0.7), false, 1.0)
		# las líneas de la constelación: de estrella en estrella
		for i in range(3, _estrellas.size()):
			if hecho.has_point(_estrellas[i]) and hecho.has_point(_estrellas[i - 3]):
				draw_line(_estrellas[i - 3], _estrellas[i], Color(0.85, 0.95, 1.0, 0.45), 1.0)
		for i in range(0, _estrellas.size() - 2, 3):
			if hecho.has_point(_estrellas[i]):
				draw_line(_estrellas[i], _estrellas[i + 2], Color(0.85, 0.95, 1.0, 0.25), 1.0)
				draw_line(_estrellas[i + 2], _estrellas[i + 1], Color(0.85, 0.95, 1.0, 0.25), 1.0)
	# las estrellas (apagado: tenues; tendido: titilan)
	for i in _estrellas.size():
		var p := _estrellas[i]
		var viva := _aparece > 0.0 and (p.y >= tam.y * (1.0 - _aparece) if a_lo_largo else p.x <= tam.x * _aparece)
		var brillo := (0.75 + 0.25 * sin(_tiempo * 3.0 + i * 1.7)) if viva else 0.22 + 0.08 * sin(_tiempo * 1.5 + i)
		var col := Color(1.0, 0.97, 0.8, brillo)
		draw_rect(Rect2(p, Vector2.ONE), col)
		if viva:
			draw_rect(Rect2(p + Vector2(-1, 0), Vector2(3, 1)), Color(col, brillo * 0.6))
			draw_rect(Rect2(p + Vector2(0, -1), Vector2(1, 3)), Color(col, brillo * 0.6))
