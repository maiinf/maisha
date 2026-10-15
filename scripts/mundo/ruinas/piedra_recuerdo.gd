extends StaticBody2D
## PIEDRA DEL RECUERDO: una de las nueve que rodean al Primer Árbol, como las de los ecos pero apagadas.
## Se despierta MANTENIENDO ACCIÓN a su lado (1,6 s): Maisha recuerda lo que dijo ese eco y la piedra se enciende.
## Mantener Acción es estar quieta, así que mientras tanto sube la escarcha (y el miedo ataca).
## Despierta da calor (como un brasero: está en el grupo «braseros») y avisa al miedo (ruinas/miedo.gd).

signal despertada(piedra: Node)

const DIBUJO := preload("res://arte/mundos/raiz/sendero/eco.png")
const CARGA := 1.6
const RADIO := 30.0
const RADIO_CALOR := 40.0

var indice := 0
var despierta := false
var activa := false              # solo se pueden despertar durante la pelea
var _carga := 0.0
var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("piedras_recuerdo")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-13, -39)
	_sprite.self_modulate = Color(0.55, 0.56, 0.64)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func despertar() -> void:
	if despierta:
		return
	despierta = true
	_carga = 0.0
	_sprite.frame = 1
	add_to_group("braseros")
	Sonido.efecto("eco_voz", 0.0, global_position)
	Impacto.onda(global_position + Vector2(0, -20))
	despertada.emit(self)                 # (el miedo le dice qué número de recuerdo es)
	# la novena, la del Silencio, plateada
	_sprite.self_modulate = Color.WHITE if indice != 8 else Color(0.86, 0.92, 1.12)


## Como un brasero: despierta, calienta alrededor
func calienta(punto: Vector2) -> bool:
	return despierta and punto.distance_to(global_position) <= RADIO_CALOR


func _process(delta: float) -> void:
	_tiempo += delta
	if despierta or not activa:
		if _carga > 0.0:
			_carga = 0.0
			queue_redraw()
		if despierta:
			queue_redraw()
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var cerca: bool = maisha != null and maisha.global_position.distance_to(global_position) < RADIO and maisha.get("puede_actuar")
	if cerca and Input.is_action_pressed("accion"):
		_carga += delta
		if _carga >= CARGA:
			despertar()
	else:
		_carga = maxf(0.0, _carga - delta * 2.0)
	queue_redraw()


func _draw() -> void:
	if _carga > 0.0:
		# el aro que se va cerrando mientras Maisha recuerda
		var c := Vector2(0, -20)
		draw_arc(c, 16.0, -PI / 2.0, -PI / 2.0 + TAU * (_carga / CARGA), 32, Color(0.75, 1.0, 0.95, 0.9), 2.0)
	if despierta:
		var pulso := 0.5 + 0.5 * sin(_tiempo * 2.2 + indice)
		var col := Color(0.43, 0.69, 0.69) if indice != 8 else Color(0.66, 0.72, 0.85)
		draw_circle(Vector2(0, -20), 16.0 + pulso * 3.0, Color(col, 0.12))
		draw_circle(Vector2(0, -20), 7.0, Color(col.lightened(0.5), 0.2))
