extends Node2D
## DERRUMBE («"» en el Camino Cobrizo): la boca de la vieja galería de la mina, tapada por piedras y maderos.
## No se puede pasar. Cuando se pone su «marca» (Fuko lo despeja al devolverle sus campanillas), los montones
## se deshacen uno a uno, de abajo arriba, con polvo y piedrecitas, y queda el paso libre.
## Dibujo: arte/mundos/raiz/camino/derrumbe.png (herramientas/pintar_camino.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/raiz/camino/derrumbe.png")

var casillas: Array[Vector2i] = []
var marca := ""
var _quitadas := 0                # cuántas casillas se han despejado ya (se anima al despejarlo)
var _cuerpo: StaticBody2D
var _montones: Array[Sprite2D] = []


func _ready() -> void:
	add_to_group("derrumbes")
	# de arriba abajo, para que los de delante tapen a los de detrás
	casillas.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y or (a.y == b.y and a.x < b.x))
	if Estado.tiene(marca):
		_quitadas = casillas.size()
		return
	var entidades := get_tree().get_first_node_in_group("region")
	var padre: Node = self
	if entidades and entidades.get("_entidades"):
		padre = entidades.get("_entidades")
	for c in casillas:
		var s := Sprite2D.new()
		s.texture = DIBUJO
		s.hframes = 3
		s.frame = (c.x * 7 + c.y * 3) % 3
		s.centered = false
		s.offset = Vector2(-8, -24)
		s.position = Vector2(c) * R.CASILLA + Vector2(8, 16 + ((c.x + c.y) % 2))
		padre.add_child.call_deferred(s)
		_montones.append(s)
	_cuerpo = StaticBody2D.new()
	add_child(_cuerpo)
	for c in casillas:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(R.CASILLA, R.CASILLA)
		forma.shape = caja
		forma.position = Vector2(c) * R.CASILLA + Vector2.ONE * 8
		_cuerpo.add_child(forma)
	Estado.marca_puesta.connect(_al_poner_marca)


func despejado() -> bool:
	return _quitadas >= casillas.size()


## (para las pruebas y el mapa: se puede llamar «arreglada», como a la pasarela rota)
func arreglada() -> bool:
	return despejado()


func _al_poner_marca(m: String) -> void:
	if m != marca:
		return
	# se deshacen de abajo arriba (desde el lado de Maisha), uno a uno
	var orden := range(_montones.size())
	orden.reverse()
	var t := create_tween()
	for k in orden:
		t.tween_callback(func() -> void:
			var s: Sprite2D = _montones[k]
			Sonido.efecto("piedra_rompe", 0.0, s.global_position)
			Impacto.temblar(1.0, 0.1)
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 6
			astillas.fuerza = 45.0
			astillas.position = s.position + Vector2(0, -6)
			s.get_parent().add_child(astillas)
			var tw := s.create_tween().set_parallel(true)
			tw.tween_property(s, "scale", Vector2(1.2, 0.2), 0.25)
			tw.tween_property(s, "modulate:a", 0.0, 0.3)
			tw.chain().tween_callback(s.queue_free)
			_quitadas += 1)
		t.tween_interval(0.16)
	t.tween_callback(func() -> void:
		if _cuerpo:
			_cuerpo.queue_free()
			_cuerpo = null
		Sonido.efecto("construir"))
