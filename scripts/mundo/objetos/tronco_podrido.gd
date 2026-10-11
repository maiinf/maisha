extends StaticBody2D
## TRONCO PODRIDO (Bosque Cobrizo): un tronco caído, blando por dentro. Estorba el paso.
## El cetro solo lo hace temblar; una semilla lo parte y deja MADERA en el suelo (la que pide Tawi).

const TEXTURA := preload("res://arte/mundos/raiz/bosque/tronco_podrido.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

@export var marca := ""          # se pone al partirlo: así sigue partido en otras visitas

var rota := false
var _sprite: Sprite2D
var _forma: CollisionShape2D
var _avisado := false


func _ready() -> void:
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("troncos_podridos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 15.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-17, -17)
	add_child(_sprite)
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	if gestor:
		gestor.aplicar_a(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(30, 8)
	_forma.shape = caja
	_forma.position = Vector2(0, -4)
	add_child(_forma)
	if marca != "" and Estado.tiene(marca):
		_partir(false)


## El cetro lo hace temblar (y la primera vez, una pista)
func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if rota:
		return false
	var t := create_tween()
	t.tween_property(_sprite, "position:x", 1.0, 0.03)
	t.tween_property(_sprite, "position:x", 0.0, 0.05)
	if not _avisado:
		_avisado = true
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Está blando y podrido por dentro... una semilla lo partiría")
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if rota or tipo != "explosion":
		return
	_partir(true)


func _partir(ahora: bool) -> void:
	rota = true
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = 1
	_forma.set_deferred("disabled", true)
	if marca != "":
		Estado.marcar(marca)
	var madera: Node2D = RECOGIBLE.new()
	madera.objeto = "madera"
	madera.marca = marca + "/recogido" if marca != "" else ""
	madera.color_halo = Color(0.85, 0.6, 0.35)
	madera.position = position + Vector2(0, 4)
	get_parent().add_child.call_deferred(madera)
	if ahora:
		Sonido.efecto("tablas_coger", 0.0, global_position)
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 12
		astillas.position = global_position + Vector2(0, -6)
		get_parent().add_child(astillas)
		var t := create_tween()
		t.tween_property(_sprite, "position:x", 2.0, 0.04)
		t.tween_property(_sprite, "position:x", -2.0, 0.06)
		t.tween_property(_sprite, "position:x", 0.0, 0.04)
