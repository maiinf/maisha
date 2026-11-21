extends StaticBody2D
## EL PEDESTAL DE LAS TRES PESAS (El Horizonte Inmóvil): con Acción, si Maisha lleva la Pesa del Oeste, la del Este
## y la del Sur, las encaja (`marca`) y avisa (`puestas`). Si falta alguna, Maisha lo piensa.
## Dibujo: arte/mundos/ocaso/horizonte/pedestal.png (0 vacío · 1 con las tres pesas).

signal puestas

const CHARLA := preload("res://scripts/mundo/charla.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/horizonte/pedestal.png")
const PESAS := ["peso_oeste", "peso_este", "peso_sur"]

var marca := ""
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("interactuables")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -15)
	_sprite.frame = 1 if Estado.tiene(marca) else 0
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(40, 10)
	forma.shape = caja
	forma.position = Vector2(0, -5)
	add_child(forma)


func interactuar() -> void:
	if Estado.tiene(marca):
		return
	if not PESAS.all(func(p: String) -> bool: return Estado.cuantos(p) > 0):
		await CHARLA.hablar(self, "horizonte_pedestal_falta")
		return
	for p in PESAS:
		Estado.quitar(p)
	Estado.marcar(marca)
	_sprite.frame = 1
	Sonido.efecto("pesas_encajan", 0.0, global_position)
	Impacto.temblar(3.0, 0.5)
	Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color(1.0, 0.85, 0.5))
	puestas.emit()
