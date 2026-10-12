extends Node2D
## LA BALSA DE KASIA («"» en la Orilla de Juncos): las casillas «"» son el trecho de río que cruza la balsa, del
## embarcadero (oeste) al banco de arena (este). El agua no se puede pisar nunca.
##   - Sin su «marca» la balsa está medio hundida junto al embarcadero, rota: al mirarla, Maisha piensa que así no
##     se puede usar.
##   - Con la marca (Kasia la arregla al devolverle sus remos) flota en el embarcadero. Con Acción, Maisha se sube y
##     la balsa cruza sola al otro lado, despacio y meciéndose; allí Maisha baja a tierra. Para volver, igual.
## Dibujo: arte/mundos/raiz/orilla/balsa.png (herramientas/pintar_orilla.py): 0 hundida · 1 a flote.

const R := preload("res://scripts/combate/reglas_combate.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const DIBUJO := preload("res://arte/mundos/raiz/orilla/balsa.png")
const VELOCIDAD := 34.0           # píxeles por segundo cruzando

var casillas: Array[Vector2i] = []
var marca := ""
var radio_interaccion := 30.0
var altura_bocadillo := 20.0
var en_el_este := false           # de qué lado del río está la balsa
var cruzando := false
var _oeste := Vector2.ZERO        # dónde espera la balsa en cada orilla
var _este := Vector2.ZERO
var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("balsas")
	add_to_group("interactuables")
	z_index = -5
	var minx := 1 << 30
	var maxx := -(1 << 30)
	var ys: Array[int] = []
	for c in casillas:
		minx = mini(minx, c.x)
		maxx = maxi(maxx, c.x)
		if not c.y in ys:
			ys.append(c.y)
	var cy := 0.0
	for y in ys:
		cy += y
	cy = (cy / ys.size() + 0.5) * R.CASILLA
	_oeste = Vector2((minx + 0.9) * R.CASILLA, cy)
	_este = Vector2((maxx + 0.1) * R.CASILLA, cy)
	# el agua del trecho de la balsa no se puede pisar
	var cuerpo := StaticBody2D.new()
	add_child(cuerpo)
	for c in casillas:
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(R.CASILLA, R.CASILLA)
		forma.shape = caja
		forma.position = Vector2(c) * R.CASILLA + Vector2.ONE * 8
		cuerpo.add_child(forma)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.frame = 1 if Estado.tiene(marca) else 0
	_sprite.position = _oeste
	add_child(_sprite)
	Estado.marca_puesta.connect(func(m: String) -> void:
		if m == marca:
			_sacar_del_agua())


func arreglada() -> bool:
	return Estado.tiene(marca)


## (con Acción se habla con la balsa donde esté: en una orilla o en la otra)
func punto_interaccion() -> Vector2:
	return _sprite.global_position


func interactuar() -> void:
	await usar()


## Kasia la saca del agua: la balsa sube, chorrea y queda a flote
func _sacar_del_agua() -> void:
	var t := create_tween()
	t.tween_property(_sprite, "position:y", _oeste.y + 4.0, 0.3)
	t.tween_callback(func() -> void:
		_sprite.frame = 1
		Sonido.efecto("kambare_salta", -8.0, _sprite.global_position))
	t.tween_property(_sprite, "position:y", _oeste.y, 0.5).set_trans(Tween.TRANS_BACK)


func usar() -> void:
	if cruzando:
		return
	if not arreglada():
		await CHARLA.hablar(self, "orilla_balsa_rota")
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	cruzando = true
	maisha.set("puede_actuar", false)
	var desde := _sprite.position
	var hasta := _oeste if en_el_este else _este
	# Maisha se sube (un saltito) y la balsa cruza meciéndose
	var sube := create_tween()
	sube.tween_property(maisha, "global_position", global_position + desde + Vector2(0, -6), 0.25)
	await sube.finished
	Sonido.efecto("tablas_coger", -4.0, maisha.global_position)
	var dura := desde.distance_to(hasta) / VELOCIDAD
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "position", hasta, dura).set_trans(Tween.TRANS_SINE)
	t.tween_property(maisha, "global_position", global_position + hasta + Vector2(0, -6), dura).set_trans(Tween.TRANS_SINE)
	await t.finished
	# y baja a tierra, una casilla más allá de la balsa
	var tierra := global_position + hasta + Vector2(R.CASILLA * (1.3 if not en_el_este else -1.3), 2)
	var baja := create_tween()
	baja.tween_property(maisha, "global_position", tierra, 0.3)
	await baja.finished
	en_el_este = not en_el_este
	maisha.set("puede_actuar", true)
	cruzando = false


func _process(delta: float) -> void:
	_tiempo += delta
	if arreglada():
		_sprite.rotation = sin(_tiempo * 1.6) * 0.03
		_sprite.offset.y = sin(_tiempo * 2.0) * 0.8
