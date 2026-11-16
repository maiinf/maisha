extends StaticBody2D
## UNA VAGONETA DE ÁMBAR (Asterhaul): está sobre una VÍA (las casillas «=» del mapa). Un golpe de CARGA SÍSMICA la
## lanza rodando en esa dirección: sigue la vía (obedece a los CAMBIOS DE AGUJAS y toma las curvas: asterhaul/via.gd)
## hasta que se acaba o hasta que algo la corta (un tope: barricada, reja, otra vagoneta). Si lo que tiene delante
## al pararse es un DERRUMBE o una BARRICADA (asterhaul/muro_agrietado.gd, grupo «derrumbes»), lo rompe.
## Rodando, aplasta a los Mchimbaji («mchimbajis») y, si le da al Kifaru («kifarus»), le abre la coraza.
## Contra el sentido de la vía no se mueve.
## Dibujo: arte/mundos/asterhaul/desfiladero/vagoneta.png, 0 de lado · 1 de frente.

signal parada

const DIBUJO := preload("res://arte/mundos/asterhaul/desfiladero/vagoneta.png")
const VIA := preload("res://scripts/mundo/asterhaul/via.gd")
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
	add_to_group("topes_via")
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
	_orientar(Vector2i.RIGHT if VIA.es_via(_filas, casilla() + Vector2i.RIGHT) or VIA.es_via(_filas, casilla() + Vector2i.LEFT) else Vector2i.UP)


func casilla() -> Vector2i:
	return VIA.casilla(global_position)


## (para las demás cosas que ruedan: una vagoneta siempre corta la vía)
func es_tope() -> bool:
	return true


func _orientar(d: Vector2i) -> void:
	_sprite.frame = 0 if d.x != 0 else 1


func recibir_carga(direccion: Vector2) -> bool:
	if rodando:
		return false
	var d := Vector2i(signi(int(roundf(direccion.x))), 0) if absf(direccion.x) >= absf(direccion.y) else Vector2i(0, signi(int(roundf(direccion.y))))
	if not VIA.es_via(_filas, casilla() + d):
		Sonido.efecto("clinc", -4.0, global_position, 0.2)       # contra el sentido de la vía solo se queja
		return true
	_dir = d
	rodando = true
	_orientar(d)
	Sonido.efecto("vagoneta_rodar", 0.0, global_position)
	_avanzar(casilla() + d)
	return true


## Sigue hacia la casilla `c`... si nada la corta
func _avanzar(c: Vector2i) -> void:
	if VIA.tope(get_tree(), c, self) != null:
		_parar()
		return
	_meta = VIA.centro(c)


func _physics_process(delta: float) -> void:
	if not rodando:
		return
	global_position = global_position.move_toward(_meta, VELOCIDAD * delta)
	_sprite.position.y = sin(Time.get_ticks_msec() * 0.05) * 0.6      # traquetea
	for m in get_tree().get_nodes_in_group("mchimbajis"):
		if (m as Node2D).global_position.distance_to(global_position) < 13.0:
			m.call("aplastar")
	for k in get_tree().get_nodes_in_group("kifarus"):
		if (k as Node2D).global_position.distance_to(global_position) < 34.0 and k.call("recibir_vagoneta"):
			_parar()
			return
	if global_position.distance_to(_meta) > 0.5:
		return
	var d := VIA.seguir(get_tree(), _filas, casilla(), _dir)
	if d == Vector2i.ZERO:
		_parar()
		return
	if d != _dir:
		_orientar(d)
	_dir = d
	_avanzar(casilla() + d)


func _parar() -> void:
	if not rodando:
		return
	rodando = false
	_sprite.position.y = 0.0
	Impacto.temblar(2.0, 0.15)
	Sonido.efecto("cosechadora_choque", -6.0, global_position)
	var delante := global_position + Vector2(_dir) * 16.0
	for nodo in get_tree().get_nodes_in_group("derrumbes"):
		if (nodo as Node2D).global_position.distance_to(delante) < 30.0:
			nodo.call("romper")
	parada.emit()
