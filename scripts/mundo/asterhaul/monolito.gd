extends StaticBody2D
## UN MONOLITO-DIAPASÓN (Asterhaul, la Aguja Caída): una piedra de estrella hendida en horquilla. Dormido, calla.
## Cuando CANTA, suelta ondas que llegan hasta ALCANCE px, y con su `fuerza` (1 a 3):
##   - la RESONANCIA DE ÁMBAR de Maisha lo hace cantar con fuerza 3, DURA s;
##   - POR SIMPATÍA: la onda de otro monolito que canta con fuerza f (2 o 3) lo despierta con fuerza f − 1,
##     también DURA s. Así una nota pasa de monolito en monolito: 3 → 2 → 1, y ahí se acaba;
##   - una CARGA SÍSMICA le da un CAMPANAZO: fuerza 1 y solo DURA_CAMPANAZO s (está en «sismicos»). No se contagia.
## Lo que hace su onda lo decide quien la escucha, preguntando `Monolito.que_suena_en(árbol, punto)`: los PUENTES DE
## CRISTAL aguantan, los PEÑASCOS acuden, los Popo se tragan su chillido y Kipanga pierde el vuelo.
## Una PLUMA-CUCHILLA zumbando cerca («plumas_cuchilla», a menos de MUDO px) lo ENMUDECE: hay que romperla.
## Dibujo: arte/mundos/asterhaul/aguja/monolito.png, 0 dormido · 1 cantando · 2 enmudecido.

signal canta(fuerza: int)

const DIBUJO := preload("res://arte/mundos/asterhaul/aguja/monolito.png")
const ALCANCE := 112.0
const VELOCIDAD := 150.0               # a lo que corre el frente de la onda (px/s)
const DURA := 7.0
const DURA_CAMPANAZO := 3.5
const CADA := 0.7                      # cada cuánto sale una onda (lo que se ve)
const MUDO := 46.0

var fuerza := 0
var radio_carga := 6.0
var _t := 0.0                          # lo que lleva cantando
var _queda := 0.0
var _sprite: Sprite2D
var _ondas: Node2D


func _ready() -> void:
	add_to_group("monolitos")
	add_to_group("sismicos")
	_ondas = Node2D.new()
	_ondas.top_level = true
	_ondas.z_index = -1
	_ondas.draw.connect(_dibujar_ondas)
	add_child(_ondas)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 3
	_sprite.offset = Vector2(0, -24)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(14, 8)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)


func cantando() -> bool:
	return fuerza > 0


## ¿Tiene una pluma-cuchilla zumbando cerca?
func mudo() -> bool:
	for p in get_tree().get_nodes_in_group("plumas_cuchilla"):
		if (p as Node2D).global_position.distance_to(global_position) < MUDO:
			return true
	return false


## Hasta dónde ha llegado ya su onda
func radio() -> float:
	return minf(ALCANCE, _t * VELOCIDAD) if fuerza > 0 else 0.0


## ¿Le llega su onda a ese punto?
func alcanza(p: Vector2) -> bool:
	return fuerza > 0 and p.distance_to(global_position) <= radio()


## El monolito que está sonando en ese punto (el que canta con más fuerza), o null
static func que_suena_en(arbol: SceneTree, p: Vector2) -> Node2D:
	var mejor: Node2D = null
	for m in arbol.get_nodes_in_group("monolitos"):
		if m.alcanza(p) and (mejor == null or m.fuerza > mejor.fuerza):
			mejor = m
	return mejor


## Empieza a cantar con esa fuerza (true si ha cambiado algo). Con `campanazo`, dura poco (el golpe de la Carga).
func resonar(f: int, campanazo := false) -> bool:
	if f <= 0 or fuerza >= f:
		return false
	if mudo():
		Sonido.efecto("clinc", -6.0, global_position, 0.3)
		return false
	if fuerza == 0:
		_t = 0.0
	fuerza = f
	_queda = DURA_CAMPANAZO if campanazo else DURA
	_sprite.frame = 1
	Sonido.efecto("diapason_ambar", 2.0 - (3 - f) * 3.0, global_position, 0.02 * (3 - f))
	canta.emit(f)
	return true


func callar() -> void:
	fuerza = 0
	_queda = 0.0
	_sprite.position.x = 0.0


func recibir_carga(_direccion: Vector2) -> bool:
	resonar(1, true)
	return true


func _process(delta: float) -> void:
	var enmudecido := mudo()
	if fuerza == 0:
		_sprite.frame = 2 if enmudecido else 0
		_ondas.queue_redraw()
		return
	_t += delta
	_queda -= delta
	_sprite.position.x = roundf(sin(_t * 50.0) * 0.6)                 # vibra
	if _queda <= 0.0 or enmudecido:
		callar()
		return
	# por simpatía: su onda despierta, con un punto menos de fuerza, a los monolitos que alcanza
	if fuerza >= 2:
		for m in get_tree().get_nodes_in_group("monolitos"):
			if m != self and m.fuerza < fuerza - 1 and alcanza(m.global_position):
				m.resonar(fuerza - 1)
	_ondas.queue_redraw()


## Las ondas: anillos de ámbar (aplastados: van por el suelo) que salen cada CADA s y se apagan al llegar al alcance
func _dibujar_ondas() -> void:
	if fuerza == 0:
		return
	_ondas.draw_set_transform(global_position + Vector2(0, -3), 0.0, Vector2(1.0, 0.62))
	var vuelo := ALCANCE / VELOCIDAD
	var k := 0
	while k * CADA <= _t:
		var edad := _t - k * CADA
		if edad < vuelo:
			var f := edad / vuelo
			_ondas.draw_arc(Vector2.ZERO, ALCANCE * f, 0, TAU, 44, Color(1.0, 0.82 - 0.2 * f, 0.36 + 0.4 * f, (1.0 - f * 0.8) * (0.5 + 0.15 * fuerza)), 1.5 + 0.6 * fuerza * (1.0 - f))
		k += 1
	_ondas.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
