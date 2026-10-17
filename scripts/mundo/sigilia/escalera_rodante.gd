extends Node2D
## UNA ESCALERA RODANTE (Las Estanterías Colgantes): una escalera de biblioteca tumbada sobre el hueco entre dos
## pisos, que corre por los raíles del borde. Es lo único por donde se cruza el hueco, y no se está quieta:
##   TENDIDA (se cruza) → AVISO (tiembla y chirría) → SE VA (rueda hacia un lado) → RECOGIDA (el hueco, sin paso) →
##   VUELVE (rueda a su sitio) → TENDIDA...
## Mientras no está tendida, una pared invisible tapa el carril. Si se va con Maisha encima, Maisha CAE al piso de
## abajo: pierde una hoja y vuelve al pie de la escalera, en el piso de abajo.
## Se coloca en la casilla de abajo a la izquierda del carril («ǝ»), con «casillas» de largo hacia el norte.

signal caida

enum Fase { TENDIDA, AVISO, SE_VA, RECOGIDA, VUELVE }
const DIBUJO := preload("res://arte/mundos/sigilia/estanterias/escalera.png")
const DURA := {Fase.TENDIDA: 4.0, Fase.AVISO: 1.1, Fase.SE_VA: 0.7, Fase.RECOGIDA: 2.6, Fase.VUELVE: 0.7}
const APARTA := 48.0                   # píxeles que rueda hacia un lado

@export var casillas := 4              # lo largo del hueco
@export var desfase := 0.0             # segundos de ventaja (para que no vayan todas a la vez)
@export var lado := 1                  # hacia dónde rueda al irse: 1 este, -1 oeste

var fase := Fase.TENDIDA
var _t := 0.0
var _sprite: Sprite2D
var _pared: StaticBody2D
var _forma: CollisionShape2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("escaleras_rodantes")
	z_index = -6                       # (por debajo de Maisha, por encima del suelo)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.centered = false
	_sprite.offset = Vector2(-2, -casillas * 16 - 6)
	add_child(_sprite)
	_pared = StaticBody2D.new()
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(32, casillas * 16)
	_forma.shape = caja
	_forma.position = Vector2(16, -casillas * 8.0)
	_pared.add_child(_forma)
	add_child(_pared)
	_t = fmod(desfase, 9.1)
	# avanza el desfase
	while _t > DURA[fase]:
		_t -= DURA[fase]
		fase = ((fase + 1) % 5) as Fase
	_poner_pared()


func esta_tendida() -> bool:
	return fase == Fase.TENDIDA or fase == Fase.AVISO


func _poner_pared() -> void:
	_forma.set_deferred("disabled", esta_tendida())


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	if _t >= DURA[fase]:
		_t = 0.0
		var antes := fase
		fase = ((fase + 1) % 5) as Fase
		if antes == Fase.AVISO:
			_comprobar_caida()
			Sonido.efecto("escala_tramo", -4.0, global_position + Vector2(16, -casillas * 8))
		_poner_pared()
	# dónde está el dibujo: en su sitio, temblando, rodando o apartado
	var x := 0.0
	match fase:
		Fase.AVISO:
			x = sin(_tiempo * 40.0) * 1.2
		Fase.SE_VA:
			x = lado * APARTA * clampf(_t / DURA[fase], 0.0, 1.0)
		Fase.RECOGIDA:
			x = lado * APARTA
		Fase.VUELVE:
			x = lado * APARTA * (1.0 - clampf(_t / DURA[fase], 0.0, 1.0))
	_sprite.position.x = round(x)


## ¿Está Maisha encima, ahora que se va? Entonces cae
func _comprobar_caida() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or maisha.get("esta_caida"):
		return
	var p := maisha.global_position - global_position
	if p.x > -2 and p.x < 34 and p.y < 2 and p.y > -casillas * 16 - 2:
		caida.emit()
		cae(maisha)


## Maisha cae al piso de abajo: se encoge como si bajara, pierde una hoja y aparece al pie de la escalera
func cae(maisha: Node2D) -> void:
	maisha.set("puede_actuar", false)
	Sonido.efecto("maisha_cae", -2.0, maisha.global_position)
	var t := maisha.create_tween()
	t.tween_property(maisha, "scale", Vector2(0.2, 0.2), 0.35)
	t.parallel().tween_property(maisha, "modulate:a", 0.0, 0.35)
	await t.finished
	if not is_inside_tree():
		return
	maisha.global_position = global_position + Vector2(16, 14)
	maisha.scale = Vector2.ONE
	maisha.modulate.a = 1.0
	maisha.set("puede_actuar", true)
	maisha.call("perder_hoja")
