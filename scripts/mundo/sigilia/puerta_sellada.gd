extends StaticBody2D
## LA PUERTA SELLADA de Maandiko (Sigilia), arriba del Paso de la Escarcha: un arco de piedra morada con las hojas
## tapadas por un sello de TINTA QUIETA. Tapa el camino hasta que se derrite con el SIGILO DE FUEGO: tres sigilos
## (está en «derretibles»: sigilo_fuego.gd llama a derretir()). Dibujo puerta.png: 0 entera, 1 agrietada,
## 2 medio derretida, 3 abierta. Lo derretido se guarda (marca «sello_escarcha/<n>»; abierta, «puerta_sellada_abierta»).

signal abierta

const DIBUJO := preload("res://arte/mundos/sigilia/paso/puerta.png")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

var estado := 0
var radio_interaccion := 40.0
var altura_bocadillo := 70.0
var _sprite: Sprite2D
var _forma: CollisionShape2D
var _temblor := 0.0


func _ready() -> void:
	add_to_group("derretibles")
	add_to_group("puerta_sellada")
	add_to_group("interactuables")
	for n in 3:
		if Estado.tiene("sello_escarcha/%d" % (n + 1)):
			estado = n + 1
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.centered = false
	_sprite.offset = Vector2(-52, -88)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(60, 12)
	_forma.shape = caja
	_forma.position = Vector2(0, -6)
	add_child(_forma)
	# los pilares, siempre sólidos (solo se pasa por el hueco)
	for lado in [-1, 1]:
		var pilar := CollisionShape2D.new()
		var c := RectangleShape2D.new()
		c.size = Vector2(18, 12)
		pilar.shape = c
		pilar.position = Vector2(lado * 40, -6)
		add_child(pilar)
	_poner()


func _poner() -> void:
	_sprite.frame = estado
	_forma.set_deferred("disabled", estado >= 3)
	if estado >= 3:
		remove_from_group("derretibles")


func _process(delta: float) -> void:
	if _temblor > 0.0:
		_temblor = maxf(0.0, _temblor - delta)
		_sprite.position.x = sin(_temblor * 80.0) * 1.5 * _temblor * 3.0
	else:
		_sprite.position.x = 0.0


## El sigilo de fuego derrite un poco el sello
func derretir() -> void:
	if estado >= 3:
		return
	estado += 1
	Estado.marcar("sello_escarcha/%d" % estado)
	_temblor = 0.35
	Sonido.efecto("clinc", -2.0, global_position)
	var gotas: Node2D = ASTILLAS.new()
	gotas.cantidad = 14
	gotas.position = global_position + Vector2(0, -30)
	get_parent().add_child(gotas)
	if estado >= 3:
		Estado.marcar("puerta_sellada_abierta")
		Sonido.efecto("portal_abre", 0.0, global_position)
		Impacto.temblar(2.0, 0.3)
		abierta.emit()
	_poner()


func interactuar() -> void:
	await CHARLA.hablar(self, "puerta_sellada")
