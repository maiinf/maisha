extends Node2D
## SITIO DE PESCA: la caña de Mzee Shamba, apoyada en la orilla del estanque.
## Minijuego:
##   1. Se lanza el anzuelo y se espera a que pique (si se tira antes, el pez se espanta).
##   2. ¡Pica! Una marca va y viene por una barra: hay que pulsar Acción cuando está en lo verde.
## Mientras, por el estanque nadan sombras de peces.

signal pescado

const PEZ := preload("res://arte/mundos/kitovu/pez.png")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PANEL := Color(0.08, 0.07, 0.10, 0.9)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const VERDE := Color("6fcf4f")
const AGUA := Color("346161")
const BARRA := Rect2(220, 296, 200, 12)

enum Fase { NADA, ESPERA, PICA, FIN }

@export var radio_interaccion := 22.0
@export var altura_bocadillo := 20.0
@export var estanque := Rect2(-120, -40, 110, 60)   # dónde nadan los peces (respecto a este punto)

var fase: int = Fase.NADA
var _ondas := 0.0
var _capa: CanvasLayer
var _lienzo: Control
var _fuente: FontFile
var _espera := 0.0
var _marca := 0.0
var _sentido := 1.0
var _verde := Vector2(80, 116)          # zona verde dentro de la barra (desde, hasta)
var _texto := ""
var _texto_tiempo := 0.0
var _empezada_en := -1
var _peces: Array[Dictionary] = []
var _tiempo := 0.0
var _azar := RandomNumberGenerator.new()


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("sitios_pesca")
	_azar.randomize()
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_capa = CanvasLayer.new()
	_capa.layer = 18
	_capa.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(_capa)
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar_ui)
	_capa.add_child(_lienzo)
	for i in 3:
		_peces.append({"pos": estanque.position + Vector2(_azar.randf() * estanque.size.x, _azar.randf() * estanque.size.y),
			"destino": Vector2.ZERO, "vel": _azar.randf_range(8, 14)})
		_peces[i]["destino"] = _peces[i]["pos"]


func interactuar() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if not Estado.tiene("tarea_pesca"):
		await dialogo.decir("Maisha", ["Una caña de pescar apoyada en una piedra. Es de Mzee Shamba.", "Mejor no cogerla sin permiso."], "pensamiento")
		return
	empezar()


func empezar() -> void:
	if fase != Fase.NADA:
		return
	fase = Fase.ESPERA
	Sonido.efecto("pesca_lanzar")
	_ondas = 0.9
	_espera = _azar.randf_range(1.2, 2.6)
	_empezada_en = Engine.get_process_frames()
	_mostrar("Esperando a que pique...", 99.0)
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		maisha.set("puede_actuar", false)


func _mostrar(texto: String, segundos := 1.6) -> void:
	_texto = texto
	_texto_tiempo = segundos


func _terminar(exito: bool) -> void:
	fase = Fase.FIN
	Sonido.efecto("pesca_saca" if exito else "pesca_escapa")
	if exito:
		Estado.dar("pez")
		_mostrar("¡Un pez! " + Estado.texto_recogido("pez"), 1.8)
		pescado.emit()
	await get_tree().create_timer(1.0).timeout
	fase = Fase.NADA
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		maisha.set("puede_actuar", true)


func _process(delta: float) -> void:
	_tiempo += delta
	_texto_tiempo = maxf(0.0, _texto_tiempo - delta)
	_mover_peces(delta)
	queue_redraw()
	_lienzo.queue_redraw()
	var pulsa := Input.is_action_just_pressed("accion") and Engine.get_process_frames() != _empezada_en
	match fase:
		Fase.ESPERA:
			_espera -= delta
			# el corcho se mece y hace ondas
			_ondas -= delta
			if _ondas <= 0.0:
				_ondas = _azar.randf_range(0.7, 1.3)
				Sonido.efecto("pesca_espera", 0.0, null, 0.15)
			if pulsa:
				_mostrar("Demasiado pronto: el pez se ha espantado.", 1.6)
				_terminar(false)
			elif _espera <= 0.0:
				fase = Fase.PICA
				Sonido.efecto("pesca_pica")
				_marca = 0.0
				_sentido = 1.0
				var desde := _azar.randf_range(30.0, 150.0)
				_verde = Vector2(desde, desde + 34.0)
				_mostrar("¡Pica! Pulsa Acción en lo verde", 99.0)
		Fase.PICA:
			_marca += _sentido * 190.0 * delta
			if _marca >= BARRA.size.x:
				_marca = BARRA.size.x
				_sentido = -1.0
			elif _marca <= 0.0:
				_marca = 0.0
				_sentido = 1.0
			if pulsa:
				if _marca >= _verde.x and _marca <= _verde.y:
					_terminar(true)
				else:
					_mostrar("¡Se ha escapado! Vuelve a intentarlo.", 1.6)
					_terminar(false)


## Para las pruebas automáticas: pone la marca en el centro de lo verde
func marca_en_verde() -> void:
	_marca = (_verde.x + _verde.y) / 2.0
	_sentido = 0.0


func _mover_peces(delta: float) -> void:
	for p in _peces:
		if p["pos"].distance_to(p["destino"]) < 2.0:
			p["destino"] = estanque.position + Vector2(_azar.randf() * estanque.size.x, _azar.randf() * estanque.size.y)
		p["pos"] = p["pos"].move_toward(p["destino"], p["vel"] * delta)


func _draw() -> void:
	# sombras de peces en el agua
	for p in _peces:
		var hacia: Vector2 = p["destino"] - p["pos"]
		draw_set_transform(p["pos"].round(), 0.0, Vector2(-1 if hacia.x > 0 else 1, 1))
		draw_texture(PEZ, Vector2(-6, -3))
	draw_set_transform(Vector2.ZERO)
	# la caña apoyada (o lanzada, con el corcho flotando)
	if fase in [Fase.ESPERA, Fase.PICA]:
		var corcho := Vector2(-22, -6 + roundf(sin(_tiempo * (12.0 if fase == Fase.PICA else 3.0)) * (2.0 if fase == Fase.PICA else 1.0)))
		draw_line(Vector2(-2, -18), corcho, Color(0.9, 0.9, 0.85, 0.7), 1.0)
		draw_rect(Rect2(corcho - Vector2(1, 1), Vector2(3, 3)), Color("de6771"))
		if fase == Fase.PICA:
			for k in 2:
				var r := 3.0 + fmod(_tiempo * 12.0 + k * 3.0, 6.0)
				draw_arc(corcho + Vector2(0, 2), r, 0, TAU, 12, Color(0.8, 0.95, 0.95, 0.5), 1.0)
	draw_line(Vector2(4, 2), Vector2(-2, -18), Color("6d4534"), 2.0)
	draw_rect(Rect2(2, -2, 6, 4), Color("7a806d"))


func _dibujar_ui() -> void:
	if _texto_tiempo > 0.0:
		var ancho := _fuente.get_string_size(_texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var pos := Vector2(round((640 - ancho) / 2.0), 284)
		_lienzo.draw_rect(Rect2(pos - Vector2(8, 15), Vector2(ancho + 16, 22)), PANEL)
		_lienzo.draw_string(_fuente, pos, _texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, TEXTO)
	if fase != Fase.PICA:
		return
	var marco := BARRA.grow(4)
	_lienzo.draw_rect(marco, PANEL)
	_lienzo.draw_rect(marco, FILO, false, 1.0)
	_lienzo.draw_rect(BARRA, AGUA)
	_lienzo.draw_rect(Rect2(BARRA.position + Vector2(_verde.x, 0), Vector2(_verde.y - _verde.x, BARRA.size.y)), VERDE)
	var x := BARRA.position.x + roundf(_marca)
	_lienzo.draw_rect(Rect2(x - 1, BARRA.position.y - 3, 3, BARRA.size.y + 6), TEXTO)
