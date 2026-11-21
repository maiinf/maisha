extends Node2D
## UNA POLILLA DE PAPEL (el Jardín de los Faroles): una polilla hecha con una página doblada. Le encanta la luz:
## mientras haya un ESPEJO DE ÁNGULO encendido (ocaso/espejo_angulo.gd), vuela hasta él y se le posa encima. Lo tapa
## (`tapado`) y la luz se para ahí. Si no hay ninguno, o Maisha anda lejos (DESPIERTA px), revolotea por su sitio.
## No pica.
##   - Un golpe de cetro (o una semilla) la rompe; la RESONANCIA DE ÁMBAR (P) la deshace aunque esté lejos.
## Dibujo: arte/mundos/ocaso/jardin/polilla.png (0-1 vuela · 2 posada · 3 golpeada).

signal destruido

const DIBUJO := preload("res://arte/mundos/ocaso/jardin/polilla.png")
const VEL := 46.0
const DESPIERTA := 200.0                 # (hasta que Maisha no se acerca, revolotea por su sitio)

var _casa := Vector2.ZERO
var _espejo: Node2D = null
var _tiempo := 0.0
var _muriendo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("polillas")
	_casa = position
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -18)
	add_child(_sprite)
	_tiempo = randf() * 4.0


func posada() -> bool:
	return is_instance_valid(_espejo) and _espejo.tapado == self


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	if posada():
		_sprite.frame = 2
		_sprite.position.y = 0.0
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or maisha.global_position.distance_to(_casa) > DESPIERTA:
		_espejo = null
	elif not is_instance_valid(_espejo) or not _espejo.encendido or is_instance_valid(_espejo.tapado):
		_espejo = _buscar()
	var meta := _casa + Vector2(sin(_tiempo * 1.3) * 18.0, cos(_tiempo * 0.9) * 10.0)
	if _espejo:
		meta = _espejo.global_position + Vector2(0, -1)
	var p := global_position.move_toward(meta, VEL * delta)
	_sprite.flip_h = p.x < global_position.x
	global_position = p
	_sprite.frame = int(_tiempo * 10.0) % 2
	_sprite.position.y = roundf(sin(_tiempo * 6.0) * 2.0)
	if _espejo and global_position.distance_to(meta) < 1.0:
		_espejo.tapado = self
		Sonido.efecto("polilla_posa", -3.0, global_position, 0.1)
		get_tree().call_group("luz_jardin", "cambiar")


## El espejo encendido y libre más cercano (que no vaya ya otra polilla)
func _buscar() -> Node2D:
	var mejor: Node2D = null
	for e in get_tree().get_nodes_in_group("espejos"):
		if not e.get("encendido") or is_instance_valid(e.get("tapado")):
			continue
		var ocupado := false
		for o in get_tree().get_nodes_in_group("polillas"):
			if o != self and o.get("_espejo") == e:
				ocupado = true
		if not ocupado and (mejor == null or global_position.distance_to(e.global_position) < global_position.distance_to(mejor.global_position)):
			mejor = e
	return mejor


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(_cantidad: int, _desde: Vector2, _tipo: String) -> void:
	morir()


## (la Resonancia de Ámbar: combate/resonancia_ambar.gd)
func resonar(_f: int) -> void:
	morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	if posada():
		_espejo.tapado = null
		get_tree().call_group("luz_jardin", "cambiar")
	Bestiario.vencido("polilla_papel", self)
	Sonido.efecto("polilla_rompe", -2.0, global_position, 0.12)
	for g in ["enemigos", "golpeables", "daniables", "polillas"]:
		remove_from_group(g)
	_sprite.frame = 3
	Impacto.chispa(global_position + Vector2(0, -18), Vector2.UP, Color("fff6e4"))
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "rotation", 1.2, 0.5)
	t.tween_property(_sprite, "position:y", 10.0, 0.5)
	t.tween_property(self, "modulate:a", 0.0, 0.5)
	t.chain().tween_callback(queue_free)
