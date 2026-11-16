extends StaticBody2D
## UN BLOQUE-IMÁN (Asterhaul, la Fundición): hierro meteórico macizo. No se empuja. El PULSO MAGNÉTICO (está en
## «magneticos») lo trae hacia Maisha en línea recta, casilla a casilla, hasta que algo lo para (una pared, la
## escoria, otro bloque), hasta quedar a su lado... o hasta ENCAJAR en una PLACA DE PRESIÓN (`placas`: casillas).
## Sirve de peso para las placas y de escudo contra lo que escupen los Kovu («paran_escoria»).
## Dibujo: arte/mundos/asterhaul/fundicion/bloque.png, 0 quieto · 1 imantado.

signal parado(casilla: Vector2i)

const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/bloque.png")
const RADIO := 120.0
const VELOCIDAD := 110.0

## las casillas con placa (las pone la escena): al pasar por una, se queda
var placas: Array[Vector2i] = []
var deslizando := false
var _dir := Vector2i.ZERO
var _meta := Vector2.ZERO
var _filas: PackedStringArray
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("magneticos")
	add_to_group("bloques_iman")
	add_to_group("paran_escoria")
	_filas = get_tree().current_scene.get_node("Region")._filas
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -10)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(15, 12)
	forma.shape = caja
	forma.position = Vector2(0, -5)
	add_child(forma)


func casilla() -> Vector2i:
	return Vector2i(floori(global_position.x / 16.0), floori((global_position.y - 6.0) / 16.0))


func _centro(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


## ¿Puede entrar en esa casilla? (suelo, sin otro bloque y sin Maisha)
func _libre(c: Vector2i) -> bool:
	if c.y < 0 or c.y >= _filas.size() or c.x < 0 or c.x >= _filas[c.y].length() or _filas[c.y][c.x] in ["0", "≈"]:
		return false
	for b in get_tree().get_nodes_in_group("bloques_iman"):
		if b != self and b.casilla() == c:
			return false
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	return maisha == null or Vector2i(floori(maisha.global_position.x / 16.0), floori((maisha.global_position.y - 6.0) / 16.0)) != c


func recibir_pulso(origen: Vector2) -> bool:
	if deslizando or origen.distance_to(global_position) > RADIO:
		return false
	var d := origen - global_position
	_dir = Vector2i(signi(int(d.x)), 0) if absf(d.x) >= absf(d.y) else Vector2i(0, signi(int(d.y)))
	if _dir == Vector2i.ZERO or not _libre(casilla() + _dir):
		Sonido.efecto("clinc", -6.0, global_position, 0.2)
		return false
	deslizando = true
	_sprite.frame = 1
	_meta = _centro(casilla() + _dir)
	Sonido.efecto("bloque_atraer", -2.0, global_position)
	return true


func _physics_process(delta: float) -> void:
	if not deslizando:
		return
	global_position = global_position.move_toward(_meta, VELOCIDAD * delta)
	if global_position.distance_to(_meta) > 0.5:
		return
	var aqui := casilla()
	if aqui in placas or not _libre(aqui + _dir):
		deslizando = false
		_sprite.frame = 0
		Sonido.efecto("cosechadora_choque", -10.0, global_position)
		parado.emit(aqui)
		return
	_meta = _centro(aqui + _dir)
