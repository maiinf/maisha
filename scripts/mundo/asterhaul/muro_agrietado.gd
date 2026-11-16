extends StaticBody2D
## UN MURO AGRIETADO (Asterhaul): un tapón de roca que cierra un paso. Con la CARGA SÍSMICA se viene abajo
## (está en «sismicos»). Con `dibujo = "derrumbe"` y `con_carga = false` es un DERRUMBE: pesa demasiado para
## Maisha y solo lo aparta una VAGONETA lanzada contra él (asterhaul/vagoneta.gd, grupo «derrumbes»).
## Una vez roto, queda roto (su `marca`).
## Entero, corta la vía (está en «topes_via»: las vagonetas se paran delante).
## Dibujo: arte/mundos/asterhaul/<dibujo>.png, 0 entero · 1 roto («desfiladero/muro», «desfiladero/derrumbe»,
## «galerias/barricada»).

signal roto

const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

@export var marca := ""
@export var dibujo := "desfiladero/muro"
@export var con_carga := true
## (lo que añade al alcance de la carga: es ancho)
var radio_carga := 18.0
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("sismicos")
	add_to_group("topes_via")
	if not con_carga:
		add_to_group("derrumbes")
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/asterhaul/%s.png" % dibujo)
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -16)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(48, 20)
	_forma.shape = caja
	_forma.position = Vector2(0, -6)
	add_child(_forma)
	if marca != "" and Estado.tiene(marca):
		_quedar_roto()


func esta_roto() -> bool:
	return _sprite.frame == 1


func es_tope() -> bool:
	return not esta_roto()


func _quedar_roto() -> void:
	_sprite.frame = 1
	_sprite.z_index = -1
	_forma.set_deferred("disabled", true)
	remove_from_group("sismicos")
	remove_from_group("derrumbes")


func recibir_carga(_direccion: Vector2) -> bool:
	if esta_roto():
		return false
	if not con_carga:
		Sonido.efecto("clinc", -2.0, global_position, 0.2)
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Pesa demasiado: hace falta algo con ruedas")
		return true
	romper()
	return true


func romper() -> void:
	if esta_roto():
		return
	_quedar_roto()
	if marca != "":
		Estado.marcar(marca)
	Sonido.efecto("roca_romper", 0.0, global_position)
	Impacto.temblar(4.0, 0.3)
	for k in 3:
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 10
		astillas.position = global_position + Vector2((k - 1) * 14, -12)
		get_parent().add_child(astillas)
	roto.emit()
