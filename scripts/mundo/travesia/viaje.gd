extends Node2D
## EL VIAJE EN EL TRANSBORDADOR (La Travesía). La barca sube sola por el centro del río, del Embarcadero Junco (sur)
## al muelle de piedra de la Gruta de las Raíces (norte). A media subida se para junto a la isla del séptimo eco:
## Maisha puede bajar, escuchar el eco y encontrar la hoja de Mauti; al volver a bordo se sigue. Maisha va en la cubierta (se puede mover por ella, pero no
## salir) y Bata lleva la pértiga en la popa. Detrás, la estela en el agua. Al llegar, Maisha baja al muelle (marca
## «travesia_hecha»); desde la barca se puede volver al Embarcadero.
## El río sigue la misma fórmula que crear_travesia (herramientas/construir_mapa.py).

const CHARLA := preload("res://scripts/mundo/charla.gd")
const CANGREJO := preload("res://scripts/enemigos/cangrejo.gd")
const ANGUILA := preload("res://scripts/enemigos/anguila.gd")
## Lo que sale del agua: [qué parte del viaje, cangrejos que trepan, anguilas que saltan, lo que grita Bata]
const OLEADAS := [
	[0.12, 2, 0, "Bata: «¡Cangrejos por la borda! ¡Échalos, que me rayan la pintura!»"],
	[0.32, 3, 0, "Bata: «¡Más! ¿Pero cuántos cangrejos tiene este río?»"],
	[0.62, 1, 2, "Bata: «¡Anguilas! ¡Saltan de lado a lado! ¡Dales en el aire!»"],
	[0.82, 2, 3, "Bata: «¡Ya casi! ¡Aguanta, lucecita!»"],
]
const CUBIERTA := preload("res://arte/mundos/raiz/embarcadero/cubierta.png")
const BATA := preload("res://arte/personajes/aldeanos/bata_frente.png")
const CASILLA := 16.0
const PISABLE := Rect2(-58, -40, 118, 62)       # la cubierta que se pisa (desde el centro de la barca)
const VELOCIDAD := 34.0                           # píxeles por segundo, río arriba
const Y_SALIDA := 160.0                           # (en casillas) dónde zarpa
const Y_LLEGADA := 14.0                           # y dónde atraca, junto al muelle de piedra
const Y_ISLA := 84.0                              # a media subida se para junto a la isla (el séptimo eco)
const X_ISLA := 22.8                              # (el centro de la barca, pegado a la isla)
const HOJA := preload("res://arte/mundos/raiz/travesia/hoja_mauti.png")
const PASARELA := Rect2(50, -14, 62, 18)          # la pasarela que Bata tiende hasta la isla (desde el centro)

enum Fase { ZARPA, NAVEGA, PARADA, ATRACADA }

var fase: int = Fase.ZARPA
var recorrido := 0.0                              # píxeles navegados
var _camino: PackedVector2Array = []
var _largo := 0.0
var _t := 0.0
var _tiempo := 0.0
var _sprite: Sprite2D
var _bata: Sprite2D
var _maisha: Node2D
var _sujeta := true                               # Maisha va sujeta a la cubierta
var _parada := 0.0                                # (en el recorrido) dónde se para junto a la isla
var _ultima_valida := Vector2.ZERO
var _seguir := -1.0                               # cuenta atrás para seguir, cuando Maisha vuelve a bordo
var _pertiga: Node2D
var _oleada := 0
var _a_bordo: Array = []                  # los cangrejos que han trepado (se mueven con la barca)


static func centro_rio(y: float) -> float:
	return 24.0 + 5.0 * sin(y * 0.045) + 2.0 * sin(y * 0.11 + 1.0)


func _ready() -> void:
	process_physics_priority = 10                 # (después de que Maisha se mueva)
	z_index = -3
	_sprite = Sprite2D.new()
	_sprite.texture = CUBIERTA
	add_child(_sprite)
	_bata = Sprite2D.new()
	_bata.texture = BATA
	_bata.offset = Vector2(0, -16)
	_bata.position = Vector2(48, 34)
	_bata.z_index = 4
	add_child(_bata)
	_pertiga = Node2D.new()
	_pertiga.z_index = 5
	_pertiga.draw.connect(_dibujar_pertiga)
	add_child(_pertiga)
	_trazar()
	_maisha = get_tree().get_first_node_in_group("maisha") as Node2D
	Estado.marca_puesta.connect(_al_poner_marca)
	if Estado.tiene("travesia_hecha"):
		recorrido = _largo
		_atracar(true)
	position = _punto(recorrido)
	if fase != Fase.ATRACADA:
		_maisha.global_position = position + Vector2(0, -6)


## El camino de la barca: por el centro del río y, al final, de lado hacia el muelle de piedra
func _trazar() -> void:
	var y := Y_SALIDA
	while y > Y_LLEGADA + 10.0:
		# junto a la isla, la barca se arrima a ella
		var arrimo := clampf(1.0 - absf(y - Y_ISLA) / 9.0, 0.0, 1.0)
		arrimo = arrimo * arrimo * (3.0 - 2.0 * arrimo)
		var x := lerpf(centro_rio(y), X_ISLA, arrimo)
		_camino.append(Vector2(x, y) * CASILLA + Vector2(8, 8))
		y -= 1.0
	var muelle := Vector2(centro_rio(12.0) + 1.3, Y_LLEGADA) * CASILLA + Vector2(8, 8)
	_camino.append((_camino[_camino.size() - 1] + muelle) / 2.0)
	_camino.append(muelle)
	for i in _camino.size() - 1:
		if _camino[i].y >= Y_ISLA * CASILLA + 8.0 and _camino[i + 1].y < Y_ISLA * CASILLA + 8.0:
			_parada = _largo
		_largo += _camino[i].distance_to(_camino[i + 1])


func _punto(d: float) -> Vector2:
	var resto := clampf(d, 0.0, _largo)
	for i in _camino.size() - 1:
		var tramo := _camino[i].distance_to(_camino[i + 1])
		if resto <= tramo:
			return _camino[i].lerp(_camino[i + 1], resto / maxf(tramo, 0.001))
		resto -= tramo
	return _camino[_camino.size() - 1]


func _physics_process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	var antes := position
	match fase:
		Fase.ZARPA:
			if _t > 2.0:
				fase = Fase.NAVEGA
				_t = 0.0
				Sonido.efecto("tablas_coger", -2.0, position)
		Fase.NAVEGA:
			recorrido = minf(_largo, recorrido + VELOCIDAD * delta)
			position = _punto(recorrido)
			if not Estado.tiene("eco/la_travesia") and recorrido >= _parada and recorrido - VELOCIDAD * delta < _parada:
				_parar_en_isla()
			if _oleada < OLEADAS.size() and recorrido / _largo >= float(OLEADAS[_oleada][0]):
				_soltar_oleada(OLEADAS[_oleada])
				_oleada += 1
			if recorrido >= _largo:
				_atracar(false)
		Fase.PARADA:
			_comprobar_vuelta(delta)
	# la barca se mece un poco
	_sprite.position.y = sin(_tiempo * 1.6) * 1.0
	_sprite.rotation = sin(_tiempo * 1.1) * 0.012
	_bata.position.y = 34.0 + sin(_tiempo * 1.6) * 1.0
	_pertiga.queue_redraw()
	# los cangrejos que han trepado van encima, como Maisha
	_a_bordo = _a_bordo.filter(func(e) -> bool: return is_instance_valid(e))
	for e in _a_bordo:
		var q: Vector2 = e.global_position + (position - antes) - position
		q.x = clampf(q.x, PISABLE.position.x, PISABLE.end.x)
		q.y = clampf(q.y, PISABLE.position.y, PISABLE.end.y)
		e.global_position = position + q
	# Maisha va encima: se mueve con la barca y no sale de la cubierta (parada en la isla, puede bajar a la isla)
	if _sujeta and is_instance_valid(_maisha):
		var p := _maisha.global_position + (position - antes)
		if fase == Fase.PARADA:
			if _en_cubierta(p) or _en_pasarela(p) or _en_isla(p):
				_ultima_valida = p
			_maisha.global_position = _ultima_valida
		else:
			var local := p - position
			local.x = clampf(local.x, PISABLE.position.x, PISABLE.end.x)
			local.y = clampf(local.y, PISABLE.position.y, PISABLE.end.y)
			_maisha.global_position = position + local
	queue_redraw()


func _draw() -> void:
	# la pasarela de tablas hasta la isla (al pararse)
	if fase == Fase.PARADA:
		var r := PASARELA
		draw_rect(Rect2(r.position + Vector2(2, 3), r.size), Color(0.04, 0.08, 0.08, 0.5))
		draw_rect(r, Color("5e3a26"))
		for k in range(0, int(r.size.x), 6):
			draw_line(r.position + Vector2(k, 0), r.position + Vector2(k, r.size.y), Color("2a1a12"), 1.0)
		draw_line(r.position, r.position + Vector2(r.size.x, 0), Color("9a6544"), 1.0)
		draw_line(r.position + Vector2(0, r.size.y), r.end, Color("2a1a12"), 1.0)
	# la estela: dos ondas en V detrás de la popa (si navega) y la pértiga de Bata
	if fase == Fase.NAVEGA:
		for k in 4:
			var f := fmod(_tiempo * 0.8 + k * 0.25, 1.0)
			var y0 := 60.0 + f * 70.0
			var a := (1.0 - f) * 0.5
			draw_line(Vector2(-70 - f * 30, y0), Vector2(-40, 58), Color(0.82, 0.94, 0.92, a), 1.0)
			draw_line(Vector2(70 + f * 30, y0), Vector2(40, 58), Color(0.82, 0.94, 0.92, a), 1.0)


## La pértiga de Bata, por encima de todo: la clava en el agua al ritmo de la barca
func _dibujar_pertiga() -> void:
	var mano := Vector2(55, 18) + Vector2(0, sin(_tiempo * 1.6))
	var empuje := sin(_tiempo * 1.2) * 6.0 if fase == Fase.NAVEGA else 0.0
	var punta := mano + Vector2(18, 44 + empuje)
	_pertiga.draw_line(mano + Vector2(-6, -14), punta, Color("3a2414"), 2.0)
	_pertiga.draw_line(mano + Vector2(-6, -14), punta, Color("8a6440"), 1.0)


func _en_cubierta(p: Vector2) -> bool:
	return Rect2(position + PISABLE.position, PISABLE.size).grow(2.0).has_point(p)


func _en_pasarela(p: Vector2) -> bool:
	return fase == Fase.PARADA and Rect2(position + PASARELA.position, PASARELA.size).has_point(p)


## En tierra de la isla (no en el agua): la isla está al este del río, a media subida
func _en_isla(p: Vector2) -> bool:
	var region := get_tree().get_first_node_in_group("region")
	if region == null:
		return false
	var filas: PackedStringArray = region.get("_filas")
	var c := Vector2i((p / CASILLA).floor())
	if c.y < 74 or c.y > 94 or c.x < 26 or c.y >= filas.size() or c.x >= filas[c.y].length():
		return false
	return filas[c.y][c.x] != "~"


## Junto a la isla: la barca se para y Bata dice que se puede bajar
func _parar_en_isla() -> void:
	fase = Fase.PARADA
	_t = 0.0
	_ultima_valida = _maisha.global_position
	Sonido.efecto("tablas_coger", -2.0, position)
	await get_tree().create_timer(0.5).timeout
	await CHARLA.hablar(self, "travesia_isla")


## Con el eco escuchado y Maisha otra vez en la cubierta, se sigue río arriba
func _comprobar_vuelta(delta: float) -> void:
	if not Estado.tiene("eco/la_travesia") or not _en_cubierta(_maisha.global_position):
		_seguir = -1.0
		return
	if _seguir < 0.0:
		_seguir = 1.2
	_seguir -= delta
	if _seguir <= 0.0 and fase == Fase.PARADA:
		fase = Fase.NAVEGA
		_seguir = -1.0
		CHARLA.hablar(self, "travesia_seguimos")


## Al escuchar el eco aparece, debajo de la piedra plana, la hoja de Mauti
func _al_poner_marca(marca: String) -> void:
	if marca == "eco/la_travesia" and not Estado.tiene("hoja_mauti"):
		var hoja := _Hoja.new()
		hoja.position = Vector2(32.0, 86.0) * CASILLA + Vector2(8, 10)
		get_parent().add_child(hoja)


## Sale algo del agua: los cangrejos trepan por la borda; las anguilas saltan por encima de la cubierta
func _soltar_oleada(oleada: Array) -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.call("mostrar_mensaje", String(oleada[3]))
	var entidades := get_parent()
	for i in int(oleada[1]):
		var lado := -1.0 if i % 2 == 0 else 1.0
		var c: CharacterBody2D = CANGREJO.new()
		var y := randf_range(-30.0, 14.0)
		c.global_position = position + Vector2(84.0 * lado, y)
		entidades.add_child(c)
		Sonido.efecto("mamba_salta", -10.0, c.global_position)
		# trepa por la borda hasta la cubierta
		var t := c.create_tween()
		t.tween_property(c, "global_position", position + Vector2(56.0 * lado, y), 0.5).set_trans(Tween.TRANS_BACK)
		t.tween_callback(func() -> void: _a_bordo.append(c))
	for i in int(oleada[2]):
		var a: Node2D = ANGUILA.new()
		a.viaje = self
		entidades.add_child(a)
		await get_tree().create_timer(0.9).timeout


## ¿Queda algo vivo a bordo o saltando?
func hay_peligro() -> bool:
	return not get_tree().get_nodes_in_group("enemigos").is_empty()


func _atracar(ya_estaba: bool) -> void:
	fase = Fase.ATRACADA
	position = _punto(_largo)
	if ya_estaba:
		_sujeta = false
		_crear_agua_y_vuelta()
		return
	Sonido.efecto("tablas_coger", 0.0, position)
	Impacto.temblar(1.5, 0.3)
	await get_tree().create_timer(0.6).timeout
	await CHARLA.hablar(self, "travesia_llegada")
	# Maisha baja al muelle de piedra
	_sujeta = false
	_maisha.set("puede_actuar", false)
	var muelle := Vector2(centro_rio(12.0) - 6.0, 12.0) * CASILLA + Vector2(8, 10)
	var t := create_tween()
	t.tween_property(_maisha, "global_position", position + Vector2(-56, 0), 0.4)
	t.tween_property(_maisha, "global_position", muelle, 0.6)
	await t.finished
	_maisha.set("puede_actuar", true)
	Estado.marcar("travesia_hecha")
	_crear_agua_y_vuelta()


## Atracada: el agua vuelve a ser agua, y desde la barca se puede volver al Embarcadero
func _crear_agua_y_vuelta() -> void:
	var region := get_tree().get_first_node_in_group("region")
	if region:
		region.call("_crear_agua", true)
	var vuelta := _Vuelta.new()
	vuelta.position = Vector2(-60, 6)
	add_child(vuelta)


class _Vuelta:
	extends Node2D
	var radio_interaccion := 34.0
	var altura_bocadillo := 30.0

	func _ready() -> void:
		add_to_group("interactuables")

	func interactuar() -> void:
		await CHARLA.hablar(self, "travesia_volver")
		Estado.ir_a("embarcadero_junco", "travesia")


class _Hoja:
	extends Node2D
	var radio_interaccion := 22.0
	var altura_bocadillo := 18.0
	var _t := 0.0

	func _ready() -> void:
		add_to_group("interactuables")
		var s := Sprite2D.new()
		s.texture = HOJA
		s.offset = Vector2(0, -6)
		add_child(s)

	func _process(delta: float) -> void:
		_t += delta
		queue_redraw()

	func _draw() -> void:
		draw_circle(Vector2(0, -6), 8.0 + sin(_t * 3.0) * 1.5, Color(0.96, 0.7, 0.44, 0.18))

	func interactuar() -> void:
		await CHARLA.hablar(self, "travesia_hoja")
		Estado.marcar("hoja_mauti")
		Sonido.fanfarria("objeto")
		queue_free()
