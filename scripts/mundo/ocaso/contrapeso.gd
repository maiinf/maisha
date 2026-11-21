extends StaticBody2D
## EL CONTRAPESO DEL OESTE (El Horizonte Inmóvil): el bloque de basalto que tira de la Cadena del Oeste de Jua-Giza.
## Mientras la cadena aguanta (`activo`), cada CARGA SÍSMICA lo agrieta (`golpeado`); a la segunda se rompe.
## Dibujo: arte/mundos/ocaso/horizonte/contrapeso.png (0 entero · 1 roto).

signal golpeado

const DIBUJO := preload("res://arte/mundos/ocaso/horizonte/contrapeso.png")

var activo := false
var roto := false
var radio_carga := 10.0
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("sismicos")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -22)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(28, 8)
	forma.shape = caja
	forma.position = Vector2(0, -4)
	add_child(forma)


func recibir_carga(direccion: Vector2) -> bool:
	if not activo or roto:
		return false
	Sonido.efecto("contrapeso_cruje", 0.0, global_position)
	Impacto.chispa(global_position + Vector2(0, -20), direccion, Color("8a4ab8"))
	golpeado.emit()
	return true


func romper() -> void:
	roto = true
	_sprite.frame = 1
	remove_from_group("sismicos")
