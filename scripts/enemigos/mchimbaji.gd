extends Node2D
## MCHIMBAJI, EL ESCARABAJO BARRENADOR DE ÁMBAR (Asterhaul, las Galerías): rueda hecho una bola por las VÍAS, de
## punta a punta, sin parar (obedece a los cambios de agujas y da la vuelta en los topes: asterhaul/via.gd).
##   - Rodando: 1 hoja a quien pille en la vía; el cetro y las semillas rebotan (¡clinc!). Una CARGA SÍSMICA de
##     frente lo manda rodando por donde venía.
##   - Si un cambio de agujas lo mete en un RAMAL MUERTO y se estampa contra el PARACHOQUES («parachoques»), se
##     queda PANZA ARRIBA unos segundos: ahí entra el cetro (1) y las semillas (2). 2 de vida.
##   - Una VAGONETA lanzada lo aplasta de una.
## Dibujo: arte/mundos/asterhaul/galerias/mchimbaji.png (herramientas/pintar_galerias.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/mchimbaji.png")
const VIA := preload("res://scripts/mundo/asterhaul/via.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 2
const RUEDA := 78.0
const PANZA := 4.5
const TOCA := 11.0

enum Fase { RUEDA, PANZA }

var vida := VIDA
var fase := Fase.RUEDA
## hacia dónde empieza a rodar
var dir := Vector2i.LEFT
var radio_carga := 4.0
var _meta := Vector2.ZERO
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _toco := 0.0
var _muriendo := false
var _filas: PackedStringArray
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("sismicos")
	add_to_group("mchimbajis")
	_filas = get_tree().current_scene.get_node("Region")._filas
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -9)
	add_child(_sprite)
	_meta = global_position


func casilla() -> Vector2i:
	return VIA.casilla(global_position)


## ¿Se puede entrar en esa casilla? (hay vía y nada la corta)
func _libre(c: Vector2i) -> bool:
	return VIA.es_via(_filas, c) and VIA.tope(get_tree(), c) == null


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_toco = maxf(0.0, _toco - delta)
	if fase == Fase.PANZA:
		_sprite.frame = 3 if _destello > 0.0 else 2
		_sprite.rotation = sin(_tiempo * (5.0 if _t < PANZA - 1.0 else 18.0)) * 0.08
		if _t >= PANZA:
			fase = Fase.RUEDA
			dir = -dir
			_meta = global_position
		return
	_sprite.rotation = 0.0
	_sprite.frame = int(_tiempo * 9.0) % 2
	_sprite.flip_h = dir.x > 0 or dir.y > 0
	global_position = global_position.move_toward(_meta, RUEDA * delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and _toco <= 0.0 and maisha.global_position.distance_to(global_position) < TOCA:
		_toco = 0.8
		maisha.call("recibir_danio", 1, global_position, "contacto")
	if global_position.distance_to(_meta) > 0.5:
		return
	# en cada casilla: por dónde sigue
	var aqui := casilla()
	var d := VIA.seguir(get_tree(), _filas, aqui, dir)
	if d != Vector2i.ZERO and _libre(aqui + d):
		dir = d
		_meta = VIA.centro(aqui + d)
		return
	# se acaba la vía (o algo la corta): contra un parachoques se estampa; si no, da la vuelta
	for p in get_tree().get_nodes_in_group("parachoques"):
		if VIA.casilla((p as Node2D).global_position) == aqui + dir:
			_estamparse()
			return
	dir = -dir
	if _libre(aqui + dir):
		_meta = VIA.centro(aqui + dir)


func _estamparse() -> void:
	fase = Fase.PANZA
	_t = 0.0
	Impacto.temblar(1.5, 0.12)
	Sonido.efecto("cangrejo_vuelca", -2.0, global_position)


# --- Carga y daño ---------------------------------------------------------------

## Una Carga de frente lo manda por donde venía
func recibir_carga(direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase == Fase.RUEDA:
		var d := Vector2i(signi(int(roundf(direccion.x))), 0) if absf(direccion.x) >= absf(direccion.y) else Vector2i(0, signi(int(roundf(direccion.y))))
		if _libre(casilla() + d):
			dir = d
			_meta = VIA.centro(casilla() + d)
		Sonido.efecto("clinc", -2.0, global_position, 0.2)
		_toco = 0.5
	return true


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase != Fase.PANZA:
		_rebotar()
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	if fase != Fase.PANZA:
		_rebotar()
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -8), Vector2.UP, Color("ffd878"))
	if vida <= 0:
		morir()


func _rebotar() -> void:
	Sonido.efecto("clinc", -2.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -10), Vector2.UP, Color("d8a858"))


## Una vagoneta lanzada
func aplastar() -> void:
	morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("mchimbaji", self)
	Sonido.efecto("roca_romper", -4.0, global_position)
	for g in ["enemigos", "golpeables", "daniables", "sismicos", "mchimbajis"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.15), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
