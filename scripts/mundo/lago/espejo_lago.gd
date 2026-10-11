extends Node2D
## EL ESPEJO DEL LAGO: decide cuándo el Lago Espejo está quieto y dibuja su agua turbia.
##   - Mientras KAMBARE vive (falta la marca «kambare_vencido»), el agua está TURBIA: barro y óxido que se arremolinan
##     encima del lago y no dejan que se calme. Si Maisha intenta calmarla, piensa que algo grande remueve el fondo.
##   - Sin Kambare: si Maisha se queda QUIETA junto al agua (R.QUIETUD_SEGUNDOS), el lago se vuelve ESPEJO: un anillo
##     se va cerrando a su alrededor mientras tanto, y al cerrarse el agua se alisa y los puentes del reflejo se hacen
##     reales. Andar no lo rompe; correr, golpear, lanzar una semilla, el Latido o una pelea, sí (el agua tiembla y los
##     puentes se apagan poco a poco), salvo con Maisha encima de un puente: entonces espera a que baje.

const R := preload("res://scripts/combate/reglas_combate.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const BARRO := Color(0.30, 0.22, 0.14)
const OXIDO := Color(0.45, 0.24, 0.12)
const VIOLETA := Color(0.42, 0.17, 0.56)

var calma := 0.0                  # 0 = agua movida, 1 = espejo
var espejo := false
var _quieta := 0.0                # segundos que lleva Maisha quieta junto al agua
var _turbio := 1.0                # 1 = turbia del todo; baja al vencer a Kambare
var _tiempo := 0.0
var _agua: Array[Vector2i] = []   # las casillas de agua (y de puente del reflejo), para la capa turbia
var _hay_agua := {}
var _maisha: Node2D
var _anillo: Node2D
var _aviso_turbio := false
var _barro: Array[Sprite2D] = []  # dos capas de barro suaves que se funden (parece que se arremolina)


func _ready() -> void:
	add_to_group("espejo_lago")
	z_index = -7
	var region := get_tree().get_first_node_in_group("region")
	var filas: PackedStringArray = region.get("_filas")
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] in "~\\":
				_agua.append(Vector2i(x, y))
				_hay_agua[Vector2i(x, y)] = true
	_turbio = 0.0 if Estado.tiene("kambare_vencido") else 1.0
	_maisha = get_tree().get_first_node_in_group("maisha")
	_crear_barro(filas)
	# el anillo que se cierra alrededor de Maisha mientras calma el agua (va por encima de todo)
	_anillo = Node2D.new()
	_anillo.top_level = true
	_anillo.z_index = 4
	_anillo.draw.connect(_dibujar_anillo)
	add_child(_anillo)
	Estado.marca_puesta.connect(func(m: String) -> void:
		if m == "kambare_vencido":
			create_tween().tween_property(self, "_turbio", 0.0, 3.0))


## El barro: una imagen pequeña (un píxel por casilla) con el agua del lago, ampliada con filtro suave, así los
## bordes quedan redondeados y las manchas se funden. Dos capas con manchas distintas, que se van turnando.
func _crear_barro(filas: PackedStringArray) -> void:
	var alto := filas.size()
	var ancho := filas[0].length()
	for capa in 2:
		var img := Image.create(ancho + 2, alto + 2, false, Image.FORMAT_RGBA8)
		img.fill(Color(0, 0, 0, 0))
		for c in _agua:
			# ¿del todo dentro del agua? (en la orilla, el barro se aclara para no pisar la hierba)
			var dentro := 0
			for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
				if _hay_agua.has(c + d):
					dentro += 1
			var n := sin(c.x * (0.55 + capa * 0.3) + capa * 2.0) * cos(c.y * (0.7 - capa * 0.2) + capa) * 0.5 + 0.5
			var col := BARRO.lerp(OXIDO, n)
			img.set_pixel(c.x + 1, c.y + 1, Color(col, (0.5 + 0.3 * n) * (1.0 if dentro == 4 else 0.45)))
		var s := Sprite2D.new()
		s.texture = ImageTexture.create_from_image(img)
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		s.centered = false
		s.scale = Vector2.ONE * R.CASILLA
		s.position = -Vector2.ONE * R.CASILLA * 0.5
		s.z_index = -1                   # (relativo: queda justo bajo los puentes y sobre el suelo)
		add_child(s)
		_barro.append(s)


func turbio() -> bool:
	return _turbio > 0.5


## ¿Está Maisha junto al agua? (a tres casillas o menos)
func junto_al_agua(p: Vector2) -> bool:
	var c := Vector2i((p / R.CASILLA).floor())
	for dy in range(-3, 4):
		for dx in range(-3, 4):
			if _hay_agua.has(c + Vector2i(dx, dy)):
				return true
	return false


func _sobre_un_puente() -> bool:
	for p in get_tree().get_nodes_in_group("puentes_reflejo"):
		if p.pisa(_maisha.global_position):
			return true
	return false


## Algo que hace temblar el agua: correr, golpear, lanzar una semilla, el Latido o una pelea
func _alborota() -> bool:
	if _maisha.get("corriendo") or _maisha.get("_golpeando"):
		return true
	if float(_maisha.get("_espera_latido")) > R.LATIDO_ESPERA - 0.3 or float(_maisha.get("_desde_ultima_semilla")) < 0.3:
		return true
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.estado == z.Estado.CERRADA:
			return true
	return false


func _physics_process(delta: float) -> void:
	_tiempo += delta
	queue_redraw()
	_anillo.queue_redraw()
	if _maisha == null or not is_instance_valid(_maisha):
		return
	var quieta: bool = _maisha.get("velocity").length() < 4.0 and _maisha.get("puede_actuar") and not _alborota()
	if espejo:
		if _alborota() and not _sobre_un_puente():
			espejo = false
			Sonido.efecto("agua_baja", -6.0, _maisha.global_position)
		_quieta = 0.0
	elif quieta and junto_al_agua(_maisha.global_position):
		_quieta += delta
		if turbio():
			_quieta = minf(_quieta, R.QUIETUD_SEGUNDOS * 0.8)     # (turbia, nunca llega a calmarse)
			if _quieta >= R.QUIETUD_SEGUNDOS * 0.8 and not _aviso_turbio:
				_aviso_turbio = true
				CHARLA.hablar(self, "lago_turbio")
		elif _quieta >= R.QUIETUD_SEGUNDOS:
			espejo = true
			Sonido.efecto("eco_voz", -4.0, _maisha.global_position)
			if not Estado.tiene("lago_espejo_visto"):
				Estado.marcar("lago_espejo_visto")
				CHARLA.hablar(self, "lago_espejo_primera")
	else:
		_quieta = maxf(0.0, _quieta - delta * 2.0)
	calma = move_toward(calma, 1.0 if espejo else 0.0, delta * (1.5 if espejo else 0.5))
	for p in get_tree().get_nodes_in_group("puentes_reflejo"):
		p.calma = calma


func _draw() -> void:
	# el agua turbia: las dos capas de barro se turnan despacio, con burbujas y algún brillo violeta de Giza
	for k in _barro.size():
		_barro[k].modulate.a = _turbio * (0.55 + 0.45 * sin(_tiempo * 0.4 + k * PI))
	if _turbio > 0.01:
		for c in _agua:
			var p := Vector2(c) * R.CASILLA
			if (c.x * 7 + c.y * 13 + int(_tiempo * 2.0)) % 29 == 0:
				draw_rect(Rect2(p + Vector2(6, 7), Vector2(3, 1)), Color(VIOLETA, _turbio * 0.6))
			if (c.x * 5 + c.y * 3) % 13 == 0:
				var f := fmod(_tiempo * 0.8 + c.x * 0.31, 1.0)
				draw_arc(p + Vector2(8, 8), 1.0 + f * 3.0, 0, TAU, 8, Color(0.62, 0.52, 0.36, _turbio * (1.0 - f) * 0.6), 1.0)
	# el espejo: un velo claro y unas vetas de luz que se deslizan cuando el agua está quieta
	if calma > 0.01:
		for c in _agua:
			if (c.x + c.y * 3) % 5 != 0:
				continue
			var p := Vector2(c) * R.CASILLA
			var f := fmod(_tiempo * 0.15 + c.y * 0.07, 1.0)
			draw_rect(Rect2(p + Vector2(f * 12.0, 6), Vector2(6, 1)), Color(0.9, 1.0, 0.98, calma * 0.35))


func _dibujar_anillo() -> void:
	# mientras Maisha calma el agua, un anillo se cierra a su alrededor (al cerrarse del todo, el lago es espejo)
	if espejo or _quieta <= 0.15 or _maisha == null:
		return
	var f := clampf(_quieta / R.QUIETUD_SEGUNDOS, 0.0, 1.0)
	var centro := _maisha.global_position + Vector2(0, -6)
	var radio := 26.0 - f * 16.0
	var col := Color(0.6, 0.45, 0.3) if turbio() else Color(0.86, 0.96, 0.94)
	_anillo.draw_arc(centro, radio, -PI / 2, -PI / 2 + TAU * f, 32, Color(col, 0.75), 1.5)
	_anillo.draw_arc(centro, radio + 3.0, 0, TAU, 32, Color(col, 0.18 * f), 1.0)
