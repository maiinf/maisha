extends StaticBody2D
## UNA VELA DE SOMBRA (las Dunas de Penumbra): un mástil con una vela de tela oscura. Un golpe de cetro la gira un
## cuarto: DE CARA (la tela ancha, mirando al este y al oeste) o DE CANTO (mirando al norte y al sur). Solo echa su
## sombra larga (ocaso/sol.gd) cuando el sol le da en la tela: de cara, con el sol al oeste o al este; de canto,
## con el sol al sur. Se guarda (`marca`, Estado.extra["velas"]).
## Dibujo: arte/mundos/ocaso/dunas/vela.png (0 de cara · 1 de canto).

const DIBUJO := preload("res://arte/mundos/ocaso/dunas/vela.png")

var marca := ""
var de_canto := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("velas_sombra")
	if marca != "":
		de_canto = bool(Estado.extra.get("velas", {}).get(marca, de_canto))
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -28)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_sprite.frame = 1 if de_canto else 0


## ¿Le da el sol en la tela a esta hora? (0 oeste · 1 sur · 2 este)
func proyecta(hora: int) -> bool:
	return de_canto == (hora == 1)


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	de_canto = not de_canto
	_sprite.frame = 1 if de_canto else 0
	if marca != "":
		var velas: Dictionary = Estado.extra.get("velas", {}).duplicate()
		velas[marca] = de_canto
		Estado.extra["velas"] = velas
		Estado.guardar_pronto()
	Sonido.efecto("espejo_gira", -2.0, global_position, 0.1)
	var sol := get_tree().get_first_node_in_group("sol")
	if sol:
		sol.recalcular()
		Sonido.efecto("sombra_tiende", -4.0, global_position)
	return true
