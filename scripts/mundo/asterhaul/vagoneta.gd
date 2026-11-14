extends StaticBody2D
## UNA VAGONETA DE ÁMBAR (Asterhaul): está sobre una VÍA (las casillas «=» del mapa). Un golpe de CARGA SÍSMICA la
## lanza rodando en esa dirección: sigue la vía (también en las curvas) hasta que se acaba. Si al final hay un
## DERRUMBE (asterhaul/muro_agrietado.gd, grupo «derrumbes»), lo aparta. Contra el sentido de la vía no se mueve.
## Dibujo: arte/mundos/asterhaul/desfiladero/vagoneta.png, 0 de lado · 1 de frente.

signal parada

const DIBUJO := preload("res://arte/mundos/asterhaul/desfiladero/vagoneta.png")
const VELOCIDAD := 120.0

var radio_carga := 6.0
var rodando := false
var _dir := Vector2i.ZERO
var _meta := Vector2.ZERO
var _filas: PackedStringArray
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("sismicos")
	add_to_group("vagonetas")
	_filas = get_tree().current_scene.get_node("Region")._filas
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -10)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(22, 12)
	forma.shape = caja
	forma.position = Vector2(0, -5)
	add_child(forma)
	_orientar(Vector2i.RIGHT if _es_via(casilla() + Vector2i.RIGHT) or _es_via(casilla() + Vector2i.LEFT) else Vector2i.UP)


func casilla() -> Vector2i:
	return Vector2i(floori(global_position.x / 16.0), floori((global_position.y - 6.0) / 16.0))


func _es_via(c: Vector2i) -> bool:
	return c.y >= 0 and c.y < _filas.size() and c.x >= 0 and c.x < _filas[c.y].length() and _filas[c.y][c.x] == "="


func _centro(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _orientar(d: Vector2i) -> void:
	_sprite.frame = 0 if d.x != 0 else 1


func recibir_carga(direccion: Vector2) -> bool:
	if rodando:
		return false
	var d := Vector2i(signi(int(roundf(direccion.x))), 0) if absf(direccion.x) >= absf(direccion.y) else Vector2i(0, signi(int(roundf(direccion.y))))
	if not _es_via(casilla() + d):
		Sonido.efecto("clinc", -4.0, global_position, 0.2)       # contra el sentido de la vía solo se queja
		return true
	_dir = d
	_meta = _centro(casilla() + d)
	rodando = true
	_orientar(d)
	Sonido.efecto("vagoneta_rodar", 0.0, global_position)
	return true


func _physics_process(delta: float) -> void:
	if not rodando:
		return
	global_position = global_position.move_toward(_meta, VELOCIDAD * delta)
	_sprite.position.y = sin(Time.get_ticks_msec() * 0.05) * 0.6      # traquetea
	if global_position.distance_to(_meta) > 0.5:
		return
	# en cada casilla: sigue recto si hay vía; si no, gira por donde siga; si no, se para
	var aqui := casilla()
	for d: Vector2i in [_dir, Vector2i(_dir.y, _dir.x), Vector2i(-_dir.y, -_dir.x)]:
		if _es_via(aqui + d):
			if d != _dir:
				_orientar(d)
			_dir = d
			_meta = _centro(aqui + d)
			return
	_parar()


func _parar() -> void:
	rodando = false
	_sprite.position.y = 0.0
	Impacto.temblar(2.0, 0.15)
	Sonido.efecto("cosechadora_choque", -6.0, global_position)
	var delante := global_position + Vector2(_dir) * 16.0
	for nodo in get_tree().get_nodes_in_group("derrumbes"):
		if (nodo as Node2D).global_position.distance_to(delante) < 30.0:
			nodo.call("romper")
	parada.emit()
