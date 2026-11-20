extends Node
## LAS CAÍDAS AL VACÍO (Asterhaul: la Aguja Caída y la Cámara de la Resonancia del Núcleo). Lo pone la escena.
## Las casillas «=» dentro de `zona` (px) son vacío: si Maisha pisa una sin nada que la sostenga (grupo «sostenes»
## → `firme()`: las losas de cristal, los peñascos), cae: pierde 1 hoja y vuelve al último suelo firme que pisó.

## dónde cuenta el vacío (por defecto, todo el mapa)
var zona := Rect2(-100000, -100000, 200000, 200000)
## en las Dunas de Penumbra no se cae: se HUNDE en la arena movediza (baja despacio en vez de encogerse)
var hundir := false
var cayendo := false
var _escena: Node
var _filas: PackedStringArray
var _firme := Vector2.ZERO


func _ready() -> void:
	_escena = get_parent()
	_filas = _escena.get_node("Region")._filas
	_firme = _escena._maisha.global_position


func _letra(p: Vector2) -> String:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return _filas[y][x] if y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() else "0"


## ¿Hay algo bajo ese punto de vacío?
func sostenida(p: Vector2) -> bool:
	for s in get_tree().get_nodes_in_group("sostenes"):
		if s.call("firme", p):
			return true
	return false


func _process(_delta: float) -> void:
	var maisha: Node2D = _escena._maisha
	if cayendo or maisha.get("esta_caida"):
		return
	var p := maisha.global_position
	var letra := _letra(p)
	if letra == "=" and zona.has_point(p):
		if not sostenida(p):
			_caer()
	elif not (letra in ["0", "≈", "="]):
		_firme = p


func _caer() -> void:
	cayendo = true
	var maisha: Node2D = _escena._maisha
	maisha.set("puede_actuar", false)
	Sonido.efecto("sombra_repta" if hundir else "kipanga_picado", -4.0, maisha.global_position, 0.3)
	var sprite := maisha.get_node("Sprite") as Node2D
	var y_sprite := sprite.position.y
	var t := create_tween().set_parallel(true)
	if hundir:
		t.tween_property(sprite, "position:y", sprite.position.y + 14.0, 0.7)
		t.tween_property(maisha, "modulate:a", 0.0, 0.7).set_delay(0.2)
	else:
		t.tween_property(sprite, "scale", Vector2(0.3, 0.3), 0.45)
		t.tween_property(maisha, "modulate:a", 0.0, 0.45)
	await t.finished
	if not is_inside_tree():
		return
	maisha.set("_invulnerable", 0.0)
	maisha.call("recibir_danio", 1, maisha.global_position, "caida")
	var volver := func() -> void:
		sprite.scale = Vector2.ONE
		if hundir:
			sprite.position.y = y_sprite
		maisha.modulate.a = 1.0
		maisha.set("puede_actuar", true)
		cayendo = false
	if maisha.get("esta_caida"):
		maisha.global_position = _firme      # (era su última hoja: se levanta como siempre)
		volver.call()
		return
	_escena._hud.fundido(func() -> void:
		maisha.global_position = _firme
		maisha.set("_empuje", Vector2.ZERO)
		maisha.set("mareo", 0.0)
		volver.call())
