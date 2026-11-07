extends Node2D
## UNA PLACA DE TINTA HELADA (Canal de Tinta): la deja el Sigilo de Hielo al caer sobre tinta líquida («~»).
##   - Flota y la CORRIENTE la lleva hacia el este; se para contra un muelle, una compuerta cerrada («ŧ») u otra placa.
##   - Maisha SUBE andando hacia ella desde la orilla (salta encima); arriba se mueve por la placa, que la lleva.
##     Baja andando hacia tierra firme o salta a otra placa que esté pegada.
##   - Dura VIDA s; los últimos AVISO s se agrieta y parpadea. Si se deshace con Maisha encima, se hunde en la tinta:
##     pierde una hoja y vuelve a la orilla de la que subió.
## Una compuerta está abierta si está la marca «compuerta/<x>» (x = su columna).

const TAM := Vector2(40, 30)          # el trozo que se pisa (desde el centro)
const CORRIENTE := 18.0               # px/s hacia el este
const VIDA := 24.0
const AVISO := 4.0
const SUBIR := 10.0                   # a cuánto de la placa hay que andar hacia ella para saltar encima
const HIELO := [Color("1f3550"), Color("3c6d93"), Color("7fb6d8"), Color("bfe3f3"), Color("eefaff")]

var vida := VIDA
var quieta := false                   # (true mientras algo la frena)
var _maisha: CharacterBody2D
var _agua: Node
var _filas: PackedStringArray
var _orilla := Vector2.ZERO           # de dónde subió Maisha (para volver si se hunde)
var _forma: PackedVector2Array
var _t := 0.0
var _hundiendo := false


## Endurece la tinta en `centro` si allí hay tinta líquida y no hay ya otra placa encima. Devuelve la placa (o null).
static func helar_en(padre: Node, centro: Vector2) -> Node2D:
	var escena := padre.get_tree().current_scene
	var region := escena.get_node_or_null("Region")
	if region == null:
		return null
	var filas: PackedStringArray = region._filas
	var c := Vector2i(floori(centro.x / 16.0), floori(centro.y / 16.0))
	if c.y < 0 or c.y >= filas.size() or c.x < 0 or c.x >= filas[c.y].length() or filas[c.y][c.x] != "~":
		return null
	for p in padre.get_tree().get_nodes_in_group("placas_hielo"):
		if absf((p as Node2D).global_position.x - centro.x) < TAM.x and absf((p as Node2D).global_position.y - centro.y) < TAM.y:
			return null
	var placa: Node2D = load("res://scripts/mundo/sigilia/placa_hielo.gd").new()
	placa.position = centro
	padre.add_child(placa)
	return placa


func _ready() -> void:
	add_to_group("placas_hielo")
	z_index = -1                      # (por debajo de quien la pisa)
	process_physics_priority = 10     # (después de que Maisha se mueva)
	var escena := get_tree().current_scene
	_filas = escena.get_node("Region")._filas
	_agua = escena.get_node_or_null("Region/Agua")
	_maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	# un témpano irregular (cada placa, distinto)
	var azar := RandomNumberGenerator.new()
	azar.seed = int(position.x * 7.0 + position.y * 13.0)
	for k in 9:
		var a := k * TAU / 9.0
		var r := Vector2(TAM.x * 0.5 + 3.0, TAM.y * 0.5 + 2.0) * azar.randf_range(0.86, 1.04)
		_forma.append((Vector2(cos(a), sin(a)) * r).round())


func _placa_de_maisha() -> Node:
	return _maisha.get_meta("placa") if _maisha.has_meta("placa") else null


func encima() -> bool:
	return is_instance_valid(_maisha) and _placa_de_maisha() == self


func contiene(p: Vector2, margen := 0.0) -> bool:
	var d := p - global_position
	return absf(d.x) <= TAM.x * 0.5 + margen and absf(d.y) <= TAM.y * 0.5 + margen


func _physics_process(delta: float) -> void:
	_t += delta
	if _hundiendo:
		return
	var antes := position
	_derivar(delta)
	vida -= delta
	if not is_instance_valid(_maisha):
		return
	if encima():
		_llevar(position - antes)
	elif _placa_de_maisha() == null and contiene(_maisha.global_position, SUBIR):
		var hacia := global_position - _maisha.global_position
		# (la tecla, no la velocidad: contra el borde de la tinta, Maisha no se mueve)
		var quiere := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo")
		if quiere.dot(hacia) > 0.0 and not _es_tinta_en(_maisha.global_position):
			_subir()
	if vida <= 0.0:
		_deshacer()


## La corriente: hacia el este, mientras delante haya tinta libre
func _derivar(delta: float) -> void:
	var paso := CORRIENTE * delta
	var frente := position.x + TAM.x * 0.5 + 2.0 + paso
	quieta = false
	for dy in [-TAM.y * 0.5 + 2.0, 0.0, TAM.y * 0.5 - 2.0]:
		if not _es_tinta_en(Vector2(frente, position.y + dy)):
			quieta = true
	for p in get_tree().get_nodes_in_group("placas_hielo"):
		if p != self and p.position.x > position.x and p.position.x - position.x < TAM.x + 1.0 + paso \
				and absf(p.position.y - position.y) < TAM.y:
			quieta = true
	if not quieta:
		position.x += paso


func _es_tinta_en(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	if y < 0 or y >= _filas.size() or x < 0 or x >= _filas[y].length():
		return false
	var c := _filas[y][x]
	return c == "~" or (c == "ŧ" and Estado.tiene("compuerta/%d" % x))


func _es_tierra_en(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	if y < 0 or y >= _filas.size() or x < 0 or x >= _filas[y].length():
		return false
	return not (_filas[y][x] in ["~", "ŧ", "0"])


## Maisha va encima: se mueve con la placa; si anda fuera, baja a tierra, salta a otra placa o se queda en el borde
func _llevar(movida: Vector2) -> void:
	var p := _maisha.global_position + movida
	if contiene(p):
		_maisha.global_position = p
		return
	for otra in get_tree().get_nodes_in_group("placas_hielo"):
		if otra != self and otra.contiene(p, 2.0):
			_maisha.set_meta("placa", otra)
			_maisha.global_position = p
			return
	if _es_tierra_en(p) and _es_tierra_en(p + (p - global_position).normalized() * 6.0):
		_bajar()
		_maisha.global_position = p
		return
	var d := p - global_position
	_maisha.global_position = global_position + Vector2(clampf(d.x, -TAM.x * 0.5, TAM.x * 0.5), clampf(d.y, -TAM.y * 0.5, TAM.y * 0.5))


func _subir() -> void:
	_orilla = _maisha.global_position
	_maisha.set_meta("placa", self)
	if _agua:
		_maisha.add_collision_exception_with(_agua)
	var d := _maisha.global_position - global_position
	var dentro := global_position + Vector2(clampf(d.x, -TAM.x * 0.5 + 4.0, TAM.x * 0.5 - 4.0), clampf(d.y, -TAM.y * 0.5 + 4.0, TAM.y * 0.5 - 4.0))
	_maisha.global_position = dentro
	Sonido.efecto("cristal", -10.0, dentro, 0.2)


func _bajar() -> void:
	_maisha.remove_meta("placa")
	if _agua:
		_maisha.remove_collision_exception_with(_agua)


## Se deshace: si Maisha va encima, se hunde en la tinta y vuelve a la orilla
func _deshacer() -> void:
	_hundiendo = true
	if encima():
		_bajar()
		_maisha.set("puede_actuar", false)
		Sonido.efecto("maisha_cae", -2.0, _maisha.global_position)
		var t := _maisha.create_tween()
		t.tween_property(_maisha, "scale", Vector2(0.5, 0.2), 0.35)
		t.parallel().tween_property(_maisha, "modulate", Color(0.2, 0.15, 0.3, 0.0), 0.35)
		await t.finished
		if is_instance_valid(_maisha):
			_maisha.global_position = _orilla
			_maisha.scale = Vector2.ONE
			_maisha.modulate = Color.WHITE
			_maisha.set("puede_actuar", true)
			_maisha.call("perder_hoja")
	var f := create_tween()
	f.tween_property(self, "modulate:a", 0.0, 0.4)
	await f.finished
	queue_free()


func _exit_tree() -> void:
	if encima():
		_bajar()


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	# los últimos segundos parpadea
	var aviso := vida < AVISO
	if aviso and int(_t * (4.0 + (AVISO - vida) * 2.0)) % 2 == 0:
		modulate.a = 0.75
	elif not _hundiendo:
		modulate.a = 1.0
	# el borde que se hunde en la tinta (oscuro, un poco más abajo), la cara de hielo y la luz de arriba
	var hondo := PackedVector2Array()
	for p in _forma:
		hondo.append(p + Vector2(0, 3))
	draw_colored_polygon(hondo, HIELO[0])
	draw_colored_polygon(_forma, HIELO[1])
	var cara := PackedVector2Array()
	for p in _forma:
		cara.append((p * 0.86 + Vector2(-1, -1)).round())
	draw_colored_polygon(cara, HIELO[2])
	var luz := PackedVector2Array()
	for p in _forma:
		luz.append((p * 0.5 + Vector2(-5, -4)).round())
	draw_colored_polygon(luz, HIELO[3])
	# vetas de tinta atrapada dentro y destellos
	draw_line(Vector2(-12, 3), Vector2(-2, 6), Color(HIELO[0], 0.5), 1.0)
	draw_line(Vector2(4, -6), Vector2(13, -2), Color(HIELO[0], 0.4), 1.0)
	draw_rect(Rect2(-9, -8, 2, 1), HIELO[4])
	draw_rect(Rect2(6, -3, 1, 1), HIELO[4])
	# la línea clara del canto
	for i in _forma.size():
		var a := _forma[i]
		var b := _forma[(i + 1) % _forma.size()]
		if a.y + b.y < 0.0:
			draw_line(a, b, HIELO[4], 1.0)
	# grietas al deshacerse
	if aviso:
		var g := clampf((AVISO - vida) / AVISO, 0.0, 1.0)
		draw_line(Vector2(-2, -12), Vector2(-2, -12).lerp(Vector2(3, 2), g), HIELO[0], 1.0)
		draw_line(Vector2(3, 2), Vector2(3, 2).lerp(Vector2(-10, 10), g), HIELO[0], 1.0)
		draw_line(Vector2(3, 2), Vector2(3, 2).lerp(Vector2(15, 6), g), HIELO[0], 1.0)
	# la estela en la tinta detrás, si se mueve
	if not quieta:
		for k in 3:
			var x := -TAM.x * 0.5 - 4.0 - k * 5.0 - fmod(_t * 10.0, 5.0)
			draw_line(Vector2(x, -6 + k * 5), Vector2(x - 3, -6 + k * 5), Color(0.6, 0.5, 0.85, 0.5 - k * 0.12), 1.0)
